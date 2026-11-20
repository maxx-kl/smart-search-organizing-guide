# The minimal OpenSearch database

[Start here](README.md) · [Previous: glossary](11-glossary.md)

**Proposal:** the first OpenSearch database covers [Milestones B and C](08-delivery-plan.md) and nothing more: a complete index of every record, rebuildable at any time, with word, substring and code search only. Asset aliases, vectors and cited answers (Milestones D–E) get no database objects yet, but the layout lets each one arrive later without a redesign.

**Basis:** this guide's chapters [3](03-resources-and-metadata.md), [4](04-assets-aliases-and-languages.md), [6](06-search-architecture.md) and [7](07-evaluation-and-acceptance.md). **Local basis:** the current pipeline description (`services/es-migration/CURRENT-PIPELINE.md`, 9 October 2026), the search requirements and defects (`ai-handoff/08-SEARCH-EVOLUTION.md`, R1–R13 and F1–F16), the data model (`ai-handoff/04-DATA-MODEL.md`) and the shared record types (`infl-general/records-types.ts`). Written 19 November 2026 and checked the same day by an [offline test](#offline-test-results) against a full RTDB backup, which confirmed the design and led to the corrections marked **(test)** below. The change-capture trigger, reconciliation and the older-client adapter are still untested.

## In one paragraph

One OpenSearch 3.x node holds one index template and one index per facility, each behind an alias. About 70 fields, counting the nested event and checklist fields, are declared up front with `dynamic: strict` (the current KB index has 227, mostly created automatically). Two analyzers and one normalizer give three ways to match text: whole words, trigram substrings and normalized equipment codes. External version numbers and tombstone documents keep writes in order. The node has no plugins and no replicas and is reachable only from localhost. The indexing pipeline's own state (change counters, pending queue, coverage counts) lives in RTDB next to the existing queues.

## 1. Indices and aliases

| Object | Setting | Why |
|---|---|---|
| Template | `records-v*`: 1 shard, 0 replicas, explicit mapping | One definition for every facility. With 0 replicas a single node shows green; the current cluster is permanently yellow |
| Index | `records-v1-<facility key, lowercased>` | Versioned name: an analyzer change means building `v2` and swapping the alias, keeping `v1` for rollback. The indexer writes to the names in the facility config (two during a rebuild) |
| Read alias | `records-<fac>` with filter `deleted: false` | The query service never sees tombstones, even if a query forgets the filter |
| Cluster | `action.auto_create_index: false` | A bad facility key can't create an index (old defects 3 and 6). The indexer creates indices from the facility list (F15) |
| Document id | RTDB record key | Re-indexing a record overwrites it; opening a result still reads RTDB |

One index per facility rather than a shared index: it matches the current layout, lets a single facility be rebuilt or checked on its own, and a wrong facility key fails with "index not found" instead of leaking another facility's records. Access checks stay in the query service ([chapter 6 §5](06-search-architecture.md)): it chooses the alias for a facility the user is authorized for and never uses the facility key the client sent.

## 2. Analysis: three ways to match the same text

```json
"analysis": {
  "tokenizer":  { "if_tri": { "type": "ngram", "min_gram": 3, "max_gram": 3, "token_chars": ["letter", "digit"] } },
  "filter":     { "if_fold": { "type": "asciifolding", "preserve_original": true } },
  "analyzer": {
    "if_words": { "type": "custom", "char_filter": ["if_word_chars"], "tokenizer": "standard", "filter": ["lowercase", "if_fold"] },
    "if_tri":   { "type": "custom", "tokenizer": "if_tri",   "filter": ["lowercase", "if_fold"] }
  },
  "char_filter": {
    "if_word_chars": { "type": "mapping", "mappings": ["_=>\\u0020"] },
    "if_code_chars": { "type": "mapping",
      "mappings": ["А=>A", "а=>a", "В=>B", "Е=>E", "К=>K", "М=>M", "Н=>H", "О=>O", "Р=>P", "С=>C", "Т=>T", "Х=>X", "…", "-=>", "_=>", ".=>", "/=>", "\\u0020=>"] } },
  "normalizer": { "if_code": { "type": "custom", "char_filter": ["if_code_chars"], "filter": ["uppercase"] } }
}
```

