# Plain-language glossary

[Start here](README.md) · [Previous: sources](10-reading-and-sources.md)

| Term | Meaning in this guide |
| --- | --- |
| Organizing system | Resources, descriptions/arrangements, and the interactions they support. IntelliFlow's records plus how people capture, find, and use them. |
| Resource | Anything being organized: an asset, a record, an event, a document, or a collection. |
| Description / metadata | Information used to identify, understand, find, or manage a resource. Its role depends on the task. |
| Surrogate | A representation standing in for something else, such as a search card describing a source record. |
| Identity | Which particular thing is being referred to. Stronger than similar words or similar symptoms. |
| Identifier | A controlled reference to a thing within a defined scope, such as a facility-qualified record key. |
| Alias | Another name for the same confirmed thing. A possible alias is not yet a confirmed identity link. |
| Namespace / scope | The context in which a name or identifier is interpreted, such as a facility or line. |
| Controlled vocabulary | Agreed terms and meanings for a domain, with rules and alternative labels where useful. |
| Taxonomy | A hierarchy of categories, such as equipment types. An equipment location tree is not automatically an equipment-type taxonomy. |
| Facet | One dimension used to filter or organize results, such as location, period, or recorded state. |
| Categorization | Defining or recognizing useful groups. |
| Classification | Assigning a resource to a category. |
| Taskonomy | Organization around the activities people need to perform. Useful for designing search around jobs rather than database fields. |
| Provenance | Where information came from and how it was processed or derived. It helps inspection; it does not guarantee truth. |
| Effectivity | When or where a resource or description applies. A procedure may be valid for one machine configuration and period. |
| Projection | Another stored or displayed view of the same underlying information. A later shift can contain a copy of a work event also shown under its parent issue. |
| Canonical event | The identity used to treat known duplicate projections as one event, while retaining their source locations. |
| Lexical retrieval | Finding words, phrases, or character forms. Valuable for technical terms and precise identifiers. |
| N-gram | A sequence of n characters or tokens. Character n-grams can support partial-word matching. |
| Trigram | A three-character sequence used in some similarity and pattern-search methods. |
| BM25 | A word-based ranking function. Exact code and phrase behavior still depend on the representation and query. |
| Embedding | A numerical representation used to compare content by learned similarity. It is not an asset identifier or evidence of factual equivalence. |
| Semantic retrieval | Finding content by learned meaning similarity rather than requiring the same words. |
| Hybrid retrieval | Combining lexical and semantic or other complementary candidate retrieval methods. |
| RRF | Reciprocal rank fusion: combine result lists using their ranking positions. Its score is not a probability that an answer is correct. |
| Reranker | A second-stage model or method that reorders a limited set of retrieved candidates for a query. |
| Chunk / passage | A smaller unit indexed or supplied to an answer model. In IntelliFlow, a coherent event may be a better boundary than an arbitrary character count. |
| Context expansion | Fetching the parent, nearby events, later corrections, or explicit links needed to interpret a retrieved match. |
| RAG | Retrieval-augmented generation: find evidence, then give it to a model to help produce an answer. Quality depends on retrieval and faithful use of evidence. |
| Grounded answer | An answer whose factual claims are supported by the retrieved sources and whose limits are explicit. |
| Hard negative | A misleadingly similar example that should not count as correct, such as a different asset with the same numeric suffix. |
| Golden query set | A versioned set of representative questions with expected relevant evidence and failure conditions. |
| Recall | The proportion of relevant items found; usually only measurable against a defined judged set. |
| Precision | The proportion of retrieved items that are relevant. |
| Coverage | Whether eligible source identities, fields, and content types are represented in search. Different from recall. |
| Freshness | How up to date the searchable representation is relative to its sources. |
| Idempotent processing | Repeating an operation does not create unintended additional effects. |
| Reconciliation | Comparing sources and derived data to find and repair omissions, stale content, or ghost documents. |
| Fencing token | An ordered processing token used to reject writes from an obsolete worker. It must be designed, not assumed from an arbitrary timestamp. |
| Tombstone | A retained deletion marker used to prevent old work from bringing a deleted item back. |
| Shadow search | Run a candidate search path for comparison without replacing the user's production result path. |
| As-of answer | An answer bounded by a historical cutoff. A true “known at the time” reconstruction needs more history than a filter on visible event dates alone. |

For the book's original terminology, consult its glossary and the sections identified in [the reading map](01-book-summary.md). Technical terms added for modern search implementation are explained here as project vocabulary, not attributed to the book as technology recommendations.
