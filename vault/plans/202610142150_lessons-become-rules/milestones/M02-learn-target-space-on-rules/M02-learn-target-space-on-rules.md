---
id: "02"
title: "Learn preamble and target space on rules"
sp: 4
status: pending
plan: "vault/plans/202610142150_lessons-become-rules/index.md"
---

# M02: Learn preamble and target space on rules

Learn's preamble names a rule record in the project specs tier and the repo `CLAUDE.md` as its two destinations, and its target space shows the rules already targeting each playbook beside the remaining lessons.

**Scope**: `playbooks/learn/playbook.md` (frontmatter `summary`/`trigger`, `## Guidance`, `## Single-location rule`), `playbooks/learn/_partials/_learn_targets.j2`, the target-space partial renamed from `playbooks/_partials/lesson_target_space.md` to `playbooks/_partials/target_space.md`, and `playbooks/learn/extract-candidates/base.md` + `fable-5.md`. Lessons still inject in this plan (C1), so the target space lists both. Rule fields available to templates: `context.targeted_rules` items carry `ref`, `title`, `brief`, `link`, `tier`, `parsed_targets` (`booping-python/src/booping/specs/rules.py`).

Tests: the rendered surface — `render-playbook learn` and the partial with `--set targets_for=groom`; the core tier's groom-targeted rules show under `**Rules:**`.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Rename the partial with `git mv`; heading `## Targets`; after the step table, a `**Rules:**` list — one bullet `- {ref} — {brief}` per rule whose `parsed_targets` name the playbook — before the existing `**Lessons:**` list. Update every reference to the old path. | `playbooks/_partials/target_space.md`, `playbooks/learn/_partials/_learn_targets.j2` | 2 | pending |
| 2.2 | Preamble and target prose: the two destinations are a rule record in the project specs tier (`booping specs init --tier project` prints its root) and the repo `CLAUDE.md`; `targets:` is the rule's wiring; `brief:` is what reaches the target. Frontmatter `summary`/`trigger` say rules, not lessons. | `playbooks/learn/playbook.md`, `playbooks/learn/_partials/_learn_targets.j2` | 1 | pending |
| 2.3 | `extract-candidates` (both variants): destination `Rule` instead of `Lesson`; each rule candidate carries a `Brief` — one or two self-sufficient lines that do not restate what the agent checks anyway (`src/specs/README.md`, rule frontmatter); the returned table (fable-5) gains a `Brief` column after `Targets`; "existing lesson" ID wording covers an existing rule (`rule/0004 (questions-settled-in-grooming)`). | `playbooks/learn/extract-candidates/base.md`, `playbooks/learn/extract-candidates/fable-5.md` | 1 | pending |

## Definition of Done

### Task 2.1

- [ ] `rg -n lesson_target_space playbooks src docs documentation -g '!_reports'` returns nothing.
- [ ] `bin/booping render playbooks/_partials/target_space.md --set targets_for=groom` shows a `**Rules:**` list carrying the core groom-targeted rules (e.g. `booping:rule/0004`).

### Task 2.2

- [ ] `bin/booping render-playbook learn` names no `_lessons/` destination; the rendered `## Targets` says rule.

### Task 2.3

- [ ] Neither variant routes a candidate to `_lessons/`; fable-5's table columns are `#`, `Rule`, `Example`, `Target`, `Lands at`, `Targets`, `Brief`.

Return: the list of changed files, nothing else.

## References

- `playbooks/_partials/lesson_target_space.md` — the shape the renamed partial keeps.
- `src/templates/_partials/_rules.j2` — how a rule bullet reads elsewhere.

## Verify

`bin/booping render-playbook learn --project playbooks/_fixtures/vault`
