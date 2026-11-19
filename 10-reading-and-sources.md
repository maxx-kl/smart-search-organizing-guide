# Sources, attribution, and a short reading list

[Start here](README.md) · [Previous: examples](09-worked-examples.md) · [Next: glossary](11-glossary.md)

Prepared 18 October 2026. Web references were checked during this task; documentation behind “latest” URLs may change. This is a private project guide grounded primarily in the supplied EPUB and local handoff, with additional design recommendations clearly identified as proposals.

## The book

**Robert J. Glushko, editor, *The Discipline of Organizing: 4th Professional Edition* (2020).** EPUB metadata lists publication on 1 April 2020 and identifies Robert J. Glushko as creator. Individual contributions are attributed where used, including Gracen Brilmyer's CalBug case and Hassan Jannah's data-center case.

- Supplied EPUB: `The-Discipline-of-Organizing-4th-Professional-Edition-1588961975.epub` (local copy, not included here; the online edition is linked below)
- [Publisher's online edition and contents](https://berkeley.pressbooks.pub/tdo4p/)
- [Creative Commons BY-NC 4.0 license named by the book](https://creativecommons.org/licenses/by-nc/4.0/)

The EPUB states that the book is licensed under Creative Commons Attribution-NonCommercial 4.0 International, except where otherwise noted. This guide uses original paraphrase and application analysis, rather than reproducing the book or its images. Its diagrams and synthetic IntelliFlow examples were created for this guide.

### Edition and locator note

The supplied EPUB's contents list **Activities in Organizing Systems as Part III (§§19–24)** and **Resources in Organizing Systems as Part IV (§§25–30)**. The online contents inspected during this task reverses those two parts and renumbers the corresponding entries. For example, “Naming Resources” is §28 in the supplied EPUB but appears as entry 22 online.

For that reason, this collection cites **the supplied EPUB entry number plus section title**, not a print page or the live site's current numbering. Some “Key Points in Chapter …” headings retain the book's own chapter labels. The [summary's reading map](01-book-summary.md) uses the local EPUB consistently.

### What was actually read

The EPUB package metadata and complete table of contents were inspected. The relevant conceptual and key-point material was reviewed across Parts I–XI, with particular attention to organizing systems, resource identity, names, resources over time, descriptions, relationships, categories/classification, faceted access, evaluation, and maintenance. Case text was consulted for the small consulting firm, CalBug, and data-center resources.

This is a **selective Smart Search synthesis**. It does not claim exhaustive close reading of every historical example, footnote, or case study. Where a point comes from a chapter's key-point recap, the guide treats it as a high-level book principle, not detailed textual analysis of every subsection.

The local EPUB, rather than web excerpts, is the primary source for the extended book summary. Several online chapter fetches were blocked, which did not prevent reading the supplied local text. The online homepage was useful for confirming metadata and identifying the numbering difference.

## Local IntelliFlow sources

These are dated research sources, not fresh production verification. They live in the private IntelliFlow workspace (paths are relative to it) and are not published here.

| Source | How it informs this guide |
| --- | --- |
| 00 — Start here (`ai-handoff/00-START-HERE.md`) | Workspace overview and boundaries of the original investigation |
| 02 — Product and domain (`ai-handoff/02-PRODUCT-AND-DOMAIN.md`) | Records, equipment, sub-records, work projections, state changes, and source-field meaning |
| 04 — Data model (`ai-handoff/04-DATA-MODEL.md`) | Authoritative stores, change detection, missing historical fields, and dependency invalidation |
| 07 — Current search (`ai-handoff/07-SEARCH-CURRENT.md`) | Existing query behavior, parser omissions, index mechanics, UI and compatibility defects |
| 08 — Search evolution (`ai-handoff/08-SEARCH-EVOLUTION.md`) | Proposed requirements, engine comparison, migration stages, and golden-query testing |
| 09 — Ina and AI readiness (`ai-handoff/09-INA-AND-AI-READINESS.md`) | Potential text/metadata reuse and limitations of the older AI code |
| 10 — Security and permissions (`ai-handoff/10-SECURITY-AND-PERMISSIONS.md`) | Source-level access risks, authorization boundary, and privacy implications; deployed state remains unknown |
| 14 October memory: AI/search direction (`ai-handoff/2026-10-14-chatgpt-memory-snapshot/intelliflow-memory-2026-10-14/04-ai-search-direction.md`) | Latest explicit retrieval-first focus, asset alias examples, uncertainty, multilingual goals, and deferred autonomy |
| 14 October memory: workflows (`ai-handoff/2026-10-14-chatgpt-memory-snapshot/intelliflow-memory-2026-10-14/03-real-world-workflows.md`) | Time, counting, outcome, planning, and conversation-layer pitfalls |
| 15 October HSE executive report (`ai-handoff/2026-10-15-telegram-hse-coordination/executive-report.md`) | Closure and resolution can diverge; duplicate/master links; partial capture and unavailable media |

### Reconcile the sources instead of blending them silently

1. **Ina:** the earlier code review says Ina does not exist as implemented code in the inspected scope. The later owner-memory snapshot describes Ina as an established product identity and historical pilot context. These can both be true. This guide treats Ina as an intended identity for future grounded assistance, not a verified current capability.
2. **Engine choice:** OpenSearch is an owner leaning. Versions, hosting, sizing, and timing in older proposals are not final decisions or current benchmarks.
3. **Retrieval unit:** earlier documents propose one composed thread. Later memory calls the natural unit task-dependent. This guide recommends a parent container with identifiable events, then passage-level expansion if justified.
4. **Change ordering:** the migration sketch's timestamp/external-version proposal is not a proven consistency protocol. This guide calls for explicit race handling and reconciliation.
5. **Corpus totals:** counts come from different dates and source scopes. They must not be combined into an apparently precise current coverage percentage.
6. **Security:** source findings are material prerequisites to investigate; this guide neither claims those vulnerabilities remain live nor claims they have been fixed.

## Read these first

The following annotations are brief; the IntelliFlow applications elsewhere in the guide are our proposals, not endorsements by the cited authors.

### 1. Naming and durable identity

**[Tim Berners-Lee — Cool URIs don't change](https://www.w3.org/Provider/Style/URI.html.en)** · Essay · Short

Why useful: explains why stable identifiers should survive changing organization and implementation. Apply the principle to source citations and existing `infl.app` links. A durable identifier still needs a maintained resolver and access checks; this is not an instruction to redesign the shortener.

### 2. A simpler interface over richer structure

**[Gracen Brilmyer — CalBug and its Search Interface Redesign](https://berkeley.pressbooks.pub/tdo4p/chapter/calbug-and-its-search-interface-redesign/)** · Case study in the supplied book · Short

Why useful: shows how user-facing search can reorganize access to richer underlying fields. Read it alongside IntelliFlow's parent/event date and author distinctions. Its museum examples do not determine the right plant vocabulary.

### 3. How to combine word and meaning matches

**[OpenSearch — Introducing reciprocal rank fusion for hybrid search](https://opensearch.org/blog/introducing-reciprocal-rank-fusion-hybrid-search/)** · Engineering blog · Medium

Why useful: explains one method of merging independently ranked result lists. Its own experiments show trade-offs rather than universal superiority. Use it to understand a baseline, then judge IntelliFlow results. Consult the [RRF documentation](https://docs.opensearch.org/latest/vector-search/ai-search/hybrid-search/rrf/) for the chosen supported version.

### 4. Why isolated chunks lose meaning

**[Anthropic — Introducing Contextual Retrieval](https://www.anthropic.com/engineering/contextual-retrieval)** · Engineering article, 19 September 2024 · Medium

Why useful: explores contextualizing passages and combining lexical and semantic retrieval. Its reported percentages, model choices, and costs belong to its experiment and date; they are not forecasts for IntelliFlow. Our first proposed application is deterministic event context, with generated context evaluated separately.

### 5. How to measure retrieval

**[Manning, Raghavan, and Schütze — Evaluation in information retrieval](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-in-information-retrieval-1.html)** · Textbook chapter · Medium

Why useful: connects judged relevance, representative collections, user utility, and result presentation. The companion [ranked-results section](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-ranked-retrieval-results-1.html) explains rank-sensitive metrics. Read before using a single number to declare a new engine “better.”

## Useful references during implementation

| Reference | Use it for | Limit / caution |
| --- | --- | --- |
| [W3C SKOS Primer](https://www.w3.org/TR/skos-primer/) | Preferred/alternative labels, concept relationships, vocabulary scope | Borrow useful distinctions; a full RDF deployment is not required for this project |
| [W3C PROV Primer](https://www.w3.org/TR/prov-primer/) | Understanding source entities, derivation activities, and responsible agents | Traceability does not certify the truth of the original claim |
| [OpenSearch nested fields](https://docs.opensearch.org/latest/mappings/supported-field-types/nested/) | Keeping author, date, and text conditions associated with one event | Check mapping, limits, and query behavior for the selected version |
| [PostgreSQL 18 `pg_trgm`](https://www.postgresql.org/docs/18/pgtrgm.html) | Trigram similarity and pattern-search options in a bounded alternative spike | Documentation version is explicit; the existing managed server's version/extensions were not inspected |
| [Firebase RTDB triggers](https://firebase.google.com/docs/functions/database-events) | Capturing source writes | Trigger availability is not an end-to-end exactly-once indexing guarantee |
| [Firebase tips and tricks](https://firebase.google.com/docs/functions/tips) | Idempotent processing and operational considerations | Design and test queue acknowledgements, retries, ordering, and leases explicitly |
| [Thakur et al. — BEIR (2021)](https://arxiv.org/abs/2104.08663) | Why evaluation needs diverse tasks and domains | Public benchmark results do not replace plant-language and equipment-code tests |

## Optional classic referenced by the book

**[William Denton — How to Make a Faceted Classification and Put It On the Web](https://www.miskatonic.org/library/facet-web-howto.html)** · Practical guide

The book cites this in its facet-design discussion. The author's page returned a verification screen during this task, so its current full text was not independently reviewed here. It is offered as an optional further-reading lead, not as fresh evidence for a technical claim. The supplied book's §54 is the reviewed source for the facet principles in this guide.

## What was verified for this deliverable

The supplied EPUB and named local reports were read for the scoped research. Source paths and the collection's internal navigation were checked. All Markdown files parsed successfully, including their tables. Diagram source and illustrative examples were reviewed for consistency with the written proposals. Automated Mermaid parsing was attempted but hit a DOMPurify environment error; diagrams were not browser-rendered, and each has a text explanation. No engine benchmark, model evaluation, live permission audit, browser behavior test, or production-data inspection was performed for this writing task.

Future implementation should revisit dated handoff facts and version-sensitive technical references. The most durable part of this collection is the decision framework: choose the interactions, preserve identities and evidence, organize enough to support the task, and measure the result.