The lookalike list is abridged: it maps every Cyrillic letter that looks like a Latin one, in both cases, and removes separators.

Each text field is `text` (analyzed with `if_words`) plus a `.sub` subfield (analyzed with `if_tri`). Equipment codes go in a `keyword` field that uses the `if_code` normalizer.

| Need | Field and query | Fixes |
|---|---|---|
| Whole words, phrases, typos | Main field: `match` requiring all words, and all pieces of a word the analyzer splits (`operator: and`), with `fuzziness` set per word length; `match_phrase` for phrases and for words with inner separators | Words over 15 characters (Q08), phrases (Q10), typos (Q05). Typo tolerance no longer switches off with transliteration (F2) |
| Substrings and word endings (R1) | `.sub`: one `match_phrase` per query word of 3+ characters, which matches it as an exact substring of any length | Q08. Words of 1–2 characters match whole words only (Q09, F8) |
| Codes (R7, Q01) | `codes`: `term` query, plus a weaker `prefix` query for codes typed in part; the normalizer applies to both the stored value and the query | `MOT 123321` = `МОТ123321` = `mot-123321`, while `PUMP123321` stays separate |

Transliteration stays in the query service, using one shared copy of the transliteration code. That needs no plugin and keeps the current behavior. Highlights use `encoder: html`, so source text is escaped (F14). Every search gets a `timeout`, so the screen can't wait forever (Q23).

**Why phrases fail today and trigrams fix it.** The current analyzer uses the ngram *token filter*, which puts all 1–15-character pieces of a word at the same position. That makes phrase queries impossible, stops words over 15 characters from matching, and the one-letter pieces swell the KB index to 679 MB. The ngram *tokenizer* gives each three-letter piece its own position, so a `match_phrase` over those pieces is an exact substring search, with no length limit and far fewer stored terms.

**(test) Underscores split words.** The standard tokenizer follows the Unicode word rules, which treat `_` as part of a word, so a tag like `K3PR_12_3456_1` was stored as one token. A query for `12 3456` then found nothing: `3456` still matched through `.sub`, but `12` is too short for trigrams and wasn't a whole word anywhere. Today's search finds such tags by accident, because its 1–15-character pieces include `12`. Underscore-joined tags appear in 4.3% of KB records (2.7% across facilities), mostly equipment and valve tags. The `if_word_chars` filter turns `_` into a space before tokenizing, at index and query time alike.

Splitting creates a second trap: a single query word that becomes several tokens (`12_3456_1` → `12 3456 1`) is OR-ed by default and matched 17,298 KB records containing `1` or `12`. Each query word therefore requires all its pieces (`operator: and`), plus a phrase bonus when they appear side by side.

**Codes are candidates, not identities.** `codes` is the conservative normalized form from the first two rows of the table in [chapter 4](04-assets-aliases-and-languages.md); it doesn't claim two mentions are the same asset. The builder extracts code-like strings with a short, versioned rule (a short prefix that starts with letters, an optional separator, then digits; details below) and leaves anything doubtful as ordinary text: `двигун 123 321` stays text, as chapter 4 recommends. Because the folding rule lives in the index's normalizer, it is versioned with the index.

**(test) The query side must be more liberal than the document side.** A query that looks like a code in any case and with any separator, a space included (`mot 123321`), adds a `codes` term as one more candidate next to the text match. With only the strict document rule, codes typed differently were found *less* often than today (Hit@20 0.34 against 0.48); with the liberal query rule, Hit@5 rose to 0.76. A wrong guess costs nothing, because the term only adds candidates.

