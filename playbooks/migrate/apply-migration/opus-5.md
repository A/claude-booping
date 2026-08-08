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
