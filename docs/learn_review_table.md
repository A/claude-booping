The review table is the single artifact the orchestrator presents to the user before writing any targets. It lists every candidate learning extracted from the retrospective, one row per landing site.

## Column shape

| # | Target | Type | Rule | Example |
|---|--------|------|------|---------|
| 1 | `lessons/0005_kebab-title.md` | `lesson` | One imperative sentence. | One concrete sentence. |
| 2 | `_booping/skill_develop.md` | `skill-ext` | One imperative sentence. | One concrete sentence. |
| … | … | … | … | … |

- `#` — stable integer, assigned once; used by the user to reject individual rows.
- `Target` — exact file path or path-template (e.g. `_booping/skill_<name>.md`). Resolve templates before writing.
- `Type` — one of the target types from the Routing Matrix inlined in the skill body.
- `Rule` — one sentence, imperative form (`do X` / `don't Y`). Single concern — if you need "and", "plus", or `;`, decompose into two rows.
- `Example` — one sentence, concrete; what went wrong or right.

## User interaction

Present the table and then ask:

> Accept all, or enter row numbers to reject (e.g. `2 5`):

- **No input / "accept all"**: proceed to write every row.
- **Row numbers**: drop those rows and write the rest.
- **User-added row**: the user may append a row in the same column shape during review. Accept it without prompting again.

## Split rule

If a user-added row's `Rule` cell carries two distinct rules, split into two rows (assigning the next available `#` values) before any write. The `Example` cell should illustrate exactly the rule in its row. Never write a single row that conflates two rules.