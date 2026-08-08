# docs — States

One machine, `run` — a **procedure tracker**. It tracks the run; the spec set and the destination
documents keep their own lives across runs and none of their statuses belong here. The run record
is runtime-named (`{YYYYMMDDHHmm}-{title}.md`), so the machine declares no `artifact:` and is
addressed with `--target`; the workdir is `{vault}/docs/`, the anchor every hook file target
resolves against.

The `update` subgraph gets **no machine of its own**: none of its inner steps holds a review gate,
and the confirmed targeting plan already carries one row per destination document — per-row
progress (pending → written → compacted → verified) is a column on that table in the run record
body, resumed from `updating`, the way `develop` resumes its milestone loop from plan-body
checkboxes. A per-instance machine would need one status file per destination, and a destination
document cannot carry frontmatter.

### run

`artifact:` none declared — `--target {vault}/docs/{YYYYMMDDHHmm}-{title}.md`, `--workdir {vault}/docs`

| Superstate | States |
| --- | --- |
| `spec-set` | `surveying`, `awaiting-scope-confirm`, `briefing`, `awaiting-briefing-confirm`, `spec-building`, `awaiting-roles-targets-confirm`, `awaiting-features-confirm` |
| `change-set` | `researching`, `awaiting-changes-confirm`, `syncing-specs`, `targeting`, `awaiting-targeting-confirm` |
| `producing` | `updating`, `writing-changelog`, `recording` |
| terminal | `done`ᵗ, `cancelled`ᵗ |

| State | To | When | Gates | Hooks |
| --- | --- | --- | --- | --- |
| `none` | `surveying` | the playbook is invoked on a project whose documentation may have drifted | | |
| `surveying` | `awaiting-scope-confirm` | survey opened the run record with the spec-set state and the undocumented set | | `frontmatter-update started="{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"`, `frontmatter-update commit="{{ macro('core.macros.git_commit') }}"` |
| `awaiting-scope-confirm` | `surveying` | the user's scope answer needs a fresh survey — a different item range, or spec files the survey did not inspect | | |
| `awaiting-scope-confirm` | `briefing` | the user settled which spec files to refresh and which delivered items to cover, and at least one spec file needs work | explicit user confirmation captured — silence never counts | `frontmatter-update scope_reviewed_at="{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"` |
| `awaiting-scope-confirm` | `researching` | the user settled the scope and every spec file is present and current — the spec waves are skipped | explicit user confirmation captured; the survey found no missing or incomplete spec file | `frontmatter-update scope_reviewed_at="{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"`, `script commit-docs` |
| `awaiting-scope-confirm` | `done` | the survey found nothing to do — spec set current, undocumented set empty — and the user closed the run | explicit user confirmation captured; the undocumented set is empty | `frontmatter-update scope_reviewed_at="{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"`, `frontmatter-update completed="{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"`, `script commit-docs` |
| `briefing` | `awaiting-briefing-confirm` | briefing wrote `_specs/index.md`, naming any vision shift against the previous one | | |
| `awaiting-briefing-confirm` | `briefing` | the user reworks the briefing — what the project is, who it serves, where it is heading | | |
| `awaiting-briefing-confirm` | `spec-building` | the user confirms the briefing | explicit user confirmation captured — a vision shift is acknowledged in the answer, silence never counts | `frontmatter-update _specs/index.md reviewed_at="{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"` |
| `spec-building` | `awaiting-roles-targets-confirm` | roles, targets and feature-index each wrote their file | | |
| `awaiting-roles-targets-confirm` | `spec-building` | the user wants roles or surfaces refined | | |
| `awaiting-roles-targets-confirm` | `awaiting-features-confirm` | the user confirms roles and surfaces, presented together | explicit user confirmation captured — silence never counts | `frontmatter-update _specs/roles.md reviewed_at="{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"`, `frontmatter-update _specs/targets.md reviewed_at="{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"` |
| `awaiting-features-confirm` | `spec-building` | the user wants features, capabilities or groups refined | | |
| `awaiting-features-confirm` | `researching` | the user confirms the feature index | explicit user confirmation captured | `frontmatter-update _specs/features.md reviewed_at="{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"`, `script commit-docs` |
| `researching` | `awaiting-changes-confirm` | the per-item sub-agents returned and the typed change table is posted in chat | every in-scope delivered item carries a row, each typed | |
| `awaiting-changes-confirm` | `researching` | the user adds items that still have to be read | | |
| `awaiting-changes-confirm` | `syncing-specs` | the user confirms the change table, extensions and refinements folded in | explicit user confirmation captured — silence never counts | `frontmatter-update changes_reviewed_at="{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"` |
| `syncing-specs` | `targeting` | sync-specs folded the confirmed table into briefing, roles, surfaces and feature index | | |
| `targeting` | `awaiting-targeting-confirm` | targeting wrote the role × surface plan to the run record | one row per destination document, no two rows naming the same file | |
| `awaiting-targeting-confirm` | `targeting` | the user reworks rows — a destination, its assigned changes, or what each must say | | |
| `awaiting-targeting-confirm` | `updating` | the user confirms the targeting plan — this gate always fires | explicit user confirmation captured — silence never counts | `frontmatter-update targeting_reviewed_at="{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"`, `script commit-docs` |
| `updating` | `writing-changelog` | every targeting-plan row left the loop | each row's progress column reads verified, or dropped with its reason | |
| `writing-changelog` | `recording` | the run's entry is written to the repo's `CHANGELOG.md`, seeded if it was absent | | |
| `recording` | `done` | record closed the run record — what landed where — and listed the work items now documented | the run record's `documented:` list names every covered work item, and its landed table every destination written — `close-documented` reads the list | `frontmatter-update completed="{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"`, `script close-documented`, `script commit-docs` |

| Superstate | To | When | Gates | Hooks |
| --- | --- | --- | --- | --- |
| `spec-set` | `cancelled` | the user cancels the run | | `frontmatter-update completed="{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"`, `script commit-docs` |
| `change-set` | `cancelled` | the user cancels the run | | `frontmatter-update completed="{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"`, `script commit-docs` |
| `producing` | `cancelled` | the user cancels the run | | `frontmatter-update completed="{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"`, `script commit-docs` |

Scripts the Hooks cells reference, each shipped at `_scripts/{name}`, each taking no arguments and
reading `BOOPING_WORKDIR` (`{vault}/docs`) and `BOOPING_ARTIFACT` (the run record):

- `commit-docs` — stage and commit the vault's `docs/` directory, tagging the message with the
  `status:` the transition just wrote. Fired on the edges that close a superstate, so the vault
  carries one commit per boundary. Vault only — the repo-side documentation this run writes is
  never committed by the playbook.
- `close-documented` — append one row per entry of the run record's `documented:` list to
  `_specs/documented.md` (work item → this run record), leaving existing rows untouched. The
  `record` step therefore only populates `documented:`; the ledger write is the hook's.
