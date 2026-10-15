---
id: "03"
title: "Learn dedup sweep and review table over rules"
sp: 4
status: done
plan: "vault/plans/202610142150_lessons-become-rules/index.md"
---

# M03: Learn dedup sweep and review table over rules

Learn's dedup sweep checks candidates against the rule records of all three specs tiers (plus remaining lessons and `CLAUDE.md`), and the review table carries the rule columns the write step needs.

**Scope**: `playbooks/learn/dedup-sweep/base.md`, `playbooks/learn/review-table/base.md`, `docs/learn_review_table.md`. Verdicts and tier reach are locked in `clarifications.md` C6; table columns in C12.

Tests: the rendered step bodies (`render-playbook learn --step dedup-sweep` / `--step review-table`); behaviour is covered by the learn evals in M05.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Lookup set: `booping specs ls --tier {core,global,project} --type rule` (a missing tier is skipped silently), `{vault}/_lessons/`, `{home_dir}/_lessons/`, the repo `CLAUDE.md`; delete the bullet that starts "The vault's legacy `lessons/`" from the lookup list. Verdicts per C6: `new`, `update existing at rule/NNNN` (project rule) or `at _lessons/{file}` (converted on write), `covered by {ref}` (core/global rule or global lesson — never written), `conflict with {ref}`. | `playbooks/learn/dedup-sweep/base.md` | 2 | done |
| 3.2 | Review table per C12: columns `#`, `Target`, `Type`, `Targets`, `Brief`, `Rule`, `Example`; Type `rule` / `claude-md` / `covered`; the format doc owns the columns, so `review-table/base.md` drops its "one added column" paragraph and the four target forms (the preamble's `## Targets` carries them) and keeps only the AskUserQuestion and record-the-response instructions. | `playbooks/learn/review-table/base.md`, `docs/learn_review_table.md` | 2 | done |

## Definition of Done

### Task 3.1

- [x] The step never names `lessons/` (legacy) and never routes a row to a lesson file.
- [x] Every C6 verdict appears once, worded as in C6.

### Task 3.2

- [x] `docs/learn_review_table.md`'s example table has one `rule`, one `claude-md` and one `covered` row in the C12 column order.
- [x] The target forms are stated in exactly one place (`_learn_targets.j2`); `review-table/base.md` links rather than restates.

Return: the list of changed files, nothing else.

## References

- `docs/learn_review_table.md` — current shape to extend.

## Verify

`bin/booping render-playbook learn --step review-table --project playbooks/_fixtures/vault`
