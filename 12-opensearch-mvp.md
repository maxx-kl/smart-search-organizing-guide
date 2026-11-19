# The minimal OpenSearch database

[Start here](README.md) · [Previous: glossary](11-glossary.md)

**Proposal:** the first OpenSearch database covers [Milestones B and C](08-delivery-plan.md) and nothing more: a complete index of every record, rebuildable at any time, with word, substring and code search only. Asset aliases, vectors and cited answers (Milestones D–E) get no database objects yet, but the layout lets each one arrive later without a redesign.

**Basis:** this guide's chapters [3](03-resources-and-metadata.md), [4](04-assets-aliases-and-languages.md), [6](06-search-architecture.md) and [7](07-evaluation-and-acceptance.md). **Local basis:** the current pipeline description (`services/es-migration/CURRENT-PIPELINE.md`, 9 October 2026), the search requirements and defects (`ai-handoff/08-SEARCH-EVOLUTION.md`, R1–R13 and F1–F16), the data model (`ai-handoff/04-DATA-MODEL.md`) and the shared record types (`infl-general/records-types.ts`). Written 19 November 2026. Nothing here has been built or measured; size and quality claims need the [offline test](#first-step-an-offline-test).

## In one paragraph

One OpenSearch 3.x node holds one index template and one index per facility, each behind an alias. About 50 fields are declared up front with `dynamic: strict` (the current KB index has 227, mostly created automatically). Two analyzers and one normalizer give three ways to match text: whole words, trigram substrings and normalized equipment codes. External version numbers and tombstone documents keep writes in order. The node has no plugins and no replicas and is reachable only from localhost. The indexing pipeline's own state (change counters, pending queue, coverage counts) lives in RTDB next to the existing queues.

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
    "if_words": { "type": "custom", "tokenizer": "standard", "filter": ["lowercase", "if_fold"] },
    "if_tri":   { "type": "custom", "tokenizer": "if_tri",   "filter": ["lowercase", "if_fold"] }
  },
  "char_filter": { "if_code_chars": { "type": "mapping",
    "mappings": ["А=>A", "а=>a", "В=>B", "Е=>E", "К=>K", "М=>M", "Н=>H", "О=>O", "Р=>P", "С=>C", "Т=>T", "Х=>X", "…", "-=>", "_=>", ".=>", "/=>", "\\u0020=>"] } },
  "normalizer": { "if_code": { "type": "custom", "char_filter": ["if_code_chars"], "filter": ["uppercase"] } }
}
```

The lookalike list is abridged: it maps every Cyrillic letter that looks like a Latin one, in both cases, and removes separators.

Each text field is `text` (analyzed with `if_words`) plus a `.sub` subfield (analyzed with `if_tri`). Equipment codes go in a `keyword` field that uses the `if_code` normalizer.

| Need | Field and query | Fixes |
|---|---|---|
| Whole words, phrases, typos | Main field: `match` requiring all words, with `fuzziness` set per word length; `match_phrase` for phrases | Words over 15 characters (Q08), phrases (Q10), typos (Q05). Typo tolerance no longer switches off with transliteration (F2) |
| Substrings and word endings (R1) | `.sub`: one `match_phrase` per query word of 3+ characters, which matches it as an exact substring of any length | Q08. Words of 1–2 characters match whole words only (Q09, F8) |
| Codes (R7, Q01) | `codes`: `term` query; the normalizer applies to both the stored value and the query | `MOT 123321` = `МОТ123321` = `mot-123321`, while `PUMP123321` stays separate |

Transliteration stays in the query service, using one shared copy of the transliteration code. That needs no plugin and keeps the current behavior. Highlights use `encoder: html`, so source text is escaped (F14). Every search gets a `timeout`, so the screen can't wait forever (Q23).

**Why phrases fail today and trigrams fix it.** The current analyzer uses the ngram *token filter*, which puts all 1–15-character pieces of a word at the same position. That makes phrase queries impossible, stops words over 15 characters from matching, and the one-letter pieces swell the KB index to 679 MB. The ngram *tokenizer* gives each three-letter piece its own position, so a `match_phrase` over those pieces is an exact substring search, with no length limit and far fewer stored terms.

**Codes are candidates, not identities.** `codes` is the conservative normalized form from the first two rows of the table in [chapter 4](04-assets-aliases-and-languages.md); it doesn't claim two mentions are the same asset. The builder extracts code-like strings with a short, versioned rule (a few letters, an optional separator, then digits) and leaves anything doubtful as ordinary text: `двигун 123 321` stays text, as chapter 4 recommends. Because the folding rule lives in the index's normalizer, it is versioned with the index.

## 3. The document: one per top-level record

A field copied from RTDB keeps its RTDB name, so the name itself records where it came from. Fields computed by the builder get new names. This keeps source assertions apart from derived interpretation ([chapter 3](03-resources-and-metadata.md)).

| Group (chapter 3) | Fields | Type |
|---|---|---|
| Identity | `facilityKey`, `recordKey`, `recordType`, `parentRecordKey` (from `parentRecordRef.key`), `threadKey` (the parent's key if there is one, else the record's own) | keyword |
| Location | `eqL1Key`, `eqL2Key`, `eqL3Key` | keyword |
| Text | `description`, `done`, `todo`, `rootCause`, `rcaText` (RCA questions **and answers**) | text + `.sub` |
| Codes | `codes[]`: code-like strings found in all the text | keyword + `if_code` |
| Events (nested `subRecords`) | `key`, `recordType` (now including `link`), `stateChange`, `commentText`, `done`, `linkText`, `rcaText`, `linkType`, `link`, `creatorKey/Name/Group`, `dateCreated` | keyword / text + `.sub` / date |
| People | `creatorKey`, `creatorName`, `creatorGroup`, keyword type at **both** record and event level (old defect 5) | keyword |
| Time | `dateCreated`; `lastUpdated` (left empty when missing, never invented); `lastActivityAt` (latest of creation and event dates) | date |
| Flags | `tagType`, `tagNumber`, `priority`, `pdcaStatus`, `projectKey`, `labels[]`, `nearMiss` (means the broader H&S category), `safety`, `quality` | keyword / boolean |
| Coverage | `attachmentCount`; `coverage[]`, e.g. `checklist-not-indexed`, `attachments-not-read`, `events-truncated` | integer / keyword |
| Processing | `builderVersion`, `inputHash`, `indexedAt`, `deleted` | keyword / date / boolean |

Left out on purpose: Telegram media details (sender data), likes, actions, Trello cards, questionnaires, `creatorEmail`, process fields, and anything stored as a map keyed by user or push id. With `strict`, a bug in the document builder shows up as a visible indexing error instead of the mapping quietly growing.

What this shape gives with nothing extra:

- **Matching entry:** `inner_hits` on the nested query returns the event that matched (its key, field, author and date). That covers "Show matching entry" from [chapter 2](02-search-jobs-and-experience.md) and the link back to the source, without a separate index of passages.
- **Event-level filters:** nested events keep author, date and text together, so "Mira's checks in March" can't combine three different events (Q13).
- **No double counting:** `collapse` on `threadKey` merges a work record that appears both in a shift and under its parent problem (Q16). The adapter for older clients doesn't collapse.
- **Ranking:** decay from `lastActivityAt` instead of creation lets older but recently active problems rank higher (F7).
- **Missing text found:** `rcaText`, `linkText` and `rootCause` become searchable (Q12, F16), and RCA text no longer overwrites `done`.
- **Totals for intelliflow-sp:** `track_total_hits` returns the plain-number total the old client expects.

## 4. Write ordering

These parts keep the index correct, not just fast. They implement the protocol sketched in [chapter 6 §2](06-search-architecture.md).

```text
RTDB  searchIndex/records/<fac>/<rk> = { gen: 17, pending: true }   (.indexOn: pending)
      searchIndex/failed/<fac>/<rk>  = { gen, error, attempts, at }
      searchIndex/status/<fac>       = { eligible, indexed, lastReconcile, builderVersion, maxLagMs }
