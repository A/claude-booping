---
type: adr
title: The specs playbook is a guide, not a menu of actions
summary: One specs playbook explains every record type and principle plus the user's typical scenarios, and the model works out from the dialogue what to do.
created_by: claude
created_at: 2026-10-15
updated_at: 2026-10-15
status: accepted
values: [value/0002, value/0013, value/0012]
---

## Context

Specs need a user surface: set a tier up, settle values, record decisions, check the
set for internal conflicts, learn from runs. The owner decided on 2026-10-15 that the
user should call one playbook (or just `/playbook`) and the work should follow from
what the user does, and that strong models do better when they understand the
system than when they follow a fixed task list.

## Decision

A single `specs` playbook carries an explanation of every record type and of the
format's principles, plus a set of scenarios the user may be in — for example
alignment (the user wants to refine the project's values), auto-review (check the
specs for internal conflicts), retro (extract lessons so the model does not repeat a
mistake), recording a decision or an idea, syncing specs and code. The model reads
the dialogue and decides what to do; the scenarios orient it, they do not restrict
it. The alignment interview runs only at init, and as a guide for the user to how
specs work: values first, then the boundaries of how the model works follow from
them.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [A guide with scenarios](#a-guide-with-scenarios) | accepted | medium | high | The model decides from the dialogue |
| [A router over fixed actions](#a-router-over-fixed-actions) | rejected | medium | high | Binds the model to a menu |

### A guide with scenarios

One playbook explains the system and lists scenarios; the model chooses.

- **Pros:** follows natural dialogue; uses stronger models better; one entry point.
- **Cons:** less predictable than a fixed path; the guide's quality decides the result.
- **Complexity:** medium.
- **Reversibility:** high.

### A router over fixed actions

A route step maps the request to one of init, align, record, review, sync, work.

- **Pros:** predictable, easy to test per action.
- **Cons:** the model is limited to the menu; a request between actions fits badly.
- **Complexity:** medium.
- **Reversibility:** high.

## Consequences

- When planning, groom names the values in play and flags where the plan departs
  from them, so the user sees what drives a choice and can refine a value
  ([rule/0030](../../specs/rule/0030-planning-shows-values-in-play.md)).
- Confirmation: `/playbook specs` on a repo without specs offers init and the alignment
  guide; on a repo with specs it acts on the user's request without asking which
  action to take.
