---
type: adr
title: Every session carries a specs primer and the values
summary: Proposed — a booping session starts with a short guide to recognise spec material in conversation and the values' one-line summaries; capture and lookup go through a subagent, rules and ADRs stay out.
created_by: claude
created_at: 2026-10-16
updated_at: 2026-10-16
status: proposed
values: [value/0002, value/0001, value/0008]
issues: []
---

## Context

The owner states spec material in passing, in any playbook: a value before a groom ("small tasks must
reach development fast"), a usage scenario ("I review specs on my phone"), a decision ("keep the
colon refs"). Nothing in a session knows that such a sentence belongs in `value/`, `story/` or `adr/`;
it stays in the transcript. No record decides how stories are collected from conversation; retro
mines session logs only for corrections and issues, and the corrections log (adr/0026) holds
corrections, not needs. adr/0033 brings the specs in at decision points through a subagent, but a
session that does not recognise spec material never asks. Only the specs playbook reads the format
guide (adr/0024).

## Criteria

- A session recognises spec material when the owner says it, in any playbook.
- The main context grows by a short fixed block, not by the registry.
- What gets written is a draft the owner confirms (value/0001).

## Decision

1. **Specs primer.** Every booping session gets, with the project context the playbook skill already
   renders, a guide of about ten lines: what each record type is and the cue that marks it in
   conversation (why the project exists → value; "always / never" → rule; a choice between options →
   adr; "I want … so that …", a usage scenario → story; "what if" → idea), and one instruction: spec
   work goes through a subagent.
2. **Values in context.** The same block lists every value of the project tier (and the global tier)
   as its title and summary, one line each, so the session orients on them without a lookup.
3. **Capture through a subagent.** When the session hears spec material it hands the sentence and its
   context to a subagent (the specs playbook's guide step) that finds related records and writes a
   draft or a candidate; the session gets back two lines (what was written, what needs the owner).
   Values and anything that drops or weakens a rule stay owner-only drafts.
4. Rules, ADRs, stories and references do not enter the session; they come through the consult of
   adr/0033 when a decision needs them.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [Primer and values, capture by subagent](#primer-and-values-capture-by-subagent) | proposed | low | high | Recognises spec material at a fixed small cost |
| [Mine transcripts after the fact](#mine-transcripts-after-the-fact) | rejected | medium | high | Late and lossy; useful only as a second net in retro |
| [Full registry in the session](#full-registry-in-the-session) | rejected | low | high | Hundreds of lines in every session (adr/0033) |
| [Nothing until the specs playbook runs](#nothing-until-the-specs-playbook-runs) | rejected | low | high | Today's state: spec material stays in chat |

### Primer and values, capture by subagent

The decision above.

- **Pros:** the cue list is enough to notice spec material; values steer every session; capture costs
  one subagent call when it happens.
- **Cons:** the cue list can over-fire; a session may hand off chatter. The subagent's draft, not the
  session, decides whether a record is due.
- **Complexity:** low — a rendered block and the capture brief.
- **Reversibility:** high.

### Mine transcripts after the fact

A retro or nightly step reads session logs and proposes stories and values.

- **Pros:** catches what the session missed.
- **Cons:** runs after the decisions were already made; context of the sentence is gone; extra cost on
  every transcript.
- **Complexity:** medium.
- **Reversibility:** high.

### Full registry in the session

Every session loads the index or the records.

- **Pros:** no subagent call.
- **Cons:** rejected in adr/0033 for context cost and mid-task relevance judgement.
- **Complexity:** low.
- **Reversibility:** high.

### Nothing until the specs playbook runs

Spec material is recorded only when the owner starts the specs playbook.

- **Pros:** no work.
- **Cons:** the owner has to remember and restate it later.
- **Complexity:** low.
- **Reversibility:** high.

## Consequences

- The playbook skill's project-context render gains the primer and the values block; their size is
  covered by a snapshot.
- The specs playbook's guide step takes a captured sentence as input and returns a two-line result.
- A cheap check: run the capture subagent over this conversation's transcript (2026-10-16) and count
  the stories and values it finds against what the owner actually said.