**(test) Tags with letters and digits in the prefix, and tags typed in part.** A rule that expects letters only before the digits stores `K3PR_12_3456_1` as `PR_12_3456_1` and loses `K3`, and a `term` query matches whole codes only, so `K3PR12-3456` (the tag typed without its underscore and its last part) found nothing. The rule now accepts a prefix of 2–6 letters or digits that starts with a letter and holds at least two letters, and **also keeps the fragment** that starts after a digit (`PR_12_3456_1`, or `PT100` in `2PT100`): dropping the fragments cost 3.6 points on codes typed differently, because people search for them that way. Queries add a `prefix` query on `codes` next to the exact `term`, at a lower boost (20 against 50) and only from 5 normalized characters with letters and digits, so `K3` alone doesn't match a whole family of tags. A partial tag that does match a family (`K3PR12`) returns the family, most recently active first; that is the right answer, not noise.

## 3. The document: one per top-level record

A field copied from RTDB keeps its RTDB name, so the name itself records where it came from. Fields computed by the builder get new names. This keeps source assertions apart from derived interpretation ([chapter 3](03-resources-and-metadata.md)).

| Group (chapter 3) | Fields | Type |
|---|---|---|
| Identity | `facilityKey`, `recordKey`, `recordType`, `parentRecordKey` (from `parentRecordRef.key`), `threadKey` (the parent's key if there is one, else the record's own) | keyword |
| Location | `eqL1Key`, `eqL2Key`, `eqL3Key` | keyword |
| Text | `description`, `done`, `todo`, `rootCause`, `rcaText` (RCA questions **and answers**) | text + `.sub` |
| Codes | `codes[]`: code-like strings found in all the text | keyword + `if_code` |
| Events (nested `subRecords`) | `key`, `recordType` (now including `link`), `stateChange`, `commentText`, `done`, `linkText`, `rcaText`, `linkType`, `link`, `creatorKey/Name/Group`, `dateCreated` | keyword / text + `.sub` / date |
| Checklist items (nested `checklistItems`) **(test)** | `key`, `text`, `checked`, `order`, `creatorKey/Name`, `checkedByKey/Name`, `responsibleKey/Name`, `dateCreated`, `checkedDate`, `lastUpdated`, `due` | keyword / text + `.sub` / boolean / double / date |
| People | `creatorKey`, `creatorName`, `creatorGroup`, keyword type at **both** record and event level (old defect 5) | keyword |
| Time | `dateCreated`; `lastUpdated` (left empty when missing, never invented); `lastActivityAt` (latest of creation, event and checklist dates) | date, `format: epoch_millis\|\|strict_date_optional_time` **(test)**: with `epoch_millis` alone, ISO dates in queries (a decay origin, a range filter) are rejected |
| Flags | `tagType`, `tagNumber`, `priority`, `pdcaStatus`, `projectKey`, `labels[]`, `nearMiss` (means the broader H&S category), `safety`, `quality` | keyword / boolean |
| Coverage | `attachmentCount`; `coverage[]`, e.g. `checklist-not-found` (the record says it has a checklist, but no items were found), `attachments-not-read`, `events-truncated` | integer / keyword |
| Processing | `builderVersion`, `inputHash`, `indexedAt`, `deleted` | keyword / date / boolean |

Left out on purpose: Telegram media details (sender data), likes, actions, Trello cards, questionnaires, `creatorEmail`, process fields, and anything stored as a map keyed by user or push id. With `strict`, a bug in the document builder shows up as a visible indexing error instead of the mapping quietly growing.

What this shape gives with nothing extra:

