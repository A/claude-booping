---
type: adr
title: A session in a booping project starts pointed at the playbooks
summary: In a project with a .booping marker a SessionStart hook injects when to
  use playbooks and the rendered playbook table; the agent offers the fitting 
  one, the manager by default.
created_by: claude
created_at: 2026-10-19
updated_at: 2026-10-19
status: superseded
values: [value/0009, value/0008, value/0013, value/0016, value/0002]
rules: []
issues: []
review: accepted
review_evidence: «Давай opus сразу… В остальном, да, все правильно» — 
  2026-10-19, chat (plan + ADR briefs)
---

## Context

Core rules [booping:rule/0032](../../specs/rule/0032-approval-asked-in-prose.md) and [booping:rule/0033](../../specs/rule/0033-decisions-listed-for-acceptance.md) and the specs guidance reach an agent only through a rendered playbook, agent or skill body. A session that works on a project outside any playbook never sees them. On 2026-10-18 a session in another booping project wrote two ADRs as accepted and dispatched developers without showing the owner the decision, its alternatives or the ADR it partly reversed; it saw the `/playbook` skill in its list and did not load it. The same day a session in this repo proposed a new record status without checking the existing `reviewed` field. Building nothing lets both errors repeat. The plugin ships no hook today.

## Criteria

- A session doing project work a playbook fits learns that it should go through it, before it takes decisions.
- Nothing changes outside booping projects.
- The playbook list is rendered from the source the `/playbook` skill already uses, never restated ([value/0003](../value/0003-single-source.md)).

## Decision

The plugin ships a `SessionStart` hook. When no `.booping` marker is found it injects nothing. When one is found it injects:

1. a short prose block on when to call a playbook — project work a playbook fits goes through it;
2. the rendered playbook table, from the same source as the `/playbook` skill.

The agent offers the fitting playbook in the dialogue; when nothing narrower fits, the project-manager is the default offer (owner, 2026-10-19). Loading a playbook brings its rules with it, so the core rules reach the session the way they reach a run.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [SessionStart hook in booping projects](#sessionstart-hook-in-booping-projects) | accepted | low | high | Tells every session in a booping project where its work belongs, before any decision |
| [Triggers in the skill description only](#triggers-in-the-skill-description-only) | rejected | low | high | Already failed: the session saw the skill and did not load it |
| [Load the project-manager on every session start](#load-the-project-manager-on-every-session-start) | rejected | low | high | Every message would go through intake into items and gates, debugging and questions included |
| [A narrower hook: prompt topic or spec writes](#a-narrower-hook-prompt-topic-or-spec-writes) | rejected | medium | high | Keyword matching is fragile; a write hook fires after the decision is taken |

### SessionStart hook in booping projects

The decision above.

- **Pros:** reaches every session in a booping project, including one that never thinks of `/playbook`; silent everywhere else; the table is rendered from the existing source; the agent still chooses in dialogue, so a debugging question is not forced into a playbook.
- **Cons:** about 2–3 KB of context in every session of a booping project, used or not — a departure from [value/0002](../value/0002-minimal-effective-context.md); the first hook the plugin ships, a new surface to maintain and test; an offer can still be ignored.
- **Complexity:** low.
- **Reversibility:** high.

### Triggers in the skill description only

Sharpen the `/playbook` skill description so the model loads it when project work starts.

- **Pros:** nothing to build; no context cost beyond the skill list.
- **Cons:** prose in the description already failed on 2026-10-18 — the session saw the skill and did not load it.
- **Complexity:** low.
- **Reversibility:** high.

### Load the project-manager on every session start

The hook loads the manager playbook itself, so every session is the manager.

- **Pros:** the strongest guarantee that project work goes through the playbooks.
- **Cons:** every message — a debugging session, a question — goes through intake into items and gates; a project that wants it can say so in its own `CLAUDE.md`.
- **Complexity:** low.
- **Reversibility:** high.

Rejected by the owner on 2026-10-19 with the plan: a project that wants the manager at start says so in its CLAUDE.md.

### A narrower hook: prompt topic or spec writes

A `UserPromptSubmit` hook matching the prompt's topic to a playbook, or a `PreToolUse` hook on writes into a specs tier.

- **Pros:** context only when it seems relevant.
- **Cons:** keyword matching is fragile; a write hook fires after the decision is already taken, too late to show the owner anything.
- **Complexity:** medium.
- **Reversibility:** high.

## Consequences

- The plugin gains its first hook; its output must be reproducible and covered like any render ([rule/0027](../rule/0027-renders-reproducible.md)).
- Every session in a booping project carries the injected block — a recorded departure from [value/0002](../value/0002-minimal-effective-context.md), paid for [value/0016](../value/0016-specs-live-with-the-work.md) and [value/0013](../value/0013-guides-to-the-goal.md).
- The injected block is the two-column table, Playbook | Trigger — about 3 KB on this repo (plan 202610190033, decision 16).
