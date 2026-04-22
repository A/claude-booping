---
name: help
description: Show what booping is, the available commands, and how to use them. Use when the user asks for help, wants a tour of the plugin, or is onboarding.
argument-hint: "[topic: skills | agents | layout | workflow]"
user-invocable: true
allowed-tools:
  - Read
  - Bash(ls *)
---

# booping — /help

Orient the user. Do not scaffold, migrate, or write files — that's `/install`'s job.

## Behavior

- With no `$ARGUMENTS`: print the **Quickstart** block below, then ask what they want next.
- With `$ARGUMENTS` in `{skills, agents, layout, workflow}`: print the matching section only.
- Anything else: print the full help document.

## Quickstart

```
booping — per-project grooming/implementation/retro/lessons with mandatory sub-agent delegation

First time in a repo:    /install
Start a discussion:      /chat
Spec new work:           /groom <topic>
Execute a plan:          /develop ~/Claude/<project>/plans/YYYYMMDD-*.md
After a sprint ships:    /retro ~/Claude/<project>/plans/YYYYMMDD-*.md
Extract lessons:         /learn ~/Claude/<project>/retrospectives/YYYYMMDD-*.md
```

Current project resolution: marker file (`.booping-project`) → `~/Claude/.booping/projects.json` → ask.
Artifacts live at `~/Claude/{project}/`. The only writer of `sprints.md` is `/develop`.

## Skills

| Slash | Purpose | Writes |
|-------|---------|--------|
| `/help` | This. | — |
| `/install` | Scaffold a new booping project and/or attach the current repo. | `~/Claude/{project}/*`, `~/Claude/.booping/projects.json`, optional `.booping-project` |
| `/chat` | Read-only discussion over project artifacts. | — |
| `/groom` | Deep-research a feature/bug/refactor into `plans/YYYYMMDD-*.md`. | `plans/`, `metrics/lesson-hits.md` |
| `/develop` | Execute a groomed plan milestone-by-milestone; always delegates to sub-agents. | `sprints.md`, plan progress marks, `metrics/lesson-hits.md` |
| `/retro` | Review what shipped, gather feedback, produce retrospective. | `retrospectives/`, `sprints.md` (`goal` field only) |
| `/learn` | Extract lessons and fold them into `_booping/` extensions. | `lessons/`, `_booping/skill_*.md`, `_booping/agent_*.md` |

## Agents

Orchestrators (always delegated to from skills):

- `booping-teamlead` — user-facing coordination, sprint/metrics writes, draft retrospectives
- `booping-techlead` — codebase research, tech feedback, blast radius
- `booping-product-manager` — requirements validation, business-goal judgement
- `booping-qa-lead` — testing strategy, regression risk

Workers (called from `/develop`):

- `booping-be-dev` — backend (Python/Django/DRF/Rust/Axum/migrations/Temporal)
- `booping-fe-dev` — frontend (React/TypeScript/Leptos)
- `booping-reviewer` — milestone diff review

## Layout

```
~/Claude/
├── .booping/projects.json       # CWD → project mapping
└── {project}/
    ├── plans/                   # /groom output
    ├── retrospectives/          # /retro output
    ├── lessons/                 # /learn output
    ├── metrics/
    │   ├── lesson-hits.md
    │   └── sp-rollup.md
    ├── _booping/                # project-local skill/agent extensions
    ├── CLAUDE.md
    └── sprints.md               # /develop only
```

## Workflow

```
/groom   ──► plans/20260421-foo.md
                │
                ▼
/develop ──► spawns booping-be-dev / booping-fe-dev per task
             spawns booping-reviewer per milestone
             updates sprints.md + plan progress
                │
                ▼
/retro   ──► booping-techlead / -product-manager / -qa-lead in parallel
             booping-teamlead synthesizes → retrospectives/*.md
                │
                ▼
/learn   ──► lessons/{N}_*.md
             optional _booping/skill_*.md, _booping/agent_*.md updates
```

## Hard rules (cross-cutting)

- **Always delegate.** The skill orchestrator never edits application code directly. Even 1-SP tasks go to a worker agent.
- **Lessons are load-bearing.** `/groom` and `/develop` read every file in `lessons/` before acting.
- **`sprints.md` is owned by `/develop`.** `/groom` never touches it; `/retro` only writes the `goal` field.
- **Per-project isolation.** Never read or write outside the current `~/Claude/{project}/` tree.

## See also

- `README.md` — higher-level overview and install instructions
- `PRD.md` — design rationale
- `docs/project-scoping.md` — how project resolution works
