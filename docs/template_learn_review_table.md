The review table is the single artifact the orchestrator presents to the user before writing any targets. It lists every candidate learning extracted from the retrospective, one row per landing site.

## Column shape

| # | Target | Type | Brief description |
|---|--------|------|-------------------|
| 1 | `lessons/0005_kebab-title.md` | `lesson` | One sentence stating the rule. |
| 2 | `_booping/skill_develop.md` | `skill-ext` | One sentence stating the behaviour change. |
| … | … | … | … |

- `#` — stable integer, assigned once; used by the user to reject individual rows.
- `Target` — exact file path or path-template (e.g. `_booping/skill_<name>.md`). Resolve templates before writing.
- `Type` — sourced from `docs/partial_learn_targets.md`, plus any types activated at runtime by other partials loaded during Preflight.
- `Brief description` — one sentence; imperative form preferred.

## User interaction

Present the table and then ask:

> Accept all, or enter row numbers to reject (e.g. `2 5`):

- **No input / "accept all"**: proceed to write every row.
- **Row numbers**: drop those rows and write the rest.
- **User-added row**: the user may append a row in the same column shape during review. Accept it without prompting again.

## Split rule

If a user-added row's `Brief description` covers two distinct rules, the orchestrator splits it into two rows (assigning the next available `#` values) before any write. Never write a single row that conflates two rules.
