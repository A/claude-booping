---
name: help
description: Show what booping is, the available commands, and how to use them. Use when the user asks for help, wants a tour of the plugin, or is onboarding.
argument-hint: "[topic: skills | agents | layout | workflow | extensions]"
user-invocable: true
effort: low
allowed-tools:
  - Read
  - Bash(ls *)
  - Bash(bin/booping-commands:*)
  - Bash(bin/booping-skills:*)
  - Bash(bin/booping-agents:*)
  - Bash(bin/booping-workflow:*)
  - Bash(bin/booping-project-name:*)
  - Bash(bin/booping-extra-instructions:*)
---

# booping — /help

Orient the user to the booping plugin. This skill is read-only — it never scaffolds, migrates, or writes files. That is `/install`'s job.

## Project Context

!`${CLAUDE_PLUGIN_ROOT}/bin/booping-project-name`

On skill load, report the resolved project context back to the user verbatim so they can see which project and vault the skill is operating on.


## High-level workflow

1. Dispatch topic based on `$ARGUMENTS`.
2. Render body.

## Phase 0 — Dispatch topic

Decide which body section(s) to print based on `$ARGUMENTS`:

- `skills`, `agents`, `layout`, `workflow`, `extensions` → print the matching section only.
- Empty or anything else → print the full body (Commands → Skills → Agents → Layout → Workflow → Extensions → Hard rules → See also).

## Phase 1 — Render body

Print the section(s) chosen in Phase 0 verbatim, in the order listed above.

!`${CLAUDE_PLUGIN_ROOT}/bin/booping-commands`

!`${CLAUDE_PLUGIN_ROOT}/bin/booping-skills`

!`${CLAUDE_PLUGIN_ROOT}/bin/booping-agents`

## Layout

```
~/Claude/
└── {project}/
    ├── plans/                   # /groom output
    ├── retrospectives/          # /retro output
    ├── lessons/                 # /learn output
    ├── notes/                   # your notes — plan reviews, code-review threads, ideas (not used in generation)
    ├── _booping/                # project-local skill/agent extensions
    └── sprints.md               # regenerated on every plan transition
```

!`${CLAUDE_PLUGIN_ROOT}/bin/booping-workflow`

## Extensions

Project-specific guidance and accumulated knowledge layer onto skills and agents at runtime:

- **Lessons** — `~/Claude/{project}/lessons/*.md`. Authored by `/learn` after retrospectives; inlined into every skill at load via `!`${CLAUDE_PLUGIN_ROOT}/bin/booping-lessons``.
- **Skill overrides** — `~/Claude/{project}/_booping/skill_<name>.md`. Inlined into the matching skill at load via `!`${CLAUDE_PLUGIN_ROOT}/bin/booping-extra-instructions skill_<name>.md``.
- **Agent overrides** — `~/Claude/{project}/_booping/agent_booping-<name>.md`. Inlined into the matching agent at load via `!`${CLAUDE_PLUGIN_ROOT}/bin/booping-extra-instructions agent_booping-<name>.md``.

## Hard rules

- **`/help` never writes files.** If the user needs scaffolding, hand off to `/install`.

## See also

- `README.md` — higher-level overview.

!`${CLAUDE_PLUGIN_ROOT}/bin/booping-extra-instructions skill_help.md`
