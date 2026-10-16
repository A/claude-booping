---
id: "02"
title: "booping plan split command"
sp: 4
status: pending
plan: "plans/202610161319_groom-one-pass-and-plan-split/index.md"
---

# M02: booping plan split command

**Goal**: `booping plan split DRAFT [--out DIR] [--replace]` writes `index.md` and the milestone files from a draft, per the I/O contract in `index.md`.

**Scope**: new `booping-python/src/booping/commands/plan.py` (the `plan` group and its `split` verb), `booping-python/src/booping/cli.py` (registration), `src/config.yaml` (`core.groom_playbook.split.sections`), possibly a small public helper extracted from `booping-python/src/booping/commands/scaffold.py`, tests `booping-python/tests/plan/split_command_test.py`. Reads `core.sprint.max_sp`, `core.plans.milestones` and `core.groom_playbook.milestone_scaffold` from the merged config.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Add `core.groom_playbook.split.sections: [Tasks, Definition of Done, References, Verify]` with a comment naming its two readers (split's output headings, draft-plan's format block). Split maps `cut.sections` keys `tasks`/`dod`/`references`/`verify` onto these names in order. | `src/config.yaml` | 1 | pending |
| 2.2 | `commands/plan.py`: `plan` group with `verbs = p.add_subparsers(dest="plan_verb", metavar="<verb>", required=True)` like `commands/items.py`; `split` verb with the arguments and exit-code constants of the I/O contract; register in `cli.py` in alphabetical order. Write each milestone file by rendering `core.groom_playbook.milestone_scaffold` in-process with `id`, `slug`, `title`, `sp` (`null` when unknown), `plan` = the plan's `index.md` path relative to the vault as the scaffold call does today, then insert each section's lines (demoted, ending in one blank line) under its `## {name}` heading. Reuse `context/scaffold.py:load` and the render/write path of `commands/scaffold.py`; extract a public helper there if the private `_plan`/`_apply` cannot be called cleanly, keeping `booping scaffold` behaviour identical. | `booping-python/src/booping/commands/plan.py`, `booping-python/src/booping/cli.py`, `booping-python/src/booping/commands/scaffold.py` | 2 | pending |
| 2.3 | `index.md`: keep existing frontmatter byte for byte except `sp:` restamped with the sum of the milestones whose `sp` is known (null ones add nothing, as `refresh-milestone-table` sums only integers); with no `index.md`, take the draft's leading frontmatter block verbatim (restamped likewise), else none. Body = plan lines in order with the generated block where the overview stood (else before the first milestone): `## Milestones` table in `refresh-milestone-table`'s exact format (columns `core.plans.milestones.table_columns`, `| --- |` separators, `title` linked to the plan-dir-relative milestone path), then `## Groups` (`| group | milestones | sp |`, `G{k}`, `M{nn}` ids). `--replace` deletes only directories holding a file matching `core.plans.milestones.glob`; without it, any such file → exit 2 before anything is written. stdout/stderr lines exactly as the contract states. | `booping-python/src/booping/commands/plan.py` | 1 | pending |

Tests: surface `booping plan split` invoked through `booping.cli` main on a temp plan dir; cases — fixed-format draft with an existing `index.md` (frontmatter kept, `sp` restamped, table equals what `refresh-milestone-table` renders for the same files), draft with no headings (exit 3, nothing written), missing `sp` (exit 4, `sp: null`, `flag:` on stderr), existing milestones without `--replace` (exit 2) and with it (old dir gone); tier integration over a real temp directory and the real config.

## Definition of Done

### Task 2.1

- [ ] `bin/booping config-get core.groom_playbook.split.sections` prints the four names, and a test asserts a written milestone file carries them as `##` headings in config order, `tasks`→first … `verify`→fourth.

### Task 2.2

- [ ] `bin/booping plan split --help` lists `DRAFT`, `--out`, `--replace` and the exit codes.
- [ ] A written milestone file's frontmatter and H1 are byte-identical to what `booping scaffold core.groom_playbook.milestone_scaffold` writes for the same `--set` values.
- [ ] `just e2e -k scaffold` still passes (scaffold is verified by the e2e corpus, not unit tests).

### Task 2.3

- [ ] Running `playbooks/develop/_scripts/refresh-milestone-table {plan-dir}` right after a split leaves `index.md` unchanged (asserted in a test).
- [ ] `uv run pytest tests/plan/split_command_test.py` passes with every case listed above.

## References

- `booping-python/src/booping/commands/items.py` — verb-group shape, `_fail`, argument style.
- `booping-python/src/booping/budget.py` — named per-command exit-code constants.
- `playbooks/develop/_scripts/refresh-milestone-table` — table format and `sp` restamp the output must match.

## Verify

```
cd booping-python && uv run pytest tests/plan -q
```
