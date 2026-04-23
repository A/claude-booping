---
name: chat
description: General working mode for project discussion, vault navigation, and small ad-hoc tasks. Opens with a vault status summary. Use for reviewing plans, exploring lessons, casual Q&A, and minor edits that fit within a single session.
argument-hint: [topic or artifact reference]
user-invocable: true
effort: xhigh
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash(booping-plans:*)
  - Bash(ls *)
  - Bash(git status *)
  - Bash(git log *)
  - Bash(git diff *)
  - Bash(cat ~/Claude/*)
  - AskUserQuestion
  - Agent
---

# booping — /chat

General working mode: discussion, vault navigation, and small ad-hoc edits. Opens every session with a live vault status summary.

This skill is **wide-domain** — it must work across very different projects. Project-specific behavior lives in `_booping/skill_chat.md`, lessons, and the vault `CLAUDE.md`. Do not bake stack details into this skill.

## Preflight

- Read and resolve project based on [project resolution principle](../../docs/partial_project_resolution.md).
- Read [plan statuses](../../docs/partial_plan_statuses.md).
- Read [research agents](../../docs/partial_agents_researchers_delegator.md) — delegate heavy reading to researchers to keep context clean.
- Read `~/Claude/{project_name}/CLAUDE.md` — vault and project conventions.
- Read lessons per [read lessons](../../docs/partial_read_lessons.md).
- Read from `~/Claude/{project}/_booping/skill_chat.md`. Silently skip, if file doesn't exist.

## High-level workflow

1. **Orient** (Phase 0) — regenerate `sprints.md`, count plans by status, surface the snapshot in the first message.
2. **Ingest** (Phase 1) — read any artifacts named in `$ARGUMENTS` or surfaced mid-conversation.
3. **Discuss / act** (Phase 2) — answer questions, navigate the vault, make small edits as needed.
4. **Hand-offs** (Phase 3) — route work that has grown beyond chat's scope to the right skill.

---

## Phase 0 Orient

Regenerate the snapshot before the first assistant message:

```bash
booping-plans --format=md > ~/Claude/{project_name}/sprints.md
```

`sprints.md` is chat-owned — `/chat` is its sole writer. Never hand-edit it.

Then count plans by status:

```bash
for s in backlog in-spec ready-for-dev in-progress awaiting-retro awaiting-learning done fail cancelled; do
  printf '%s\t%d\n' "$s" "$(booping-plans --status "$s" 2>/dev/null | tail -n +2 | wc -l)"
done
```

The **first assistant message** must include the resulting 9-row count table. If `backlog >= 5` or `awaiting-retro >= 1`, append a one-line nudge (e.g. "5 plans in backlog — consider a groom session" or "1 plan awaiting retro").

## Phase 1 Ingest

Read artifacts referenced in `$ARGUMENTS` or named during conversation before answering questions about them. When the request spans more than ~3 artifacts, delegate the read to a researcher (`booping-researcher-middle` by default) and have it return a summary, not raw dumps.

## Phase 2 Discuss / act

Answer questions, explore the vault (Glob/Grep inside `~/Claude/{project_name}/`), and make small edits that fit within the current session. When the user refers to something not yet loaded, read it before answering.

You may delegate research to a `booping-researcher-{senior,middle,junior}` agent when you need a summary from files, code, web searches, or docs — see [research agents](../../docs/partial_agents_researchers_delegator.md) for tier selection.

## Phase 3 Hand-offs

Escalate rather than stretch:

- `/groom <topic>` — new work that needs spec, estimation, or a plan file.
- `/develop <plan-path>` — a `ready-for-dev` plan the user wants to implement now. (Path is the plan file, not a backlog directory.)
- `/retro <plan-path>` — a plan just finished (`awaiting-retro`) that needs a retrospective written.
- `/learn <retro-path>` — a retro just written (`awaiting-learning`) that needs lessons extracted.

## What chat does NOT do

- **No plan-status transitions.** Chat owns none. Status changes are manual frontmatter edits made by the appropriate skill.
- **No retrospective writing.** That belongs to `/retro`.
- **No lesson extraction.** That belongs to `/learn`.

## Hard rules

- Never commit, push, or run destructive git operations. User runs those.
- When a task grows beyond ~1 file or needs estimation, escalate to `/groom` rather than expanding in-session scope.
- Never hand-edit `sprints.md` — regenerate it via `booping-plans --format=md` only.
