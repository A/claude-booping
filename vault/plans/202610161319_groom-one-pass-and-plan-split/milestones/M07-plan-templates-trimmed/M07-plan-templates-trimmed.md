---
id: "07"
title: "Plan templates trimmed to the one-file format"
sp: 3
status: done
plan: "plans/202610161319_groom-one-pass-and-plan-split/index.md"
---

# M07: Plan templates trimmed to the one-file format

**Goal**: the five core plan templates carry the template sections and per-surface milestone content only — no ablation cut rules, no anti-pattern lists, no milestone-shape items now checked by code, no milestone-file seeding prose.

**Scope**: `docs/plan_templates/backend.md`, `claude_skill.md`, `cli.md`, `documentation.md`, `frontend.md`. Rule texts: `~/Dev/@A/booping-benchmarks/groom/ablation/rules.yaml` (ids listed in `index.md` Decisions, "Rules cut").

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | In each template merge `## Milestones` and `## Milestone files` into one `## Milestones` section: "One `### M{nn} — {title}` block per milestone, in the format draft-plan states", followed by the surface's content guidance as the content of its sub-headings — Goal and Scope lines (top of Tasks), the task table, DoD checkbox bullets per task, References, Verify — with the seeding/`booping scaffold`/"generated table" prose removed. | the five files | 1 | done |
| 7.2 | Remove from each `# Quality Checklist` and from Plan Body prose every line expressing one of the 16 cut rules, the whole `## Anti-patterns` block, and the items `booping plan check` or split now own (Verify scoped/one command, files named, DoD per task, `sp` sum, index table matches files, every milestone a file, self-contained milestone). Keep template sections and the items the ablation marked "keep" (motivation, scope-not, decisions alternatives, DoD checkboxes, `summary`, title/type, surface-specific checks such as I/O contract and authorization). | the five files | 1 | done |
| 7.3 | Create `plans/202610161319_groom-one-pass-and-plan-split/template-cuts.md` (vault-relative; returned to the runner, who writes it) listing per template each removed line and the rule id or reason. | — | 1 | done |

Tests: surface the five template files; case — removed rules absent, sections present; tier grep over files.

## Definition of Done

### Task 7.1

- [x] `grep -l 'Milestone files\|milestone_scaffold' docs/plan_templates/*.md` prints nothing.

### Task 7.2

- [x] `grep -n -i -E 'TBD|similar to task|either X or Y|handle edge cases|## Anti-patterns' docs/plan_templates/*.md` prints nothing.
- [x] Every template still has `# Plan Body` and `# Quality Checklist` and the same `##` sections under Plan Body as before, `Milestone files` excepted.

### Task 7.3

- [x] The return carries the per-template removal list, naming each of the 16 rule ids with the line removed or "not present in this template".

## References

- `~/Dev/@A/booping-benchmarks/groom/ablation/prompt-src.md` — backend.md with each line tagged by rule id.
- `~/Dev/@A/booping-benchmarks/groom/ablation/report.md` — keep / cut / fix lists.

## Verify

```
grep -c -E '^# (Plan Body|Quality Checklist)$' docs/plan_templates/*.md
```
