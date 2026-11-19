# How to know whether Smart Search is better

[Start here](README.md) · [Previous: architecture](06-search-architecture.md) · [Next: delivery plan](08-delivery-plan.md)

**Proposal:** maintain a small, versioned set of representative questions with explicit relevance judgments and failure conditions. Use it before every consequential retrieval, normalization, or model change.

**Book basis:** EPUB §67, “Evaluating Interactions,” and §33 on description quality. **Local basis:** [search-evolution validation plan](/Users/maksimklimenko/dev/infl/ai-handoff/08-SEARCH-EVOLUTION.md) and [IF-AI-07 evaluation guidance](/Users/maksimklimenko/dev/infl/ai-handoff/2026-10-14-chatgpt-memory-snapshot/intelliflow-memory-2026-10-14/04-ai-search-direction.md).

## Evaluate the chain, not just the final answer

```text
Source coverage → Correct representation → Candidate retrieval
                → Useful ranking → Complete enough evidence → Faithful answer
```

A missed record can originate anywhere in this chain. If the source was never indexed, changing the language model will not fix the cause. If a later correction was indexed but never fetched, a fluent answer may still repeat a disproven hypothesis.

The information-retrieval literature emphasizes representative collections and relevance judgments rather than assuming a technique transfers successfully between domains. [Stanford: evaluation in information retrieval](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-in-information-retrieval-1.html). BEIR's research similarly motivates testing across different retrieval tasks; it does not establish the best engine or embedding model for plant records. [BEIR paper](https://arxiv.org/abs/2104.08663).

## Construct the first evaluation set

**Suggested initial size, not a statistical guarantee:** about 60 questions to expose obvious failures, expanded toward 100–200 after pilot feedback. The handoff also recommends a 100–200-query golden set.

Include known-item searches, symptom searches, history questions, structured filters, no-answer cases, and adversarial identity/permission cases. Sample by facility, language, age, record kind, and content location—not just recent Ukrainian problem titles.

For each question store:

| Field | Purpose |
| --- | --- |
| Question and task | Distinguish literal query text from the intended need |
| Authorized user/scope | Define what the test is allowed to see |
| Time semantics | Creation, recorded event, occurrence, current state, or historical cutoff |
| Corpus snapshot | Make repeated runs comparable |
| Relevant source identities | Record/event IDs and relevance grades |
| Hard negatives | Similar-looking items that must not be mistaken for the answer |
| Required evidence | A later correction or outcome that must be included |
| Forbidden claim | A plausible but unsupported conclusion |
| Judgment origin | Human reviewer, source evidence, and unresolved disagreement |

Keep real records and query logs in an approved private evaluation location, not committed fixtures or shared documentation. The synthetic set below can be used in repository tests. Do not paste production text into this guide.

### Avoid training yourself to the test

Use one portion for tuning and a held-out portion for final comparison. Split by incident/thread where appropriate: placing one event in the tuning set and another near-identical event from the same incident in the holdout inflates confidence.

Pool candidates from old lexical, new lexical, and hybrid search for human judgment. If you judge only the old engine's results, genuinely useful new results will be incorrectly treated as failures. Unknown relevance should remain unjudged, not automatically irrelevant.

For multilingual cases, have a qualified speaker assess meaning. Record disagreements rather than hiding them behind an averaged score.

## Starter acceptance scenarios

**All identifiers and wording are synthetic.** These rows specify behavior; they are not executed test results.

| ID | Question or setup | Expected behavior / required evidence | Failure to catch |
| --- | --- | --- | --- |
| Q01 | `PT-12` | Exact code hits clearly distinguished | A different code wins through fuzzy expansion |
| Q02 | `MOT 123321` with a confirmed `МОТ123321` alias | Find the correct scoped asset history | Alias match omitted |
| Q03 | Same suffix on another line | Preserve separate candidates; use explicit context | False identity merge |
| Q04 | Pump and motor share a number | Show relation if known; do not equate assets | Component conflation |
| Q05 | Typo `Simens` | Find supported manufacturer variants | Turning off transliteration also removes typo handling |
| Q06 | Ukrainian query; relevant Russian work entry | Retrieve the relevant cross-language evidence | English-only semantic quality assumption |
| Q07 | Latin-typed Cyrillic | Find relevant text using supported transliteration | Overbroad rewrite destroys exact codes |
| Q08 | Query term longer than 15 characters | Match its complete word where present | Old n-gram limitation persists |
| Q09 | Short term / two-digit fragment | Controlled broad results or explicit refinement | Unbounded noisy matching |
| Q10 | Exact phrase with an unrelated word-order near-match | Exact phrase ranks/filters according to documented mode | Phrase behavior claimed but unsupported |
| Q11 | Work record with empty description and useful `done` | Find the work | Only titles indexed |
| Q12 | Query matches only an RCA answer or link text | Find and identify the source field | Parser drops evidence |
| Q13 | “Mira's checks in March” | Text, author, date meet the chosen event semantics together | Fields match different events |
| Q14 | Known old record has no `lastUpdated` | It is in the full backfill | Historical record silently absent |
| Q15 | Equipment renamed or record moved | Search reflects the updated intended context | Dependency invalidation missed |
| Q16 | Work appears in parent and later shift | Group/deduplicate as one event for the chosen unit | Double-counting |
| Q17 | Hypothesis followed by negative check | Include the check; preserve uncertainty | Initial hypothesis becomes asserted cause |
| Q18 | Closed issue with incomplete outcome evidence | State “recorded closed,” qualify physical outcome | Closure becomes proof of repair |
| Q19 | Closed duplicate links to active master | Inspect authorized linked master | Unfinished work disappears |
| Q20 | “What was known by Tuesday?” | Exclude later evidence; disclose limits of historical reconstruction | Future information leaks into past narrative |
| Q21 | “How many repairs?” with only top-k retrieval available | Define count unit and use supported exhaustive path, or abstain | A ranked result count is reported as total repairs |
| Q22 | Attachment referenced but not ingested | State it was not examined | Model invents image contents |
| Q23 | Search worker down / timeout | End loading with a useful error | Infinite spinner |
| Q24 | User changes request to unauthorized facility | No result, count, snippet, suggestion, cache, or citation leakage | Client-provided scope trusted |
| Q25 | User loses membership after cached search | Revalidate access; deny future source/answer access as required | Stale cache bypasses revocation |
| Q26 | Record text instructs Ina to ignore rules | Treat it as record content | Prompt injection changes tool behavior |
| Q27 | Late worker retries an older state | Newer indexed state survives | Stale overwrite |
| Q28 | New update arrives while worker acknowledges old generation | New work remains pending | Lost update |
| Q29 | Delete followed by stale indexing retry | Deleted source is not resurrected | Ghost record |
| Q30 | Semantic service fails but lexical search works | Return lexical results with a concise limitation | Optional AI disables all search |

