# Analytics from the search index

[Start here](README.md) · [Previous: the minimal OpenSearch database](12-opensearch-mvp.md)

**Status: draft for discussion, written 21 November 2026. Nothing has been built.**

**Question:** can the new search database (OpenSearch, filled by `services/infl-search`, [chapter 12](12-opensearch-mvp.md)) also answer analytics questions? The example question was *"how many tasks do people have, and across how many problem records?"*

**Short answer:** yes, for questions about the **current state**. Examples are open tasks per person, overdue items and open items per problem. The index already holds the fields these questions need, the answers are exact, and on the test node they took 5–100 ms. Questions about **trends and history** fit worse: monthly reports by department, time to close and workload over time. The index lacks department membership, close dates and any change history, and BigQuery already holds most of that.

**Recommendation:**
1. Serve a fixed set of operational reports from OpenSearch through the existing `search/v2` queue. Do not let clients send their own aggregations.
2. Add a few derived fields in the next builder version.
3. Keep trend reporting in BigQuery, and give BigQuery the checklist data it lacks today.
4. Don't run OpenSearch Dashboards on droplet02.

**Basis:** `infl-general/checklist-types.ts` and `records-types.ts`; the intelliflow "My tasks" view and issue board (`users/user.service.ts` `getProblemsWithResponsible`, `issue-board.component.ts`); `services/infl-search` (`core/analysis.ts`, `core/builder.ts`); `services/infl-stat` (`records.ts`); the BigQuery table `stat_data.records` (schema and metadata only). Every number below comes from read-only queries on the offline test node (OpenSearch 3.10, laptop, 2 GB heap). That node holds all 13 facilities: records from the 10 October 2026 RTDB backup and checklist items from the 20 November 2026 Firestore export. Only aggregate numbers appear here; people are labelled A, B, C….

## 1. What "tasks" means in IntelliFlow

The app already defines it. The **Tasks** tab under a user ("My tasks", `MyTasks`) lists the records that have **open checklist items with that user as the responsible person**. Its counter is the number of such records. The data comes from `checkListTasks`, an index the checklist trigger maintains. It holds every open item that has a due date or a responsible person, on any record type. The issue board reads the same index and groups the items by due date (overdue, today, this week…).

So the example question means: **for each responsible person, the number of open checklist items, and the number of distinct records those items are on.**

Other readings exist but don't match the app's wording:
- a problem's `todo` text (free text with no owner or state);
- problems "assigned" to workgroups (`editedWgList`; not indexed, see §3);
- active problems a person created.

Checklist items exist only on problems. None of the 458,352 records has items on a work record. So the "work record copied under its parent" problem from chapter 12 can't double-count tasks.

## 2. What the index holds for analytics

Every `keyword`, `date`, `boolean` and numeric field in the `records-v2` mapping has doc values, so you can aggregate on it. The `text` fields (`description`, `done`, `todo`, `rootCause`, `rcaText`, comment and item text) have no fielddata and can only be searched, not grouped. `_source` is stored, so the whole document can be read back.

| Level | Fields usable in aggregations |
|---|---|
| Record | `facilityKey`, `recordKey`, `recordType` (`activeProblem` / `closedProblem` / `workRecord`), `parentRecordKey`, `threadKey`, `eqL1Key`–`eqL3Key`, `creatorKey/Name/Group`, `dateCreated`, `lastUpdated`, `lastActivityAt`, `tagType`, `tagNumber`, `priority`, `pdcaStatus`, `projectKey`, `labels`, `nearMiss`, `safety`, `quality`, `attachmentCount`, `coverage`, `codes` |
| Nested `subRecords` (events) | `recordType` (comment, workRecord, stateChange, link), `stateChange` (`active` / `closed`), `creatorKey/Name/Group`, `dateCreated`, `linkType`, `link`, `inReplyTo`, `codes` |
| Nested `checklistItems` | `checked`, `responsibleKey/Name`, `creatorKey/Name`, `checkedByKey/Name`, `due`, `dateCreated`, `checkedDate`, `lastUpdated`, `order`, `codes` |

Size of the test data: 458,352 records (319,513 work records, 134,843 closed and 3,991 active problems), 91,380 checklist items on 32,741 problems, and 247,039 events. That makes 796,771 Lucene documents counting nested ones, and 482 MB on disk across 13 single-shard indices.

