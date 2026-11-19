# What Smart Search should help people do

[Start here](README.md) · [Previous: book summary](01-book-summary.md) · [Next: resources](03-resources-and-metadata.md)

**Proposal:** keep a familiar search box, useful results, and visible scope. Add assistance where it saves interpretation effort. A conversational answer is one possible output, not the definition of the product.

**Book basis:** EPUB §§13, 22, 54–55, 64, 67, 82. **Local basis:** [current search](/Users/maksimklimenko/dev/infl/ai-handoff/07-SEARCH-CURRENT.md), [owner's search direction](/Users/maksimklimenko/dev/infl/ai-handoff/2026-10-14-chatgpt-memory-snapshot/intelliflow-memory-2026-10-14/04-ai-search-direction.md), and [workflow synthesis](/Users/maksimklimenko/dev/infl/ai-handoff/2026-10-14-chatgpt-memory-snapshot/intelliflow-memory-2026-10-14/03-real-world-workflows.md). Findings describe those dated sources; the UX below is proposed.

## Five jobs, five different definitions of a good result

| Job | Example question, invented | Best first response | What would make it misleading? |
| --- | --- | --- | --- |
| Find something remembered | “The PT-12 comment about unstable readings” | Exact or tolerant text results with the matching comment | A vaguely similar sensor taking the exact match's place |
| Learn from a previous incident | “Has this motor tripped after washdown before?” | Comparable incident threads, dates, and reported outcomes | Showing only an early suspicion or treating similarity as shared cause |
| Understand a current record | “What was done, and what is still uncertain?” | Dated evidence summary and recorded state | Treating closure as verified resolution |
| Find a bounded set | “Open safety issues on Line 2” | Structured filters and a list; no text query required | Guessing safety from the legacy field name or hiding exclusions |
| Investigate a count | “How many RCA events were recorded last month?” | Clarify the unit, then an exhaustive structured query if supported | Counting a top-20 semantic result list |

The first two are good entry points for a pilot. Record summaries can follow when history loading is reliable. Accurate aggregation is a separate capability with stricter coverage requirements.

## Keep the good habits people already have

The technical handoff describes substring matching, transliteration, matches inside comments, equipment filters, and active-first ranking as familiar behavior. Preserve and test those capabilities. Intentional ranking changes should be assessed, not slipped into an engine migration.

One visible distinction can resolve conflicting ranking needs:

- **Relevant history:** emphasize the question and comparable evidence; old closed incidents remain competitive.
- **Open issues:** apply the chosen current-state filter and use a suitable activity/priority order.

Start with normal filters or a small sort control. Do not require a worker to select a “retrieval algorithm.” If the system interprets a natural-language question as a filter, show that interpretation and let the user change it.

## A result should explain its usefulness

A synthetic card sketch:

```text
Motor trips after washdown                         Recorded state: closed
Demo Plant / Packaging / Line 2 / Filler
Issue opened: 3 Feb     Matching work entry: 5 Feb

Matched a confirmed spelling variant: MOT 123321
“Repaired the damaged cable connection …”

Reported outcome: production resumed
Later follow-up: preventive verification not found in the retrieved history

Open issue history       Show matching entry
```

The excerpt must be source text. The outcome line is either explicitly sourced extraction or a labeled generated summary. Avoid presenting a generated sentence as a quotation.

“Show matching entry” is a proposed interaction. Verify whether the current route can target a sub-record; if it cannot, open the parent and identify the event by date/key in the UI. Do not invent a deep link and assume it works.

At first, the card can simply show a matching excerpt, its date/type, equipment context, and an “Open history” link. Add outcome summaries only after they pass evaluation.

## Filters should answer understandable questions

| UI label | Meaning to define explicitly |
| --- | --- |
| Facility | Authorized scope; selected explicitly and enforced by the server |
| Equipment/location | Records attached to this node or subtree; distinguish verified asset mentions from location attachment |
| Issue opened | Parent creation date |
| Work or comments recorded | Matching event's recorded date |
| Current state | State of the issue now, not necessarily during the selected historical period |
| Author | Author of the matching entry, or author of the parent; label which |
| Team | Requested help, participation, or author's team; use separate meanings |
| Project | The operational improvement project, distinct from admin groupings of facilities |

Do not expose all these at once. Begin with the existing familiar filters; clarify their labels and add new distinctions only when a real task needs them.

Keep filters visible as removable chips. A query for “pressure sensor last week” might become **Equipment: Filler · Entries recorded: 5–11 October · Query: pressure sensor**, with an editable date range and facility timezone. The date example is illustrative; actual ranges must be computed from the selected plant's calendar, not the server's timezone.

## Broaden deliberately

When results are scarce, offer one change at a time:

1. Include confirmed aliases or spelling variants.
2. Include related wording in other supported languages.
3. Expand from this machine to this line.
4. Expand the date range.

Explain the expanded scope. Never silently search another tenant. “No result on this equipment; 3 potentially related incidents elsewhere on this line” is more useful than silently mixing the lists.

For an ambiguous asset, show the candidate identities with their paths. For a broad symptom, search can proceed and show possibilities. Clarification is most valuable when an incorrect interpretation would materially change the answer.

## Empty, failed, and incomplete are different states

| Situation | Useful message |
| --- | --- |
| Successful search with no matches | “No matches within these filters.” Offer controlled broadening. |
| Search service unavailable | “Search is temporarily unavailable. Your query is saved here; try again.” |
| Lexical works, semantic branch fails | Show lexical results and state that meaning-based matches are unavailable. |
| Index incomplete for the selected scope | Show a concise coverage note; avoid “nothing happened.” |
| An attachment is referenced but unread | “The record references an attachment; its contents were not searched.” |
| Answer generation fails | Keep the retrieved records accessible. |

The handoff reports an indefinite spinner/error-response defect. Fixing that is part of making search dependable, even before improving relevance.

## Add feedback that teaches the system something specific

Start with three optional actions: **Useful result**, **Wrong equipment**, and **Missing a record I know exists**. The last can accept a record link. These correspond to ranking, entity resolution, and coverage problems.

A click alone is weak evidence: people also open bad results to discover that they are bad. Avoid optimizing for click volume or using search activity to rank employees. Store only the diagnostic data needed under an explicit retention and access policy.

## A small user-discovery exercise

Ask a few operators, technicians, and supervisors to bring examples:

1. What was the last record you struggled to find?
2. What words or code did you remember?
3. What did you need to decide after finding it?
4. Which result looked right but turned out to be wrong?
5. What evidence would make you trust a summary?

Collect the question and the intended outcome, not just a proposed UI feature. Convert those examples into the [evaluation set](07-evaluation-and-acceptance.md).