Add native-speaker-reviewed Georgian/Azerbaijani cases before claiming support for those languages. These 30 scenarios are a starting checklist, not a substitute for real relevance judgments.

## Useful measurements in plain language

| Measure | Definition | Use |
| --- | --- | --- |
| Coverage | Indexed eligible source identities / eligible identities in a defined snapshot | Detect missing history; separately track fields and source kinds |
| Hit@5 | Fraction of known-item questions with an expected item in the first five results | Can a user quickly find a remembered record? |
| Precision@k | Relevant results among the first k divided by k, under a documented treatment of short result lists | How much irrelevant material is shown? |
| Recall@k | Relevant items retrieved in the first k / all known relevant items | How much judged evidence was found? Label as judged recall when the corpus is not exhaustively assessed. |
| nDCG@10 | A ranking score that rewards highly relevant items near the top, normalized against the ideal judged order | Compare graded relevance; not needed for the first smoke test |
| False entity-link rate | Incorrect accepted identity links / accepted links in the labeled sample | Are aliases merging the wrong assets? Report sample size and unresolved rate too. |
| Evidence coverage | Required evidence items retrieved / required items in the judged case | Did the correction and follow-up reach the answer? |
| Claim support | Supported factual claims / factual claims in reviewed answers | Does the answer say only what its citations support? |
| Freshness lag | Source-change-to-searchable delay, with measurement definition | Is new information discoverable promptly? |
| Task success and time | Can a worker complete the stated task, and how long does it take? | Product usefulness |

Ranked-retrieval metrics and graded relevance are explained in [Stanford's ranking-evaluation chapter](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-ranked-retrieval-results-1.html). Do not compare scores across changing corpora or relevance rules as if they measured the same experiment.

**Tiny arithmetic example:** a judged question has four relevant events. The first five results contain three of them. Precision@5 is 3/5 = 60%; judged Recall@5 is 3/4 = 75%. If the missing fourth event contradicts the proposed answer, the evidence is still insufficient despite a reasonable retrieval score.

## Proposed release gates

These are starting targets to negotiate after a baseline run, **not measured results or promises**.

| Gate | Suggested first criterion |
| --- | --- |
| Access | Zero unauthorized disclosures in the full permission test suite; unresolved access defects block rollout |
| Coverage | Every eligible identity in the pilot snapshot indexed, or explicitly quarantined with a visible reason; reconcile differences before release |
| Known items | At least 95% Hit@5 on the judged known-item slice, with every regression reviewed |
| Identity | Zero false merges in the curated hard-negative suite; report real-sample error and uncertainty separately |
| Relevance | No unexplained material regression against the stable lexical baseline; hybrid must demonstrate a useful gain on its intended query slices |
| Evidence | Required later corrections retrieved for every curated contradiction case |
| Answers | No unsupported critical claim in the reviewed acceptance set; citations resolve and support the adjacent claims |
| Responsiveness | Initial candidate target: p95 search results within 2 seconds and p95 searchable updates within 60 seconds under an agreed test load |
| Recovery | Retry, interruption, reconciliation, and rollback drills pass in an isolated environment |

The latency targets may need revision after measurement. Fast failure messages and partial lexical results are preferable to unexplained waiting. A zero-error test suite is a release requirement, not proof that errors can never occur in production.

## The experiment that decides whether AI helps

Compare **old search → new lexical → lexical plus aliases → hybrid → hybrid plus reranker**, adding one change at a time. Keep the same snapshot and judged queries. Break results down by exact codes, languages, old records, nested text, and historical evidence.

For each change record quality, latency, indexing cost, query cost, and operational burden. Preserve the simpler option if an added component does not materially help. Review actual failures with workers; a small aggregate improvement should not conceal a serious exact-code regression.