- **Matching entry:** `inner_hits` on the nested queries returns the event or checklist item that matched (its key, field, author and date; for an item also its state, responsible person and due date). That covers "Show matching entry" from [chapter 2](02-search-jobs-and-experience.md) and the link back to the source, without a separate index of passages.
- **Event-level filters:** nested events keep author, date and text together, so "Mira's checks in March" can't combine three different events (Q13).
- **No double counting:** `collapse` on `threadKey` merges a work record that appears both in a shift and under its parent problem (Q16). The adapter for older clients doesn't collapse.
- **Ranking:** decay from `lastActivityAt` instead of creation lets older but recently active problems rank higher (F7).
- **Missing text found:** `rcaText`, `linkText` and `rootCause` become searchable (Q12, F16), and RCA text no longer overwrites `done`.
- **Checklist text found (test):** items live outside the record (`checkListItems/<recordKey>/<itemId>`), and today's search never sees them. They get their own nested field rather than becoming events, because an item has state (checked or open, responsible person, due date) and a later filter such as "open items assigned to Mira" must stay inside one item, as Q13 requires for events. Ticking an item off counts as activity on the record, which the app already tracks apart from `lastUpdated` (`lastUpdatedByChecklist`).
- **Totals for intelliflow-sp:** `track_total_hits` returns the plain-number total the old client expects.

**(test) The adapter for older clients must translate, not forward.** Today's query, run unchanged on OpenSearch 3, fails with `too_many_nested_clauses`: its fuzzy multi-field match over the 1–15-character pieces expands past 1,024 clauses. ES 5.4 counted that limit per boolean level; Lucene 10 counts the whole query. The adapter maps the old request's fields (query text, filters, paging) onto the new query instead of passing the old query body through.

## 4. Write ordering

These parts keep the index correct, not just fast. They implement the protocol sketched in [chapter 6 §2](06-search-architecture.md).

```text
RTDB  searchIndex/records/<fac>/<rk> = { gen: 17, pending: true }   (.indexOn: pending)
      searchIndex/failed/<fac>/<rk>  = { gen, error, attempts, at }
      searchIndex/status/<fac>       = { eligible, indexed, lastReconcile, builderVersion, maxLagMs }
```

1. **Catch every change:** a small Cloud Function fires on any write to `facilityData/{fac}/records/{rk}` and **(test)** to `facilityData/{fac}/checkListItems/{rk}/{itemId}`, deletes included. In one transaction it increments the *record's* `gen` (its change counter) and sets `pending = true`. This catches the changes `lastUpdated` misses: priority, PDCA, project, moves, deletes and checklist activity.
2. **Index:** the worker reads `gen` **first**, then the record and its checklist items. It builds the document and writes it with `version = gen, version_type = external`. If the record no longer exists, it writes a tombstone (`deleted: true`) at that version instead.
3. **Reject stale writes:** a 409 conflict means a newer version is already in the index, so the worker counts it as success. OpenSearch itself refuses the stale overwrite (Q27).
4. **Finish:** another transaction sets `pending = false` only if `gen` hasn't changed in the meantime (Q28).
5. **Backfill:** each record is written with its current `gen`, or 0 if it has none. Start the trigger before the backfill. Records without `lastUpdated` are included (Q14).
6. **Reconcile:** once a day, compare record keys in RTDB (`shallow=true`) with the ids in the index and mark missing or leftover ones as pending. After a builder change, also compare content hashes (`inputHash`). The results go to `status/<fac>`, which the UI can use to warn about incomplete coverage.

**(test) Checklists depend on the RTDB cutover.** Production checklists are still in Firestore (`facilities/<fac>/checkLists/<recordKey>/items`); the move to `checkListItems` described in the workspace README hasn't run, and the 19 November RTDB backup has no items. Until it runs, an RTDB trigger can't see checklist changes. Index checklists only after the cutover, or add a temporary Firestore trigger that bumps the same `gen`. The offline test read the items from the 20 November Firestore export instead.

**The version number is the fencing token.** OpenSearch refuses any write with an older version, so overlapping workers can't corrupt the index, and the minimal version needs no worker locks to stay correct. Two traps:

