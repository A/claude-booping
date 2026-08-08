---
status: done
reviewed_at: 20260805 09:05
fixtures_reviewed_at: 20260805 09:05
suite_reviewed_at: 20260805 09:11
---

[← index](../../index.md)

# apply-migration

## Contract

- **Needs** —
  - the migration to apply, given as its location on disk — the sub-agent reads that
    directory's `migration.md` (prompt plus commands) itself, so no migration body enters the
    runner's context
  - the vault's current on-disk state, exactly as the previous migration left it
  - the recorded migration id: the `latest_migration` key in the repo's `.booping` marker, and
    the value it currently holds (`-1`, or a comparable sentinel, meaning nothing applied yet)
  - the sub-agent's outcome receipt, once it has run — the input the landing decision turns on
- **Value** — one migration's whole cycle, completed before the next begins: apply, advance
  `latest_migration` to this migration's `id`, commit everything. Nothing batches to the end of the
  run, so an interrupted sequence resumes from the recorded id and each landed migration is
  independently revertable. The migration itself is performed by a context-fresh sub-agent
  briefed only with the migration's location — one migration's context never leaks into the
  next — while the runner keeps the parts the migration knows nothing about: git and the
  recorded id. When the sub-agent reports failure, or returns no usable receipt, the step halts
  the whole sequence rather than landing anything: it names the failing id, what failed, and a
  remedy the user can apply by hand. No skipping ahead, no silent rollback; the recorded id and
  the commits stay at the last migration that fully succeeded.
- **Output files** —
  - `[CREATED|UPDATED] <vault>/…` — whatever files this migration's own instructions transform.
    The set is data-driven, named by the migration and never by this step (for the
    `plans_to_dirs` migration: `[CREATED] <vault>/plans/{slug}/index.md` per flat plan, each
    flat `<vault>/plans/{slug}.md` removed). Scope is the vault and only the vault; a
    repo-local vault is no special case.
  - `[UPDATED] <repo>/.booping` — the marker's `latest_migration` key set to this migration's
    frontmatter `id` (set, not incremented — ids may skip; the `NNN_` directory prefix is never
    parsed). `latest_migration` is the spelling the step prompt, the downstream core plan and
    the sibling `makemigration` playbook all write and read.
  - one commit covering the whole working state, made after the id advance and before the next
    instance starts. Neither the id advance nor the commit happens on the failure path.
- **Harness return** — `## Changed:` listing the vault files this migration transformed plus
  `.booping`; `## Notes:` the applied id, the new `latest_migration` value and the commit — or,
  on failure, the halt line naming the failing id, what failed and the remedy, plus what
  `latest_migration` and the commits were left at.
- **Review gate** —
  - none — per-migration gates are excluded by design; the run's single approval was taken in
    `survey`. Halting is a failure path, not a gate, and this step owns it.
- **Delegation** — `assisted`, deliberately widened. The step is runner-performed and carries
  **no `detached:` key**: that absence is what forbids parallel instances (the driving protocol
  parallelises subgraph instances only when every inner step is detached) and keeps
  halt-on-failure in the runner's own hands, making strict sequencing a property of the engine
  rather than a promise in `repeat` prose. The delegated work is the migration's *execution*,
  not merely heavy reads — a context-fresh sub-agent per instance, tier `opus-5:medium`.
  Because the delegation is body-owned rather than framework-owned, the body hand-rolls the
  bootstrap and return contract a `detached:` step gets for free; the example below is that
  contract, and it is what the eval suite pins.

## Example artifact

```markdown
Apply one booping vault migration. Read
`<plugin-root>/migrations/003_lessons_to_targeted/migration.md` — that file is your entire
instruction: follow its prompt and run its commands. Nothing else briefs you.

## Run-time context
project: acme-api
vault: /home/u/Claude/acme-api
migration id: 3

## Inputs
- the migration's location: `<plugin-root>/migrations/003_lessons_to_targeted/`
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

## Return Format

```markdown
## Changed:
- [CREATED] /home/u/Claude/acme-api/_lessons/0003_gates.md
- [UPDATED] /home/u/Dev/acme-api/.booping

## Notes:
- migration 3 (lessons_to_targeted) applied; `latest_migration` now 3; committed
```

On failure the sequence halts and the halt line replaces the applied line, `.booping` is
absent from `## Changed:`, and whatever the migration left behind is reported uncommitted:

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
