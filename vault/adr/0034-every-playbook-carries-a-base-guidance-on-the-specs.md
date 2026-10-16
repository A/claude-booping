---
type: adr
title: Every playbook carries a base guidance on the specs
summary: Proposed — every playbook knows what the specs are, the values, and that it reads and writes them through a subagent, applying them where they raise quality; no per-playbook scenarios.
created_by: claude
created_at: 2026-10-16
updated_at: 2026-10-16
status: proposed
values: [value/0016, value/0002, value/0001, value/0012]
issues: []
---

## Context

Specs stay current only if they are maintained during the work and used where they help (value/0016).
Today a playbook knows about them only through rule briefs injected into its steps (rule/0020); only
the specs playbook reads the format guide (adr/0024). So spec material the owner states in passing — a
value before a groom, a usage scenario, a decision — stays in the transcript, and a run that decides
does not know what is already settled. adr/0033 adds a consult at named decision points, but it
depends on a playbook already knowing that specs exist and what they are for. Writing a scenario per
playbook ("groom does X with stories, develop does Y with ADRs") would not cover the next playbook
and would not cover what the owner says outside those scenarios.

## Criteria

- Any playbook, including one written later, works with the specs without a scenario written for it.
- The main context grows by a small fixed block.
- What a playbook writes into the specs is a draft the owner confirms (value/0001).

## Decision

A principle, not a set of scenarios. Every playbook — core, global or project — runs with a base
guidance on the specs:

1. **What it knows.** What the specs are for and what each record type holds (values, rules,
   conflicts, ADRs, stories, ideas, references, runbooks), well enough to recognise spec material in
   its own work and in what the owner says; and the values of the project and global tiers, one line
   each, to orient on without a lookup. It does not hold rules, ADRs or other records.
2. **How it gets it.** Rendered with the project context the playbook skill already renders for every
   run, from the specs format guide and the values' summaries; the size is fixed and checked.
3. **How it works with them.**
   - It applies the specs where they add quality to its result or knowledge of decisions already made,
     and skips them where they add nothing. When it does, it asks a read-only subagent (the consult of
     adr/0033) and keeps only the subagent's bounded answer.
   - It updates them as the work happens: when its work or the owner's words produce spec material —
     a decision, a scenario, a departure from a record, a record the work made untrue — it hands that to
     a subagent that writes a draft or a candidate in the right place and returns a line or two.
   - Values and anything that drops or weakens a rule stay owner drafts; every other draft follows the
     run's autonomy mode (adr/0027).

adr/0033 stays the mechanism for the named decision points; this ADR is the ground every playbook
stands on, including the ones adr/0033 does not name.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [Base guidance for every playbook](#base-guidance-for-every-playbook) | proposed | low | high | Covers every playbook and every unscripted moment at a fixed small cost |
| [Scenarios per playbook](#scenarios-per-playbook) | rejected | medium | high | Covers only what was foreseen, rots as playbooks change |
| [Mine transcripts after the fact](#mine-transcripts-after-the-fact) | rejected | medium | high | Late and lossy; at most a second net in retro |
| [Full registry in every session](#full-registry-in-every-session) | rejected | low | high | Context cost rejected in adr/0033 |

### Base guidance for every playbook

The decision above.

- **Pros:** one mechanism for core, global and project playbooks; the model applies a principle
  instead of matching a scenario; the values steer every run.
- **Cons:** judgement can over-fire (drafts for chatter) or miss; the subagent's draft and the
  owner's confirmation are the filter.
- **Complexity:** low — a rendered block, a capture brief, a size check.
- **Reversibility:** high.

### Scenarios per playbook

Each playbook gets rules telling it which records to read and write at which step.

- **Pros:** precise where foreseen.
- **Cons:** every new playbook needs its own; what the owner says outside a scenario is lost; rules
  multiply.
- **Complexity:** medium.
- **Reversibility:** high.

### Mine transcripts after the fact

A retro or nightly step reads session logs and proposes records.

- **Pros:** catches what a run missed.
- **Cons:** runs after the decisions were made; the context of a sentence is gone.
- **Complexity:** medium.
- **Reversibility:** high.

### Full registry in every session

Every run loads the index or the records.

- **Pros:** no subagent call.
- **Cons:** hundreds of lines per run; rejected in adr/0033.
- **Complexity:** low.
- **Reversibility:** high.

## Consequences

- The playbook skill's project-context render gains the guidance block (format summary, the values,
  the read-and-write principle); a snapshot covers its size.
- The specs playbook's guide step accepts a handed-over piece of spec material and returns a short
  result, so any playbook can use it as the capture subagent.
- A check: run the capture subagent over this conversation (2026-10-16) and compare what it records
  with what the owner said.