- `gen` must never be deleted or reset. If the counter restarted at 1, OpenSearch would reject every later update as older than what it already holds.
- A real `DELETE` remembers its version for only 60 seconds (`index.gc_deletes`). After that, a late retry can bring a deleted record back (Q29). A tombstone keeps its version forever, and the alias filter hides it from searches.

## 5. Server and operations

- **Where:** OpenSearch 3.x (it ships its own Java) on a separate 4 GiB droplet. About 1.5 GB of heap; the rest goes to the file cache and the Node workers. This is a starting point, not a measured capacity plan.
- **Plugins:** none for the minimal version. Add k-NN and neural-search when Milestone D starts. Fewer plugins make upgrades simpler.
- **Network:**
  - `network.host: 127.0.0.1` with no public port; the DigitalOcean firewall allows SSH only.
  - The indexer and the query worker run on the same droplet. The Cloud Function writes only to RTDB, so nothing outside the droplet needs OpenSearch.
  - Turning the security plugin off is acceptable *only* under these conditions.
- **Backups:** set `path.repo` and take a file snapshot before every mapping change or upgrade. If the server is lost, rebuild the index from RTDB; it holds nothing RTDB doesn't.
- **Bulk loads:** `refresh_interval: -1` during the backfill, then back to `1s`. No OpenSearch Dashboards, to save memory.
- **Disk watermarks (test):** the default watermarks are percentages (85/90/95%). On a small, nearly full disk they block index creation and writes while gigabytes are still free. Set absolute values (`cluster.routing.allocation.disk.watermark.low/high/flood_stage`, e.g. a few GB each) and alert well before the flood stage.
- **Before testing the trigger:** `intelliflow-functions/firebase.json` has no `emulators` section. Until it does, testing the trigger locally writes to production.

## 6. What's left out, and how each part arrives later

| Later addition | Change to the database | Cost |
|---|---|---|
| Searching equipment names as text | New field, plus re-indexing a node's records when it is renamed (`equipmentRecords/<eq>` lists them) | Re-run the indexer |
| More filters (workgroups) | New field via `PUT _mapping` | Re-run the indexer |
| Checklist filters (open items, responsible person, due date) | None: the fields are already in `checklistItems` | Query service only |
| Ukrainian/Russian word stems | New analyzer → `records-v2-*`, filled with `_reindex` from v1 (stored `_source` makes that possible), then swap the alias | No RTDB reads |
| Cross-language search (Q06) | **(test)** Records carry no stored translations (none of 458,352 in the backup), so this needs its own source: translation at indexing time into a separate, labeled field, or multilingual vectors in Milestone D | Find where the app's translations live, if they are stored at all |
| Alias register (Milestone D) | Small `aliases-<fac>` index, applied at query time | Record indices untouched |
| Vectors and hybrid retrieval (Milestone D) | `index.knn` can only be set at creation → new v2 index plus plugins | Alias swap |

## 7. Acceptance

Against the [starter scenarios](07-evaluation-and-acceptance.md):

- **Must pass:** Q01, Q05, Q07–Q16, Q23–Q24 and Q27–Q29, plus parity with current search (R1–R13).
- **Q15 partly:** record moves pass; equipment renames only once names are indexed.
- **Later milestones:** Q02–Q04, Q06, Q17–Q22, Q25–Q26 and Q30.

## Offline test results

Run on 19 November 2026 on a laptop with OpenSearch 3.10 (no plugins, 2 GB heap). **New:** this chapter's mapping, built from the 10 October 2026 RTDB backup. **Old:** the 9 October ES 5.4 export with its own analyzer, queried by a line-by-line port of today's query builder and transliteration. The scripts and full results stay in the git-ignored `services/es-migration/spike/`, because they hold production data; only aggregates appear here.

