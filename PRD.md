# booping — Product Requirements

## Why a new plugin instead of patching `scrum-*`?

`scrum-*` skills were written for a single-project flat `~/Claude/` layout. They also tolerate the main agent doing work directly (small tasks, quick edits). Two problems we observed:

1. **Multi-project pollution** — working from `aurora-frontend` and `aurora-api` in the same day causes plans/lessons from different products to mix in `~/Claude/plans/`, `~/Claude/lessons/`, and the single `sprints.md`.
2. **Main-context bloat** — the orchestrator sometimes writes code itself ("it's only 1 SP"), which fills the main context with implementation detail and leaves less room for planning.

`booping` addresses both:

- **Per-project scope** — every artifact lives under `~/Claude/{project}/`, selectable per session.
- **Mandatory sub-agent delegation** — the skill orchestrator is forbidden from writing application code in the main context; every task goes to a `booping-*` agent.

## Artifacts

| Artifact | Path | Writer |
|----------|------|--------|
| Plan | `~/Claude/{project}/plans/YYYYMMDD-title.md` | `/groom` |
| Retrospective | `~/Claude/{project}/retrospectives/YYYYMMDD-title.md` | `/retro` |
| Lesson | `~/Claude/{project}/lessons/{N}_{title}.md` (N is incrementing) | `/learn` |
| Skill extension | `~/Claude/{project}/_booping/skill_{name}.md` | `/learn` |
| Agent extension | `~/Claude/{project}/_booping/agent_{name}.md` | `/learn` |
| Sprint log | `~/Claude/{project}/sprints.md` | **`/develop` only** |
| Metrics — lesson hits | `~/Claude/{project}/metrics/lesson-hits.md` | `/develop` (increments) |
| Metrics — SP rollup | `~/Claude/{project}/metrics/sp-rollup.md` | `booping-teamlead` |

## Non-goals

- `/groom` does **not** write to `sprints.md`. A groomed item is a candidate; only executing it via `/develop` creates a sprint row.
- `/develop` does **not** traverse all historical retros — it reads the plan + current `lessons/` only.
- Lessons are not automatically applied by hooks. They are consulted by the responsible skill and tracked in `lesson-hits.md`.

## Agents

Four orchestrators:

- **booping-teamlead** — user-facing. Searches session logs, summarizes, writes `sprints.md`, produces the final retrospective document.
- **booping-techlead** — tech research & feedback. Reads the codebase, identifies patterns, challenges designs.
- **booping-product-manager** — requirements & web research. Validates the "why" and widens the solution space.
- **booping-qa-lead** — testing strategy, QA plan, regression risk.

Four workers (invoked by `/develop`):

- **booping-developer-junior** — developer tasks, 1 SP (haiku).
- **booping-developer-middle** — developer tasks, 2-3 SP (sonnet).
- **booping-developer-senior** — developer tasks, 4 SP (opus); 5 SP refuses.
- **booping-reviewer** — code review pre-merge.

## Project scoping

Resolution order when a skill needs to know the current project:

1. `.booping-project` marker file in CWD or ancestors.
2. Longest-prefix match in `~/Claude/.booping/projects.json` `paths`.
3. Ask the user, then persist the answer (adds an entry to `projects.json` and, if permitted, writes a `.booping-project` marker file in the repo root).

Cross-project parallel sessions are deferred — see `docs/project-scoping.md`.

## Metrics

- `lesson-hits.md` — table of `(lesson_id, title, hits, last_applied_sprint)`. `/develop` and `/groom` append a hit when a lesson is referenced.
- `sp-rollup.md` — per-sprint and rolling monthly story-point totals, maintained by `booping-teamlead` on sprint close.

## Cross-links (shallow)

- Plan `source:` frontmatter → originating chat / issue URL.
- Sprint row → plan path.
- Retrospective `sprint:` frontmatter → sprint row.
- Lesson `retro:` frontmatter → retrospective path.

`/develop` follows: sprint → plan → lessons. It does **not** walk into retros.
`/retro` follows: sprint → plan → code diff.
`/learn` follows: retro → lessons directory (for existing-lesson checks) → skill/agent extensions.
