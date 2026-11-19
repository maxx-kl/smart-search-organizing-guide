# Worked examples: what the principles change

[Start here](README.md) · [Previous: delivery plan](08-delivery-plan.md) · [Next: reading and sources](10-reading-and-sources.md)

**Every record, person, asset, date, and result in this chapter is invented.** These examples illustrate proposed behavior; no search engine or model was run against them. They can seed synthetic tests after being converted into fixtures.

## Example 1 — Find a past repair without repeating an old hypothesis

A technician asks:

> “What happened with MOT 123321 after washdown? Did overheating cause it?”

### The available evidence

All times below are shown in the fictional facility's local time, with the same timezone used consistently for the example.

| Source | Date | Stored meaning |
| --- | --- | --- |
| P17, initial problem | 3 February | `МОТ123321` trips after washdown; overheating suspected |
| E1, diagnostic comment under P17 | 4 February | Temperature check did not confirm overheating; intermittent trip remains |
| E2, work entry under P17 | 5 February | Damaged cable connection repaired; operation resumed |
| W2, linked shift work entry | 5 February | A second projection of E2, explicitly linked by event identity |
| E3, closing event | 6 February | Closed after a reported successful operating check |
| P22, separate problem on another line | 10 February | Pump `123321` has low output; no verified identity link to the motor |
| A1, attachment reference under P17 | 5 February | Photograph referenced; contents unavailable to the retrieval system |

The alias register has a **confirmed, facility- and line-scoped** mapping between `MOT 123321` and `МОТ123321`. It has no mapping equating the motor with P22's pump.

### How retrieval should proceed

1. Authenticate the technician and establish the authorized facility and selected line.
2. Search the literal code and its confirmed alias. Keep any broader candidates separate.
3. Retrieve P17 and the matching entries. Load its relevant history, including E1, E2, and E3.
4. Recognize W2 as another projection of E2, so it does not become a second repair.
5. Keep P22 out of the exact-asset answer. It can be a separate candidate only if the user broadens scope.
6. Preserve the attachment limitation.

### A useful proposed answer

> The retrieved record does not confirm overheating. The 4 February temperature check left that hypothesis unsupported [E1]. A later entry reports repairing a damaged cable connection and resuming operation [E2]. The issue was marked closed after a reported operating check [E3]. The photograph referenced with the repair was not available for review [A1].

The bracket labels refer to the synthetic table above, not real clickable record URLs. A product implementation should resolve citations to authorized source entries.

Notice what this answer avoids: it does not say “overheating was impossible,” “the cable was definitively the root cause,” or “the repair was permanent.” Those claims are stronger than the provided evidence.

### Which book ideas did the work?

- **Naming and identity:** the alias finds the motor; shared digits do not merge the pump.
- **Resource granularity:** match an event, explain a thread.
- **Relationships:** E2 and W2 are two projections of one event.
- **Provenance and time:** the negative check precedes the reported repair.
- **Collection scope:** an attachment reference is distinguished from examined content.

## Example 2 — The same history, a different question

Now ask:

> “What did the team know by the end of 4 February?”

E2 and E3 are later than the cutoff. They must not appear as information available by that date.

A useful proposed answer:

> By the end of 4 February, the record described trips after washdown and a temperature check that did not confirm overheating. The retrieved entries up to that cutoff did not yet report a completed repair [P17, E1]. This is an event-bounded account; it does not reconstruct overwritten metadata or unrecorded conversations.

If the current equipment path or record state is displayed alongside the answer, label it **current context**. A present-day “closed” badge is not the historical status.

**Design consequence:** an embedding or generated summary that includes the entire later history must not become evidence for the cutoff answer. The system may use a broad index to locate the thread, but historical evidence selection must happen against appropriately dated source content.

## Example 3 — Closed as duplicate does not mean completed

Suppose a new synthetic record D9 says “Guarding concern on conveyor.” It is closed with “Duplicate; follow master issue M4.” M4 remains active and contains a planned action plus partial work.

Question:

> “Was this concern resolved?”

A result showing only D9's closed badge would be misleading. A useful response is:

> D9 was closed as a duplicate and points to M4. The linked master remains recorded as active. Its retrieved history reports partial work, but does not establish completion.

This requires an explicit source-supported duplicate link and access to M4. If the user cannot access M4, the system should not leak its state or contents. It can explain that the visible record refers to additional evidence that is not available within the user's access.

**Book connection:** relationship type changes the meaning of closure. An ordinary untyped link alone would not establish “duplicate of.”

## Example 4 — Counting repairs requires a definition

Using Example 1, someone asks:

> “How many repairs were recorded for this motor in February?”

Potential answers differ by unit:

| Unit | Count in the tiny synthetic dataset | Meaning |
| --- | --- | --- |
| Parent problem records about the motor | 1 | P17 |
| Source appearances of the repair work | 2 | E2 and W2 |
| Distinct repair-work events | 1 | E2 after projection deduplication |
| Independently verified physical repairs | Unknown | The dataset contains reports, not an independent audit |

The assistant should clarify or state the counting rule, search the complete scoped dataset through an appropriate structured path, and report exclusions. It should not count however many candidates happened to arrive in a ranked top-k list.

If only search-result retrieval is implemented, a truthful answer is: “I found one distinct reported repair event in the retrieved records; this search does not establish the total for February.”

## Example 5 — Browsing without knowing the right words

A supervisor wants:

> “Open safety issues on Line 2.”

This is primarily a structured retrieval task. The proposed interpretation is:

```text
Facility: Demo Plant
Location subtree: Line 2
Current record state: active problem
Safety classification: validated source mapping
Text query: none
```

Show the applied scope and list matching records. Use the correct source interpretation: the handoff reports that the legacy `nearMiss` boolean can mean the broader H&S category, not only the narrower near-miss subtype.

Facets let the user refine by period, project, or other verified dimensions. They should not have to guess the wording used by each author. An LLM is optional for translating the question into proposed filters; the backend validates and executes them.

## Example 6 — “No match” is not “never happened”

A query finds no result for a component in an old date range. The pilot index has a known coverage gap, and photos have not been ingested.

A useful message is:

> No matches were found in the indexed record text for this equipment and period. Coverage for part of the selected period is incomplete, and attachment contents were not searched. Try a broader location or spelling variant, or open the journal directly.

Once coverage is complete, the wording can become simpler, but absence from recorded evidence still does not establish absence in the physical world.

The distinction matters operationally: a user should know whether to change the query, inspect another source, or wait for a service repair.