| | Old | New |
|---|---|---|
| Records indexed | 441,547 | 458,352 (all of RTDB, incl. the 15,107 without `lastUpdated`) |
| Disk, all facilities (force-merged) | 799 MB | 444 MB (KB: 455 → 246 MB) |
| Build | — | 49 s reading the backup + 79 s building and loading |
| Query time p50 / p95 / max | 27 / 152 / 1,123 ms | 35 / 71 / 149 ms |

**Findability.** An automatic known-item test: from sampled text in seven facilities, the record's two rarest words became a query (12,899 queries), varied as below. The record had to be in the top 5. Overall **0.465 → 0.652**.

| Variant or text location | Old Hit@5 | New Hit@5 |
|---|---|---|
| Exact words / word endings cut / infix | 0.52 / 0.39 / 0.51 | 0.68 / 0.60 / 0.69 |
| One typo / Cyrillic typed in Latin | 0.54 / 0.44 | 0.64 / 0.64 |
| Word over 15 letters (Q08) | 0.17 | 0.39 |
| Code typed differently (Q01) | 0.33 | 0.76 |
| Link text / `rootCause` / RCA (Q12) | 0.06 / 0.17 / 0.80 | 0.75 / 0.77 / 0.92 |
| Records without `lastUpdated` (Q14) | 0.11 | 0.58 |

Every facility improved; AZ-BB only slightly (0.54 → 0.56), not yet explained.

**Scenario checks.**
- **Q09 short terms:** a two-letter query in KB matches 88 records instead of 49,431.
- **Q16 projections:** without `collapse`, a work record and its copy under the parent both filled the top 20 in 81 of 141 test queries (old and new alike); with `collapse` on `threadKey`, in none.
- **Q27, Q29 write ordering** (synthetic documents): a late write at an older version is refused; a tombstone stays hidden after `gc_deletes`; a real `DELETE` lets the late retry bring the record back, as §4 warns.
- **Profibus:** both engines find the reviewed fault cards (92 → 100 of 101), but only 4–5 reach the top 20. That needs ranking and structured filters, not analysis.

**Follow-up runs (20–21 November).** Trying queries in a local search tester turned up three gaps, fixed and re-measured. Earlier test buckets asked the same questions in every run; new buckets were added for checklists and tags:
- **Run 3, underscores split words** (§2): a two-part tag query that found nothing now finds the same records as today's search. Overall Hit@5 0.652 → 0.654, codes typed differently 0.755 → 0.781, and no metric got worse. Query time p50 and p95 unchanged; the slowest query went from 149 to 235 ms.
- **Run 4, checklist items** (§3): 92,362 items from the 20 November Firestore export, attached to 32,721 records; 506 checklists belong to records newer than the 10 October RTDB snapshot. Disk 444 → 459 MB (KB 246 → 259 MB), no indexing errors. Checklist text Hit@5: today 0.44 → new 0.71 (today's search only finds items whose words repeat the record's own text). Overall 0.654 → 0.661; query time p50 / p95 35 / 71 → 41 / 82 ms, from the extra nested clause.
- **Runs 5–6, tags with mixed prefixes and tags typed in part** (§2): a new test of up to 100 multi-part tags per facility. Typed joined (`k3pr1234561`): today 0.38 → new 0.81; typed without the last part: today 0.13 → new 0.42. Run 5 dropped code fragments and codes typed differently fell 0.78 → 0.74; keeping the fragments (run 6) brought them back to 0.77. Nothing else ended worse than in run 4; overall Hit@5 0.664 with the new buckets, 0.661 without.

**Limits.**
- Queries come from the records themselves, so this measures whether a record *can* be found, not relevance for real questions. The judged query set from [chapter 7](07-evaluation-and-acceptance.md) is still needed.
- Ranking changed too (decay from `lastActivityAt` over 180 days instead of from `dateCreated` over 14 days), so the gain isn't split between analysis and ranking.
- Latency is from a laptop, one query at a time, not a loaded 4 GiB droplet.
- Not tested: the trigger and acknowledgement (Q28), reconciliation, the intelliflow-sp adapter, and authorization (Q24).
