---
{}
---

[← index](../../index.md)

# states — Tests

## Fixtures

| Fixture                | Requirements                                                                                                     |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------- |
| minimal-verdict-tree   | confirmed decomposition with `state machine: minimal — …` in Decisions, two gated waves, brief                   |
| rich-verdict-tree      | confirmed decomposition with `state machine: rich — …`, a repeated subgraph, an artifact other playbooks gate on |
| ephemeral-verdict-tree | confirmed decomposition with `state machine: ephemeral — …`, no user override                                    |

## Tests

| Fixture                | Tier    | Title            | Check logic                                                                                                                                                                                                                                                                                                |
| ---------------------- | ------- | ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| minimal-verdict-tree   | smoke   | FILE-WRITTEN     | `_specs/states.md` written with a `## <machine>` per machine; index links it right after the graph fence; index frontmatter preserved                                                                                                                                                                      |
| minimal-verdict-tree   | smoke   | TABLE-COLS       | transitions table columns exactly State, To, When, Gates, Hooks                                                                                                                                                                                                                                            |
| minimal-verdict-tree   | smoke   | NONE-ROW         | first transitions row is `none` → the initial status                                                                                                                                                                                                                                                       |
| minimal-verdict-tree   | smoke   | HOOKS-MACHINE    | every non-empty Hooks cell matches `frontmatter-update …` or `script <name>` — no prose; multi-hook cells are `;`-separated                                                                                                                                                                                |
| minimal-verdict-tree   | smoke   | REVIEWED-STAMP   | every row leaving an `awaiting-*-confirm` status on a confirm (non-rework) edge carries a `reviewed_at="{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"` hook — one per reviewed file, always `frontmatter-update <path> reviewed_at="{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"` with an explicit path, even when the reviewed file is the machine's own artifact; no confirm edge is exempt |
| minimal-verdict-tree   | smoke   | NO-RETIRED-STAMP | no retired stamp shapes authored — no `*_confirmed`, `smoke_green` or `completed` keys; a confirm gate's only stamp is `reviewed_at` (or a subject-keyed `<subject>_reviewed_at`), keys carrying run data are unaffected                                                                                   |
| minimal-verdict-tree   | smoke   | TERMINAL-MARK    | terminal states carry `ᵗ` in every appearance and have no outgoing row                                                                                                                                                                                                                                     |
| ephemeral-verdict-tree | smoke   | SKIP-CLEAN       | no `states.md` created, index unchanged; return carries the skip note, empty `## Changed:`                                                                                                                                                                                                                 |
| minimal-verdict-tree   | regress | MINIMAL-PATTERN  | machine is the confirmation chain only — in-progress + awaiting-confirm per gated wave, `done`ᵗ, artifact `index.md`, no superstates/scripts                                                                                                                                                               |
| rich-verdict-tree      | regress | RICH-SOUND       | per-instance machine uses `{instance}` in its artifact and only there; every non-terminal has an exit; confirmations modeled as gated statuses; handoff statuses reflect the cross-playbook dependency                                                                                                     |
