---
name: chat
description: Context-aware discussion over plans, retros, and lessons without writing files unless explicitly asked. Use for reviewing plans, discussing open specs, or exploring prior retros/lessons for the current project.
argument-hint: [topic or artifact reference]
user-invocable: true
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(ls *)
  - Bash(cat ~/Claude/*)
  - Bash(git status *)
  - Bash(git log *)
  - Bash(git diff *)
  - AskUserQuestion
  - Agent
effort: xhigh
---

# booping — /chat

Discussion mode over project artifacts. Read-only by default.

## Project resolution

Follow [docs/project-scoping.md](../../docs/project-scoping.md). Briefly: marker file → `projects.json` → ask. Persist on first-ask.

## Read-before-first-reply

Always read (in parallel) before the first assistant message:

- `~/Claude/{project}/CLAUDE.md` — vault/project instructions
- `<attached-repo>/CLAUDE.md` — in-repo code conventions (path from `projects.json` `cwd`; skip if file doesn't exist)
- `~/Claude/{project}/sprints.md` — active sprints
- `~/Claude/{project}/_booping/skill_chat.md` — project-local behavior overrides (if exists)

If `$ARGUMENTS` references an artifact (`plans/...`, `retrospectives/...`, `lessons/...`), read it too.

## Behavior

- Respond based on the artifacts you have read. If the user refers to something not yet loaded, read it before answering.
- When the user asks for exploration ("what's in the plans?", "which lessons touch testing?"), use Glob/Grep inside the project directory only.
- Do **not** write or edit files in `/chat`. If the conversation produces actionable changes, offer to hand off: "Run `/groom` to spec this" or "Run `/learn` on retro X to capture this as a lesson."
- Delegate heavy reading or cross-referencing to sub-agents when the request spans more than ~3 artifacts, keeping the main context tight.

## Hand-offs

- Actionable new work → suggest `/groom <topic>`
- Ready to implement existing backlog → suggest `/develop <backlog-path>`
- Sprint just finished → suggest `/retro <backlog-path>`
- Retro just written → suggest `/learn <retro-path>`

## Hard rules

- Never touch files outside `~/Claude/{project}/` in this skill.
- Never update `sprints.md` — that's `/develop`'s responsibility only.

For the status enum and lifecycle definitions, see [docs/plan-schema.md](../../docs/plan-schema.md).
