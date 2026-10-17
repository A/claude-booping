---
id: "03"
title: "plan split e2e cases on benchmark plans"
sp: 3
status: done
plan: "plans/202610161319_groom-one-pass-and-plan-split/index.md"
---

# M03: plan split e2e cases on benchmark plans

**Goal**: the e2e corpus holds `booping plan split` cases on four real benchmark plans and on each failure exit code.

**Scope**: new `booping-python/e2e/cases/plan/*.txtar`. Sources (read-only, outside the repo): `~/Dev/@A/booping-benchmarks/groom/results/{path}/plan.md` for the labels `m2-V3a-r1`, `m2-V3-r2`, `s1-V3a-r1`, `c1-V3a-r1` in `~/Dev/@A/booping-benchmarks/groom/split/plans.txt`.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Secret check before copying: `grep -n -i -E '(api[_-]?key|token|secret|password|passwd|bearer|BEGIN [A-Z ]*PRIVATE|@[a-z0-9-]+\.[a-z]{2,}|https?://[^ ]*(internal|corp|\.local)|[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})'` over each source plan; read every hit. A plan with a real credential, personal email, private hostname or internal URL is swapped for the next plan of the same task in `plans.txt` (never redacted by hand); a task with no clean plan left loses its case, and the run keeps at least three benchmark cases. The worker runs on the owner's machine, where the benchmark repo is local. Record the four chosen labels and the outcome of the check per plan in `plans/202610161319_groom-one-pass-and-plan-split/develop-defaults.md` (vault-relative; the runner writes it from the worker's return). | — | 1 | done |
| 3.2 | One case per chosen plan: `booping plan split draft.md` over a `cwd` holding only `draft.md` (no `index.md`), asserting exit 0 or the 4 the plan really earns, stdout, and the expected `index.md` plus every milestone file; baseline with `just e2e -k plan --txtar-update`, then read each expected milestone file against its source block — section placement right, no line lost — before keeping the baseline. | `booping-python/e2e/cases/plan/split-benchmark-m2-v3a-r1.txtar`, `split-benchmark-m2-v3-r2.txtar`, `split-benchmark-s1-v3a-r1.txtar`, `split-benchmark-c1-v3a-r1.txtar` | 1 | done |
| 3.3 | Contract cases on small hand-written drafts: existing `index.md` frontmatter kept and `sp` restamped; exit 3 headingless draft (no files written); exit 4 missing `sp`; exit 2 existing milestones without `--replace`; `--replace` replaces them; a `### M02 — x` line inside a fenced block is not a cut. | `booping-python/e2e/cases/plan/split-keeps-index-frontmatter.txtar`, `split-no-milestone-headings.txtar`, `split-missing-sp-flags.txtar`, `split-refuses-existing-milestones.txtar`, `split-replace.txtar`, `split-heading-in-fence.txtar` | 1 | done |

Tests: surface `bin/booping plan split` as a user runs it; cases above; tier e2e (txtar contract corpus).

## Definition of Done

### Task 3.1

- [x] Return lists, per chosen plan, its label and "clean" or what was found and the replacement label.

### Task 3.2

- [x] Four benchmark cases exist and pass; each asserts every written file.

### Task 3.3

- [x] Six contract cases exist and pass, each asserting its exit code and stderr `flag:`/`error:` line where the contract names one.

## References

- `booping-python/e2e/cases/scaffold/core-milestone-tree.txtar` — a case asserting written files.
- `booping-python/e2e/conftest.py` — the corpus wiring (`cwd`, `home`, `xdg` roots).
- https://github.com/A/pytest-txtar — the case format spec.

## Verify

```
just e2e -k plan
```
