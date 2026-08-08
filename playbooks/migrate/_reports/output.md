Brings the vault current: every pending migration applied in id order, each its own vault
commit, closing with one summary. Scope is the vault only — a repo-local vault is no special
case.

Migrations complete one full cycle before the next starts — apply, advance the recorded id,
commit everything — never batched to the end and never in parallel. A failing instance halts
the sequence immediately: name the failing id, what failed, and a remedy the user can apply by
hand. No skipping ahead, no silent rollback.

`migration.md`'s `id` frontmatter is authoritative; the `NNN_` directory prefix is a cosmetic
sort hint only. Migrations know nothing of git or `.booping` — the playbook owns every commit
and the id advance.

## Playbook Steps

Execute the steps in the most effective order considering their dependencies.

| Step | Dependencies | Summary | Review gate |
| --- | --- | --- | --- |
| `survey` | — | Open the run: confirm a project is attached and the recorded migration id is readable; when work is uncommitted, name it, ask, and commit repo and vault on confirmation; present the pending set the rendered body carries and what each migration will do; report "already current" and end the run when the set is empty. | The user approves applying the whole pending set — the run's only gate, taken once and covering every listed migration. The in-body commit ask is a safety confirmation resolved inside the step, not this gate. An empty pending set ends the run with nothing to approve. |
| `apply` *(subgraph)* | `survey` | once per pending migration, in ascending id order; strictly one instance at a time — never in parallel — and a failed instance stops the run | — |
| `apply-migration` *(in apply)* | — | Run one migration's whole cycle — hand its `migration.md`, prompt plus commands, to a context-fresh sub-agent, then advance `latest_migration` and commit everything; on failure halt the sequence, naming the failing id, what failed and a remedy the user can apply by hand. | — |
| `summarize` | `apply` | Close with a single report of what changed across the whole run — the migrations applied, the commits carrying them, and whether the vault is now current. | — |

## Step: Survey
# Open the migration run

## Ground

Confirm a project is attached, and name it and its vault path in the presentation.

The recorded migration id — the last migration this vault applied — is **3**,
read from the repo `.booping` marker's `latest_migration` key; `-1` means nothing has been applied yet.
If no project is attached, or that id came through as anything other than a number, say which and
end the run: nothing below resolves without it.


## Already current

Nothing is pending: **3** is the latest migration the plugin ships.

Report it in one line — the project and its vault, the recorded id, that the vault is **already
current**, and that the run ends here. Ask nothing, commit nothing, and do not continue to the next
step.

## Return

```markdown
## Changed:

## Notes:
- pending: 0 — already current at recorded id 3
- end the run: nothing to apply
```

`## Changed:` stays empty — this step writes no file.

## Subgraph: apply

Instructions:
- After: survey
- Repeat: once per pending migration, in ascending id order; strictly one instance at a time — never in parallel — and a failed instance stops the run
- Inner waves: 1. `apply-migration`

## Step: Apply Migration
# Apply one migration

This instance is one pending migration, named in your run-time context by its location, id and
title. You never read its `migration.md` — a context-fresh sub-agent reads it and performs the
transformation, so no migration body enters this conversation. You own the parts the migration
knows nothing about: the recorded id and the commit.

Complete the whole cycle before the next instance starts — **apply → set `latest_migration` →
commit everything → next**. Nothing batches to the end of the run.

## 1. Apply

Spawn a sub-agent — model opus, effort medium — with this bootstrap, filled from your run-time
context and nothing else:

```
Apply one booping vault migration. Read `<migration-dir>/migration.md` — that file is your
entire instruction: follow its prompt and run its commands. Nothing else briefs you.

## Run-time context
project: <project>
vault: <vault path>
migration id: <id>

## Inputs
- the migration's location: `<migration-dir>/`
  Files beside `migration.md` are that migration's own workspace — read them only if its
  prompt sends you there.

## Rules
- Transform the vault and nothing else.
- Do not stage, commit, or touch `.booping` — the playbook owns the commit and the id advance.
- Do not read or apply any other migration.

## Return (≤ 5 lines)
- outcome: `applied` or `failed`
- the files you changed
- on `failed`: what failed, concretely enough that a remedy can be named
```

## 2. Land it

On an `applied` receipt, and only then:

- Set `latest_migration` in the repo's `.booping` marker to this migration's frontmatter `id` —
  **set, not incremented**. Ids may skip, and the `NNN_` directory prefix is never parsed.
- Commit everything — the whole working state, not a path-scoped subset.

## 3. Halt on failure

A `failed` receipt, or no usable receipt at all, stops the whole sequence. Do not advance the id,
do not commit, do not roll back, do not start the next migration. Report the failing id and
title, what failed, a remedy the user can apply by hand, and where `latest_migration` and the
commits were left — naming what the failed migration left behind uncommitted.

## Return format

```markdown
## Changed:
- [CREATED] /home/u/Claude/acme-api/_lessons/0003_gates.md
- [UPDATED] /home/u/Dev/acme-api/.booping

## Notes:
- migration 3 (lessons_to_targeted) applied; `latest_migration` now 3; committed
```

`## Changed:` lists the vault files this migration transformed plus `.booping`. On the failure
path the halt line replaces the applied line, `.booping` is absent, and what the migration left
behind is reported uncommitted:

```markdown
## Changed:
- [UPDATED] /home/u/Claude/acme-api/_lessons/0003_gates.md — left uncommitted by the failed migration

## Notes:
- HALTED at migration 4 (plans_to_dirs): `plans/20260714-09-12_add-search/` already exists as a
  directory holding a different plan, so the move refused.
- Remedy: rename or merge that directory by hand, then re-run `/playbook migrate` — it resumes
  from `latest_migration: 3`.
- `latest_migration` stays at 3; migration 4 is not committed; migrations 5+ were not started.
```

## Step: Summarize
Close the run with **one** report — one however many migrations ran.

You carry, from this run: each migration it applied (id, title, outcome), the commit each one
landed in, and the pending set `survey` presented. Read the `latest_migration` key in the repo's
`.booping` marker and compare it against the highest id in that pending set — the highest id the
plugin ships. Currency is a checked fact, never an assumption.

Present in chat:

```
Vault migrated — {n} migrations applied, vault is now current.

| id  | migration       | outcome | commit    |
| --- | --------------- | ------- | --------- |
| 003 | plans_to_dirs   | applied | `a1b2c3d` |
| 004 | lessons_targets | applied | `e4f5a6b` |

`latest_migration`: `002` → `004` — the highest migration the plugin ships, so render surfaces
stop reporting the vault as behind and normal work resumes.

Migrations `001`–`002` landed in an earlier run; this report covers only what this run applied.
```

- one row per migration **this run** applied, in ascending id order
- the closing line only when earlier ids landed before this run — one line, never an enumeration
  of what those migrations did
- when `latest_migration` is below the highest shipped id, that mismatch is the headline: say the
  vault is **not** current, name the id it stopped at and the ids still pending, and drop the
  "normal work resumes" claim

Scope is the run just completed. Never reconstruct the vault's whole migration history — a
re-entry after an earlier halted run is an ordinary run. A failed run never reaches you:
`apply-migration` halts the sequence itself, so never describe a failure.

Return to the runner (the report above is what the user sees; this block is bookkeeping):

```
## Changed:

## Notes:
- {n} migration(s) applied; latest_migration {from} → {to}; vault current
```