**Missing for analytics:**

| Missing | Where it lives | Effect |
|---|---|---|
| Workgroups a problem is assigned to (`editedWgList`) | RTDB record; BigQuery `workGroups` (as names) | No "problems per department". Only `creatorGroup`, the creator's workgroup, is available |
| Responsible person's workgroup (`responsible.workgroup`) | RTDB item; the builder drops it | No "open tasks per department" |
| Close date | Only as a nested `stateChange: closed` event; BigQuery has `fixedAt` | Time to close needs a script or client-side work (§4.4) |
| `closed`, `closedByKey`, `tagClosedBy`, `planning`, `processType` | RTDB record | No "closed by" or planned/unplanned splits |
| Who set the due date or the responsible person, and when (`dueSetBy…`, `responsibleSetBy…`) | RTDB item | No "tasks assigned by X" |
| Change history: reassignments, unchecking, due-date moves | Nowhere (only the latest state is stored) | Past workload can only be estimated (§4.5) |
| Equipment, workgroup and user names | RTDB lookups | Results group by key; the client has to resolve names. The stored `creatorName` / `responsibleName` are snapshots taken at write time |
| Deleted items and deleted records | Tombstones keep the key only | Nothing about deleted work |

## 3. The example question on real data

One request per facility (or one over all 13 aliases). It is a `nested` aggregation on `checklistItems`, a filter `checked: false`, `terms` on `responsibleKey`, and then `reverse_nested` back to the record:

```json
{"size": 0, "aggs": {"items": {"nested": {"path": "checklistItems"}, "aggs": {
  "open": {"filter": {"term": {"checklistItems.checked": false}}, "aggs": {
    "people": {"terms": {"field": "checklistItems.responsibleKey", "size": 2000}, "aggs": {
      "overdue": {"filter": {"range": {"checklistItems.due": {"lt": "now"}}}},
      "records": {"reverse_nested": {}, "aggs": {
        "active": {"filter": {"term": {"recordType": "activeProblem"}}}}}}}}}}}}}
```

The `reverse_nested` bucket's `doc_count` is the **exact** number of distinct records. On these data it matched `cardinality(recordKey)` for all 210 people. `cardinality` isn't needed here.

**Result (all 13 facilities):**

- 3,430 open checklist items in total. 2,696 have a responsible person, 1,980 have a due date.
- 210 people have open tasks: 2,696 items on 1,953 person-record pairs, of which 1,912 are active problems. Two people have tasks in more than one facility.
- Per person: median 3 items on 3 records; 90th percentile 32 items on 19 records; maximum 208 items on 142 records.
- The five largest: person A 208 items on 142 records (139 active problems); B 206 on 131; C 160 on 110; D 124 on 97; E 81 on 70.
- 57 closed problems still have open items. The app's Tasks tab counts them too, because `checkListTasks` doesn't look at the record's state. A report should say which convention it uses.

**Overdue, relative to the checklist export date (20 November 2026):** 670 open items with a due date are overdue, on at most 449 records (a record can fall into two age bands). By age: under 7 days 119, 7–30 days 186, 30–180 days 262, over 180 days 103. Another 1,310 items are due later. 22 overdue items have no responsible person. Took 24–57 ms.

## 4. Other questions tried

### 4.1 Problems per creator group and location per month

A `date_histogram` on `dateCreated` (calendar month, `time_zone: Europe/Kyiv`), with `terms` on `creatorGroup` and `eqL2Key` nested inside. October 2025 to September 2026: 22,277 problems, 1,600–2,020 a month, 15–18 creator groups and about 500–625 level-3 locations a month. 40 ms median, 115 ms max.

Caveats:
- This is *creator* group, not the department responsible for the problem (§2).
- Facilities are in more than one time zone. `infl-stat` runs per time-zone group, so a monthly report should bucket each facility in its own zone.

### 4.2 Work and events over time

Events per month with distinct authors: 14–16 ms. Counting work needs care. 136,561 top-level work records have a parent, and 78,730 copies of them also sit under the parent as `subRecords` events with `recordType: workRecord`. Count work from the top-level documents only, or dedupe on `threadKey`. Never add the two together.

