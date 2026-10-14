The review table is the single artifact the orchestrator presents to the user before writing any targets. It lists every candidate learning extracted from the retrospective, one row per landing site.

## Column shape

| # | Target | Type | Targets | Brief | Rule | Example |
|---|--------|------|---------|-------|------|---------|
| 1 | `rule/0005-kebab-title.md` | `rule` | `develop/sprint`, `agent:booping-developer` | The one or two lines injected into each target. | One imperative sentence. | One concrete sentence. |
| 2 | `CLAUDE.md` | `claude-md` | — | — | One imperative sentence. | One concrete sentence. |
| 3 | `booping:rule/0003` | `covered` | — | — | One imperative sentence. | One concrete sentence. |
| … | … | … | … | … | … | … |

- `#` — stable integer, assigned once; used by the user to reject individual rows.
- `Target` — where the row lands: `rule/{NNNN}-{slug}.md` relative to the project tier root for a new rule (the number is provisional until write), the existing `rule/NNNN` for an update, `CLAUDE.md`, or the covering ref for a `covered` row.
- `Type` — `rule` for a project rule record, `claude-md` for a bullet in the attached repo's `CLAUDE.md`, `covered` for a candidate an existing core or global rule already covers — shown, never written.
- `Targets` — comma-separated target entries, written verbatim into the rule's `targets:` list, so non-empty for a `rule` row; `—` for `claude-md` and `covered`.
- `Brief` — the one or two lines that will be injected into the targets; `—` for `claude-md` and `covered`.
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
