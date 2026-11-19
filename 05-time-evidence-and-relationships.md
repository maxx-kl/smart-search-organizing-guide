# Preserve time, evidence, and the meaning of links

[Start here](README.md) · [Previous: aliases](04-assets-aliases-and-languages.md) · [Next: architecture](06-search-architecture.md)

**Proposal:** Smart Search should help users reconstruct what was reported, when it was known, and what remains uncertain. It should not turn a collection of notes into a falsely tidy repair story.

**Book basis:** EPUB §29, “Resources over Time”; §§37–43, relationships; §67, contextual relevance. **Local basis:** workflow synthesis (`ai-handoff/2026-10-14-chatgpt-memory-snapshot/intelliflow-memory-2026-10-14/03-real-world-workflows.md`), data model (`ai-handoff/04-DATA-MODEL.md`), and the 15 October HSE report (`ai-handoff/2026-10-15-telegram-hse-coordination/executive-report.md`). The latter reports that closure, archival, continuing work, and reported physical resolution can diverge. The examples below are invented.

## Four clocks that should not be confused

| Time | Meaning | What to do when unavailable |
| --- | --- | --- |
| Occurrence time | When the physical event reportedly happened | Keep unknown, or retain the source's approximate wording |
| Recorded time | When the entry was written | Preserve the stored value and source clock; do not call it exact physical event time |
| State/activity time | When the relevant recorded state changed or substantive activity occurred | Derive from explicit events using a documented rule |
| Index time | When the search system processed the source | Use for freshness monitoring, never as the incident date |

**Example:** work happens Monday, is entered Tuesday, and is indexed Wednesday. A question about “work recorded Tuesday” can be answered from the entry timestamp. A question about “work physically done Monday” needs evidence of that occurrence date.

The handoff also notes different timestamp units across sources. Normalize deliberately at the boundary and retain origin. Facility shifts and calendar ranges use the facility timezone; a date range should use a defined start-inclusive/end-exclusive interval to avoid boundary errors.

## Historical view and current history are different questions

```text
Monday       Issue opened; cause suspected
Tuesday      A test does not support that cause
Wednesday    Repair reported; operation resumes
Friday       Issue closed
Next month   Similar symptom returns; issue reopened
```

- “What was known by Tuesday evening?” includes Monday and Tuesday evidence only.
- “What do we now know about Monday's issue?” can include the later work and recurrence.
- “Is the issue currently open?” uses current authorized state.

**Important limitation:** filtering visible events by date is not enough to recreate a historical system state if metadata was overwritten or historical versions were never retained. An MVP can offer an **event-bounded narrative** with that limitation. A full “as known at the time” view needs reliable historical state, including when information was entered and later corrected.

Do not silently attach today's equipment name, project, checklist status, or generated summary to a historical answer as if it were known then. Label current context as current, or omit it from the historical claim.

## Use evidence categories as reading aids

A modest proposed vocabulary:

| Category | Example | What it does not establish |
| --- | --- | --- |
| Observation | “Motor stopped after cleaning.” | A cause |
| Hypothesis | “Possibly moisture at the connector.” | A diagnosis |
| Diagnostic check | “Inspected connector; moisture not seen.” | Proof moisture was never present |
| Planned action | “Inspect cable next shift.” | Completed work |
| Reported work | “Replaced damaged cable section.” | A verified outcome |
| Reported check/outcome | “Ran through the shift without a repeat trip.” | Permanent prevention |
| Recorded state change | “Closed.” | Physical hazard eliminated |
| Later correction or contradiction | “Fault recurred.” | That all earlier work was useless |

These labels describe assertions in records. They are not claims of independent field verification. Keep original wording available and permit “unclear/mixed” rather than forcing every passage into a confident class.

## Retrieve counterevidence, not just supporting passages

Once a candidate incident is found, load its relevant chronology. Include later close/reopen events, corrections, and explicit links that materially affect interpretation. A matching early hypothesis may be contradicted by a later comment that shares none of the query words.

This expansion must be bounded and permission-checked. If a long history exceeds the available context, select evidence deliberately and disclose omissions. Useful signals include the matching event, nearby context, explicit replies, state transitions, and later corrections. Do not assume “the last event” always contains the final truth.

For a historical cutoff, expansion must respect the cutoff. Do not use a whole-thread present-day AI summary as evidence about an earlier moment.

## Give relationships a direction and a status

| Relationship | Example | Retrieval consequence |
| --- | --- | --- |
| `work-on` | Event → parent issue | Read event in its incident context |
| `projection-of` | Shift work entry → canonical work event | Avoid double-counting |
| `explicitly-linked-to` | Source link → another record | Follow the reference without assuming its meaning |
| `duplicate-of` | Record → master record, when explicitly supported | Inspect continuing work on the master |
| `part-of` / `drives` | Component → assembly / motor → pump | Broaden context without merging identities |
| `possibly-similar-to` | Incident → candidate incident | Suggest comparison; do not assert shared cause |
| `corrects` / `contradicts` | Later assertion → earlier assertion | Present both with chronology and source |

Existing structural links can be imported directly. Their semantic meaning may require reading the associated text. Inferred relations should carry status and evidence. No relation should widen tenant permissions.

## Provenance is traceability, not automatic truth

A source pointer tells us where a claim came from. It does not prove that the author was correct, that an observation was complete, or that identity metadata was tamper-proof. The handoff's security review specifically leaves deployed access controls unverified.

For each important answer claim, retain the source record/event, text field, timestamp, retrieval time, and the processing version used. The [W3C PROV Primer](https://www.w3.org/TR/prov-primer/) offers a useful distinction among entities, activities, and agents. Here that can mean a source entry, the extraction that derived a summary, and the software or person responsible. Adopting that thinking does not require a full PROV implementation.

## A practical answer contract for Ina

A proposed answer has four parts:

1. **Scope:** selected facility/equipment, period, and sources searched.
2. **Finding:** concise statements, each tied to the relevant source entry.
3. **Chronology and qualifications:** failed checks, temporary outcomes, later corrections, and current recorded state where relevant.
4. **Limits:** missing attachments, unsearched source types, incomplete history, unresolved identity, or insufficient evidence.

A synthetic answer:

> The retrieved history reports a cable repair on 5 February, followed by a successful operating check. The earlier overheating hypothesis was not supported by the recorded temperature check. The issue is currently marked closed, but I did not find a recorded preventive verification in the retrieved history. The record references a photograph whose contents were not examined.

In a product, the first three factual sentences need event-level source links. This example has no live citations because its evidence is invented; see [the complete synthetic evidence table](09-worked-examples.md).

Historical work reports should be presented as history. To answer “what should I do now?” with an approved procedure, the system needs an authorized, applicable procedure source and version; a past workaround alone is insufficient.
