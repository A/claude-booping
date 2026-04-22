# {{project-name}}

Booping project for {{short description — what the codebase does}}.

Attached repo: `{{repo path}}`.

## Layout

- `Notebook.md` — active scratch pad / draft prompts / open design thinking
- `plans/` — canonical plan files; `/groom` writes here, `/develop`/`/retro`/`/learn` transition state via `booping-plans set`
- `retrospectives/` — sprint retros (`/retro` writes here)
- `lessons/` — extracted rules, always read before `/groom` and `/develop`
- `notes/` — research, user stories, decision logs
- `metrics/` — `lesson-hits.md`, `sp-rollup.md`
- `_booping/` — project-local skill/agent extensions (read at the start of every skill run in this project)
- `sprints.md` — regenerated wholesale by `booping-plans sync-sprints`; do not hand-edit

## Booping commands

- `/chat` — context-aware discussion over the artifacts above
- `/groom` — spec a new feature / bug / refactor into `plans/YYYYMMDD-*.md`; sets initial status via `booping-plans set`
- `/develop <plan-path>` — execute a groomed plan item; transitions status to `in-progress` / `awaiting-retro` via `booping-plans set`
- `/retro <plan-path>` — generate a retrospective; transitions status to terminal via `booping-plans set`
- `/learn <retro-path>` — extract lessons + update skill/agent extensions

## Plan lifecycle

See `docs/plan-schema.md` for the full 9-state status lifecycle and plan frontmatter schema.

## Project-specific notes

{{Anything particular to this codebase — local commands, tech stack, conventions not obvious from the code.}}