### 4.3 Checklist throughput

Items created and checked per month (May–October 2026), and how many were checked by their own responsible person. For example, 5,821 items with a responsible person were checked in those six months, 4,195 of them by that person. The comparison uses a doc-values script (`doc['…checkedByKey'] == doc['…responsibleKey']`), which works.

### 4.4 Time to close: the hard case

The close date is a nested event and the creation date sits on the parent. Plain aggregations can't subtract one from the other. Two attempts:

- **A script over `_source` inside a `percentiles` aggregation:** 7 of 13 shards failed with `security_exception: Denied OPEN (read) access` when Painless tried to load stored source. That looks like OpenSearch 3.10's script sandbox and is probably not specific to the laptop. **The request still returned HTTP 200** with the six surviving shards' numbers. Scripts that read doc values had no such failures.
- **Client side:** a read-only scroll over the 20,353 problems created in that year and now closed. It fetched `dateCreated` and the close events, took 0.8 s, and the client did the arithmetic.
  - 8,757 have a close event: median 8.1 days to the last close, 75th percentile 36.4, 90th percentile 90.3 days.
  - 11,596 (57%) have no close event and were last updated the same day they were created. These problems were *logged as already closed* (the app offers `closedProblem` as a creation type). `infl-stat` makes the same call (`fixedAt = dateCreated`).
  - 328 were reopened at least once.

A `closedAt` field written by the builder makes this an ordinary aggregation (§6).

### 4.5 Past workload

Items store `dateCreated`, `checked` and `checkedDate`. That makes "open at date T" computable: created before T, and either still open or checked after T. Open items at each month end, May–November 2026: 3,626–3,873.

This is an estimate. The index can't see an item that was unchecked and checked again, a reassignment (it only sees today's responsible person), or a deleted item. "Who was responsible on 1 September" is not answerable.

### 4.6 Latency

Ten runs each, request cache off. The time for the largest facility alone was about the same as for all 13:

| Report | Median | Max |
|---|---|---|
| Open tasks per person, with distinct records | 5 ms | 15 ms |
| Overdue aging | 24–57 ms | — |
| Problems per month × creator group × location | 40 ms | 115 ms |
| Events per month with distinct authors | 15 ms | 23 ms |
| `cardinality` of `recordKey` and `threadKey` | 30 ms | 122 ms |
| Time to close, client-side scroll of 20k documents | 0.8 s | — |

The laptop has more and faster cores than droplet02's 2 vCPUs and 1 GB heap. Expect several times these numbers there, which still fits comfortably inside the 3 s search limit.

## 5. Accuracy rules for any report built on the index

- **Distinct counts:**
  - Prefer the `reverse_nested` `doc_count` (exact).
  - `cardinality` is approximate: with the default precision it was 0.57% low on 458,352 record keys, and with `precision_threshold: 40000` 0.56% high. Below the threshold (40,000 at most) it is close to exact, which covers per-facility counts of problems and people.
- **Partial failures:** a request can succeed with failed shards. Check `_shards.failed == 0`, or refuse the result.
- **`terms` completeness:** check `sum_other_doc_count == 0` and raise `size` if it isn't. With one shard per facility, `terms` is exact within a facility. Across facilities, use per-facility requests or check `doc_count_error_upper_bound`.
- **Tombstones:** query the read aliases (`records-<fac>`), which filter out `deleted: true`. Don't query `records-v2-*` directly. A wildcard that matches the concrete index name directly may bypass that filter, so list the aliases explicitly.
- **Projections:** dedupe work on `threadKey` (§4.2).
- **Freshness:**
  - On droplet02, a change reaches the index within seconds: the triggers `searchIndexRecord` and `searchIndexChecklistItem` (intelliflow-functions `50f0b83`) bump `gen` for record *and* checklist-item writes, and `refresh_interval` is 1 s.
  - Check `maxLagMs` in the indexer lifebeat and `searchIndex/status` before trusting a count.
  - On the test node the two sources have different dates. Items on records created after 10 October are missing, which shows as the October drop in §4.3.
- **Names:** group by keys, and resolve names from `users` / `workgroups` / `equipment` at display time.
- **No `_source` scripts:** see §4.4.

