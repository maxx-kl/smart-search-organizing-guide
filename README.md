# Smart Search for IntelliFlow

**A practical reading of *The Discipline of Organizing*, with a design guide for IntelliFlow.**  
Prepared for Maksim · 18 October 2026

**The central recommendation:** make IntelliFlow's operational history easier to find, distinguish, and understand. Start with complete, dependable search; add equipment-aware aliases and multilingual retrieval; then let Ina explain retrieved evidence with dates and source links.

The book's strongest contribution is a way to decide **what deserves its own identity, which descriptions matter, and which interactions those descriptions should enable**. Those decisions will outlast the choice of search engine or AI model.

## Start with the question workers actually need answered

> “Have we seen this problem before on this equipment, what did people try, and what happened afterward?”

A useful answer needs more than similar wording. It needs the right machine, the right incident, the sequence of work, the unsuccessful attempts, and the limits of the available evidence.

Consider a fictional example: a motor trips; someone suspects overheating; a check does not support that theory; a later work entry reports an electrical repair; production resumes; preventive follow-up is still undocumented. Finding only the first report gives the wrong explanation. Finding only a closed badge hides the uncertainty. See the complete [worked example](09-worked-examples.md).

## Choose a reading route

| Your available time / purpose | Read |
| --- | --- |
| About 10 minutes: understand the recommendation | This page → [worked examples](09-worked-examples.md) → the first two milestones in [delivery plan](08-delivery-plan.md) |
| Understand the book without reading the whole EPUB | [Relevant book summary](01-book-summary.md) |
| Design what users will see | [Search jobs and experience](02-search-jobs-and-experience.md) → [time and evidence](05-time-evidence-and-relationships.md) |
| Prepare an implementation | [Resources and metadata](03-resources-and-metadata.md) → [aliases and languages](04-assets-aliases-and-languages.md) → [architecture](06-search-architecture.md) → [evaluation](07-evaluation-and-acceptance.md) → [OpenSearch database](12-opensearch-mvp.md) |
| Plan the work | [Delivery plan](08-delivery-plan.md), including a first implementation brief |
| Learn unfamiliar terms or read more | [Glossary](11-glossary.md) · [annotated sources and reading list](10-reading-and-sources.md) |

## The collection

1. [The book's most useful ideas](01-book-summary.md) — a selective summary with IntelliFlow implications and an EPUB reading map.
2. [Search jobs and experience](02-search-jobs-and-experience.md) — what “smart” should mean to a worker, result-card sketches, filters, and failure states.
3. [Resources and metadata](03-resources-and-metadata.md) — records, incidents, events, equipment, source pointers, and a minimal derived model.
4. [Assets, aliases, and languages](04-assets-aliases-and-languages.md) — finding variant names without falsely merging assets.
5. [Time, evidence, and relationships](05-time-evidence-and-relationships.md) — chronology, source quality, links, and careful answers.
6. [Search architecture](06-search-architecture.md) — a practical route from the existing search to hybrid retrieval.
7. [Evaluation and acceptance](07-evaluation-and-acceptance.md) — how to tell whether each change actually helps, with a starter query set.
8. [Delivery plan](08-delivery-plan.md) — milestones, decisions, responsibilities, and a bounded first task.
9. [Worked examples](09-worked-examples.md) — invented cases showing the whole idea in use.
10. [Reading and sources](10-reading-and-sources.md) — the supplied book, local evidence, and useful external articles/documentation.
11. [Glossary](11-glossary.md) — plain-language definitions tied to IntelliFlow.
12. [The minimal OpenSearch database](12-opensearch-mvp.md) — indices, analyzers, document fields, and write ordering for Milestones B–C.
13. [Analytics from the search index](13-analytics-from-the-search-index.md) — which counts and reports the search index can serve (draft), with measured results and a comparison with BigQuery.

## Five decisions to carry into implementation

| Decision | Practical consequence |
| --- | --- |
| Preserve original records; enrich a derived representation | Fix vocabulary and retrieval without changing what workers originally wrote. |
| Separate identity from similarity | A motor and the pump it drives may be related, but are not the same asset. |
| Retrieve at several levels | Match an event, display its incident, and load enough history to explain it. |
| Make scope, chronology, and evidence visible | A closed record does not establish a permanent repair; a missing result does not establish that nothing happened. |
| Measure before expanding | Prove lexical coverage, then alias quality, then hybrid improvement, then answer quality. |

## What comes from where

- **Book idea** means a paraphrase of the supplied EPUB, attributed by section title and EPUB entry number. It is a selective application-oriented reading, not a summary of every example or endnote.
- **Handoff finding** means evidence or interpretation reported in the October 2026 local handoff. It has not been independently re-audited against production in this task.
- **Proposal** means my recommendation for Smart Search. It is not an approved architecture, an implemented capability, or a delivery promise.
- **Synthetic example** means invented records, identifiers, dates, and outcomes. These are teaching examples, not customer records.

The local handoff combines technical investigations dated 10–11 October, a memory snapshot dated 14 October, and workflow research through 15 October. The later memory clarifies the direction: **retrieval first, then bounded assistance**. Old descriptions of Ina should not be mistaken for a verified current grounded assistant. See [source reconciliation](10-reading-and-sources.md).

## What this guide deliberately keeps small

The first useful release does not require a graph database, a complete plant ontology, autonomous agents, a new task-management system, or a compulsory form full of classifications. It needs reliable records, useful descriptions, a good search interaction, and evidence that it works.

The architecture is a proposal. No application code, production data, services, or deployments were changed for this guide. No customer records were sent to external research services. All operational examples in the collection are synthetic; local reports are referenced for their findings rather than reproduced as raw evidence.

Diagrams use Mermaid and also have plain-language explanations, so the guide remains usable in Markdown viewers that do not render diagrams. Links between these files are relative so the folder can be moved together; local handoff references are absolute and require this Mac's files.
