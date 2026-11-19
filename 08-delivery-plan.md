# A staged delivery plan

[Start here](README.md) · [Previous: evaluation](07-evaluation-and-acceptance.md) · [Next: worked examples](09-worked-examples.md)

**Recommendation:** deliver dependable search in small increments. Make the first milestone a visible improvement people can use, while preparing the evidence needed to choose later techniques.

**Book basis:** EPUB §§70–75, especially separating requirements from implementation and planning for maintenance. **Local basis:** earlier search roadmap (`ai-handoff/08-SEARCH-EVOLUTION.md`) and 14 October direction (`ai-handoff/2026-10-14-chatgpt-memory-snapshot/intelliflow-memory-2026-10-14/04-ai-search-direction.md`). This plan refines those proposals; it is not an adopted sprint schedule.

## Milestone A — Understand and stabilize the baseline

**Deliverables:** a short behavior inventory, an initial judged query set, visible timeout/error handling, and an eligibility/coverage definition for a pilot facility.

Read current code before acting on the dated handoff. Confirm which findings remain open, especially the unreadable-error path and search authorization dependencies. Verify deployed access policy before a live pilot; offline synthetic research can proceed while that is unresolved.

Keep the existing lexical behavior as a baseline. Capture query/result identities for evaluation under a deliberate data policy, not indiscriminate production logging.

**Exit evidence:** a worker can distinguish no matches from a failed search; existing key searches are pinned by tests; missing coverage is measured against a defined source snapshot.

## Milestone B — A complete, rebuildable search representation

**Deliverables:** a deterministic document builder, historical backfill, source pointers, event-level fields, and a tested update/reconciliation protocol.

Include problem text, standalone work, comments, state changes, root cause, RCA questions/answers, and link text where the source supports them. Record explicitly whether checklists and attachments are included. Preserve unknown historical values.

Test duplicate projections, equipment moves/renames, parser oddities, retries, late events, deletes, and updates arriving during acknowledgement. Measure full and incremental processing before choosing a reconciliation frequency.

**Exit evidence:** every eligible pilot identity is indexed or explicitly accounted for; a rebuild is repeatable; drift can be detected and repaired; an old worker cannot overwrite newer results.

## Milestone C — Choose the engine and pilot modern lexical search

**Deliverables:** a bounded comparison, an engine decision note, a shadow query path, and the legacy compatibility adapter.

OpenSearch is the leading candidate from owner context, not a final decision. PostgreSQL is worth a bounded alternative only if existing infrastructure and available extensions make it credible. Agree the time budget and stopping rule for the comparison; do not investigate every search product.

Keep the representation and relevance tests as constant as practical. Compare actual requirements: exact identifiers, partial words, phrases, nested author/date matching, language behavior, highlights, memory, and maintenance.

**Exit evidence:** reviewed relevance differences, measured resource use, a successful rollback drill, and contract tests for both client generations. Pilot one facility before broad rollout.

## Milestone D — Equipment-aware aliases and multilingual retrieval

**Deliverables:** a small reviewed alias/vocabulary register, collision tests, and a hybrid retrieval experiment.

Alias work and semantic experiments may proceed partly in parallel once the baseline is stable. Neither requires a complete taxonomy. Keep exact searches reliable while testing semantic questions on a held-out set.

**Exit evidence:** useful gains on actual questions, no false merges in the hard-negative suite, and reviewed results for each language claimed in the pilot. Cost and latency remain within an agreed budget.

## Milestone E — Read-only cited explanations

**Deliverables:** source-history expansion, an answer format with scope and limitations, citation validation, and contradiction/abstention tests.

Start with “summarize this issue's retrieved history” and “explain these comparable incidents.” These have bounded evidence sets. Keep ordinary results accessible next to the explanation.

Defer broad counts, unbounded plant-wide synthesis, and operational actions until their evidence and access requirements are separately met. Historical “as known then” answers need a precise statement of what can actually be reconstructed.

**Exit evidence:** critical claims are supported, later corrections are not omitted, unavailable attachments are acknowledged, the assistant abstains on insufficient evidence, and model failure does not remove access to search results.

## Milestone F — Extend only from observed demand

Possible later work: approved manuals, controlled procedures, attachment/OCR retrieval, component inventories, confirmed recurrence groups, and structured analytical queries.

Choose one extension from repeated user needs. Each new source adds authority, permissions, time/version semantics, ingestion, and maintenance work. The book's scope discipline is especially useful here.

## Decisions that need an owner, not a default hidden in code

| Decision | Suggested starting position | Evidence needed to finalize |
| --- | --- | --- |
| Pilot | One facility and a small mix of roles | Representative questions and someone available to judge results |
| Engine/hosting | OpenSearch leading candidate; bounded PostgreSQL check if justified | Benchmark, supported features, maintenance capacity, total cost |
| Ranking | Relevant history by default for exploratory questions; clear current-state filters | Side-by-side worker evaluation; preserve old behavior until changes are justified |
| Date/author semantics | Distinguish parent from matching event | Examples of what current users expect |
| AI processing policy | No provider assumption | Customer-approved data handling, retention, hosting, and cost terms |
| Source scope | Start with defined record fields; state omissions | Coverage inventory and source permissions |
| Component identity | Candidate mentions until confirmed | Asset references and a reviewer |
| `intelliflow-sp` | Preserve through an adapter initially | Contract tests and the actual migration/retirement plan |
| Historical answers | Event-bounded explanation with explicit limits initially | What source history/versioning really exists |

## Who maintains what?

| Responsibility | A practical owner |
| --- | --- |
| User tasks and relevance judgments | Maksim plus a few pilot users |
| Builder, change capture, tests, operational monitoring | Maintainer |
| Local terminology and disputed asset aliases | A named plant/domain reviewer |
| Permissions and external AI data policy | Responsible customer/technical owners |
| Model-generated candidate metadata | Automated processing, with reviewed acceptance rules |

This need not become a committee. The point is that vocabulary disputes, source quality, and service failures should not become ownerless tasks.

## First implementation brief

> **Objective:** make one facility's existing record search measurable and dependable before adding semantic retrieval.
>
> **Scope:** inspect the current query/parser/client error path; define pilot source eligibility; create a small synthetic regression corpus and an initial private judged-query list; implement bounded loading/error behavior and targeted request validation where still needed; document current ranking and filter semantics.
>
> **Preserve:** substring/transliteration capabilities, matching within sub-records, existing facility access boundaries, navigation by source key, and the legacy client contract.
>
> **Acceptance:** failed searches terminate visibly; malformed inputs do not crash the worker; known-item behavior is pinned; dated handoff defects are marked verified/fixed/not reproduced; no production data enters committed fixtures.
>
> **Out of this first task:** engine cutover, embeddings, automated asset merges, generative answers, task management, deployments, and source-record rewrites.

This brief is deliberately narrow enough to review. The next brief should cover the builder and update protocol once the baseline findings are known.

## What to track each week during a pilot

Review missing known records, wrong-equipment matches, unanswered questions, indexing lag, service failures, and a few complete user journeys. Keep a decision log: what changed, which examples motivated it, which slice improved, and what became worse.

Do not optimize all facets or vocabulary entries in advance. Let recurring failures identify the next organizing work worth doing.
