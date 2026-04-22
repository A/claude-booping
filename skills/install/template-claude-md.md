# {{project-name}}

Booping project for {{short description — what the codebase does}}.

Attached repo: `{{repo path}}`.

## Layout

- `Notebook.md` — active scratch pad / draft prompts / open design thinking
- `backlog/` — groomed specs awaiting implementation (`/groom` writes here)
- `retrospectives/` — sprint retros (`/retro` writes here)
- `lessons/` — extracted rules, always read before `/groom` and `/develop`
- `notes/` — research, user stories, decision logs
- `metrics/` — `lesson-hits.md`, `sp-rollup.md`
- `_booping/` — project-local skill/agent extensions (read at the start of every skill run in this project)
- `sprints.md` — sprint registry; **written only by `/develop`**

## Booping commands

- `/chat` — context-aware discussion over the artifacts above
- `/groom` — spec a new feature / bug / refactor into `backlog/YYYYMMDD-*.md`
- `/develop <backlog-path>` — execute a groomed backlog item, updates `sprints.md`
- `/retro <backlog-path>` — generate a retrospective
- `/learn <retro-path>` — extract lessons + update skill/agent extensions

## Sprint registry conventions

- **Status**: `PLANNED` | `IN PROGRESS` | `DONE` | `FAIL`
- **Goal Status**: `SUCCESS` | `PARTIAL` | `FAIL` (set by `/retro`)
- Story points measure scope per Claude Code session (scale 1-5)

## Project-specific notes

{{Anything particular to this codebase — local commands, tech stack, conventions not obvious from the code.}}