## 6. Options compared

| | Freshness | What it can answer | Effort | Load / risk |
|---|---|---|---|---|
| **OpenSearch, fixed reports via `search/v2`** | Seconds | Current state: tasks per person, overdue, open items per record/location/creator group, simple monthly counts | Small: a `kind: 'stats'` request with a named report, the existing membership check, a response shape. Builder v3 adds derived fields | Bounded aggregations on doc values, 5–100 ms. Searches and reports share 2 vCPUs, so cap the report size and rate |
| **BigQuery `stat_data.records`** (`infl-stat`, nightly) | Nightly. Table last changed 20 Nov 2026 21:32 UTC, 159,334 rows | History and trends with names: `fixedAt`, `workGroups`, fixer, equipment names, planned/unplanned, PDCA, any SQL | Already running. **No checklist data:** `checkListItemsCount` is always -1. Covers 7 facilities. Updates rely on `lastUpdated`, so changes that don't bump it are missed | None on droplet02. Dashboards outside the workspace already read it |
| **`infl-stat` extended** with a checklist-items table | Nightly | The example question as history: tasks per person per day, per workgroup (via `responsible.workgroup`) | Medium: read `checkListItems` per facility (about 91k items in all), add a table and a merge, decide on daily snapshots | droplet01 has 1 GB RAM. Checklists are small enough |
| **Separate analytics index** (e.g. one flat document per checklist item) | Seconds, if the indexer writes it | The same as the main index, with simpler queries, no nested aggregations, and room for history fields | Medium: second builder output, second mapping, its own backfill and reconcile | Doubles the write path on a small node. Not needed at today's sizes |
| **OpenSearch Dashboards on droplet02** | Seconds | Anything, ad hoc | Low to install | About 0.5–1 GB of RAM for its Node server on a 4 GB machine that already runs a 1 GB heap and the Node workers. Needs an exposed port or an SSH tunnel and per-facility roles, because the `infl_search` role sees every facility. Chapter 12 left it out to save memory. **Not recommended** |

## 7. Recommendation

1. **Operational counts from OpenSearch.** Add a `stats` request to the `search/v2` contract that names one of a few fixed reports:
   - `tasksByResponsible`: per responsible person, open items, overdue items and distinct records. This is the example question. **Decided 21 November 2026: match the app.** A task is an open item with a responsible person, on any record, so items on closed problems count, as they do on the Tasks tab. Items with a due date but no responsible person aren't anyone's task. They appear only in the overdue report, as on the issue board.
   - `overdueAging`.
   - `openItemsByLocation`.
   - `problemsByMonth`.

   The query process builds the aggregation, checks `_shards.failed` and `sum_other_doc_count`, and returns keys and counts. The client adds names. Membership is checked as for search, with one facility per request. Clients never send aggregation bodies.
2. **Builder v3 fields.** Add them to the template and to the live indices with `PUT _mapping` before the new builder writes (the mapping is `strict`), then bump `BUILDER_VERSION` and run `backfill --rebuild`. No new index version is needed:
   - `closedAt`: the last `closed` event, or `dateCreated` for problems created closed;
   - `createdClosed`: boolean;
   - `workgroups`: keys from `editedWgList`;
   - `checklistItems.responsibleWorkgroup`;
   - optionally `openItemCount` on the record.

   Overdue depends on "now" and stays a query-time filter.
3. **Trends stay in BigQuery.** Extend `infl-stat` with a checklist-items table (or daily per-person snapshots) and fill `checkListItemsCount`, so "tasks per person over time" is possible there. Have it read the same change counter (`searchIndex/records`) or do a full nightly read of the checklists, rather than `lastUpdated`.
4. **No Dashboards and no separate analytics index for now.** Look again if the number of reports grows or item history becomes a requirement.

## Open questions for the decision

- ~~Should "tasks" follow the app, or count only active problems?~~ Decided 21 November 2026: follow the app (see §7.1).
- Per person only, or also per workgroup? Per workgroup needs builder v3 (`responsibleWorkgroup` / `workgroups`).
- Who sees the reports: every facility member, or managers only? This decides whether `stats` needs a role check beyond membership.
- Is "today" enough, or are history and trends needed? History points to the BigQuery route.
