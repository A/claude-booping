---
id: "04"
title: "Learn writes rule records"
sp: 4
status: done
plan: "vault/plans/202610142150_lessons-become-rules/index.md"
---

# M04: Learn writes rule records

Learn's write step writes each accepted rule row as a rule record in the project specs tier, checked by `booping specs check`, and closes with a commit that stages the tier; rule/0001 gets its targets and brief back.

**Scope**: `playbooks/learn/write/base.md` + `fable-5.md`, a new `playbooks/learn/_partials/_rule_template.j2` replacing `_lesson_template.j2` (deleted), `playbooks/learn/playbook.yaml` (gate text, hook argv), `playbooks/_scripts/close-working-set` only if staging a deleted lesson path fails today, `vault/specs/rule/0001-lessons-are-rules.md`. Record shape: `clarifications.md` C5; update/convert semantics C6; staging C7; rule/0001 text C9.

Tests: `close-working-set --stage` with a deleted file under a staged dir — if the script needs a change, cover it where its existing tests live (`rg -l close-working-set booping-python/tests booping-python/e2e`); the write behaviour is covered by the learn evals in M05.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Write step (both variants): `booping specs init --tier project` first (its last stdout line is the tier root), `booping specs next rule --tier project` per new record, the record per C5 from `_rule_template.j2`; `update existing at rule/NNNN` edits in place and bumps `updated_at`; `update existing at _lessons/{file}` writes a new rule with the merged content and deletes the lesson (C6); `covered` rows are not written; an accepted `conflict with {ref}` row is written as a new project rule whose `## Rule` opens with a `[clarify]` sentence naming `{ref}` as the departed rule and asking the owner for an ADR (C6); a re-run after a partial failure reuses the record already written for a row (same `title` in the tier) instead of taking a new number; after the last file `booping specs check --tier project` reports no error on the written records (fix and re-run, never weaken). Drop the re-render-for-lesson-notices paragraph. | `playbooks/learn/write/base.md`, `playbooks/learn/write/fable-5.md` | 2 | done |
| 4.2 | `_rule_template.j2`: the C5 frontmatter and body skeleton in `{% raw %}`, `{placeholder}` style; delete `_lesson_template.j2` and every include of it. | `playbooks/learn/_partials/_rule_template.j2`, `playbooks/learn/_partials/_lesson_template.j2` | 1 | done |
| 4.3 | `playbook.yaml`: second gate reads `every accepted row written to its single target — rule records pass booping specs check`; hook `script close-working-set --stage _lessons specs --prefix learn`; confirm `--stage` stages a deletion (adjust the script only if not). rule/0001 per C9. | `playbooks/learn/playbook.yaml`, `vault/specs/rule/0001-lessons-are-rules.md`, `playbooks/_scripts/close-working-set` | 1 | done |

## Definition of Done

### Task 4.1

- [x] Neither variant writes or edits a file under `_lessons/` except the C6 deletion.
- [x] The conflict and re-run cases are each stated once, as in this task.
- [x] The number comes from `booping specs next`, the root from `booping specs init` — no hand-computed path or number.

### Task 4.2

- [x] `rg -n _lesson_template playbooks src -g '!_reports'` returns nothing.
- [x] The template's frontmatter keys equal C5's list; `reviewed` is absent.

### Task 4.3

- [x] `just specs-check` passes with rule/0001 carrying `targets: [learn]` and its brief, no `## Exceptions`.
- [x] `bin/booping render-playbook learn` shows rule/0001 under `## Rules`.

Return: the list of changed files, nothing else.

## References

- `vault/specs/rule/0006-information-architecture-pass.md` — a targeted rule record to copy the shape of.
- `src/specs/schemas/rule.yaml` — the rule schema; do not search elsewhere for the shape.
- `playbooks/learn/_partials/_lesson_template.j2` — the raw-block template style to keep.

## Verify

`bin/booping render-playbook learn --step write --project playbooks/_fixtures/vault`