```

1. **Catch every change:** a small Cloud Function fires on any write to `facilityData/{fac}/records/{rk}`, deletes included. In one transaction it increments `gen` (the record's change counter) and sets `pending = true`. This catches the changes `lastUpdated` misses: priority, PDCA, project, moves and deletes.
2. **Index:** the worker reads `gen` **first**, then the record. It builds the document and writes it with `version = gen, version_type = external`. If the record no longer exists, it writes a tombstone (`deleted: true`) at that version instead.
3. **Reject stale writes:** a 409 conflict means a newer version is already in the index, so the worker counts it as success. OpenSearch itself refuses the stale overwrite (Q27).
4. **Finish:** another transaction sets `pending = false` only if `gen` hasn't changed in the meantime (Q28).
5. **Backfill:** each record is written with its current `gen`, or 0 if it has none. Start the trigger before the backfill. Records without `lastUpdated` are included (Q14).
6. **Reconcile:** once a day, compare record keys in RTDB (`shallow=true`) with the ids in the index and mark missing or leftover ones as pending. After a builder change, also compare content hashes (`inputHash`). The results go to `status/<fac>`, which the UI can use to warn about incomplete coverage.

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
- **Before testing the trigger:** `intelliflow-functions/firebase.json` has no `emulators` section. Until it does, testing the trigger locally writes to production.

## 6. What's left out, and how each part arrives later

| Later addition | Change to the database | Cost |
|---|---|---|
| Searching equipment names as text | New field, plus re-indexing a node's records when it is renamed (`equipmentRecords/<eq>` lists them) | Re-run the indexer |
| More filters (workgroups, checklists) | New field via `PUT _mapping` | Re-run the indexer |
| Ukrainian/Russian word stems | New analyzer → `records-v2-*`, filled with `_reindex` from v1 (stored `_source` makes that possible), then swap the alias | No RTDB reads |
| Cross-language search (Q06) | First try the machine translations some records already carry (`translations`), in a separate, labeled field | Check how many records have them first |
| Alias register (Milestone D) | Small `aliases-<fac>` index, applied at query time | Record indices untouched |
| Vectors and hybrid retrieval (Milestone D) | `index.knn` can only be set at creation → new v2 index plus plugins | Alias swap |

## 7. Acceptance

Against the [starter scenarios](07-evaluation-and-acceptance.md):

- **Must pass:** Q01, Q05, Q07–Q16, Q23–Q24 and Q27–Q29, plus parity with current search (R1–R13).
- **Q15 partly:** record moves pass; equipment renames only once names are indexed.
- **Later milestones:** Q02–Q04, Q06, Q17–Q22, Q25–Q26 and Q30.

## First step: an offline test

1. Build documents from a full RTDB backup in `prod-data/rtdb/` and load them into a local OpenSearch with this mapping.
2. Measure the index size.
3. Run the evaluation queries against this index and against the old ES 5.4 export loaded locally.

Build from the RTDB backup, not from the ES export. The export is the old parser's output: it drops RCA answers, link entries and `parentRecordRef`, and probably lacks the roughly 15,000 early records with no `lastUpdated`. Both contain production text, so keep them and any results out of this guide and out of git.
