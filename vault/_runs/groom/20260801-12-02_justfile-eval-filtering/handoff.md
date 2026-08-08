# handoff — 20260801-12-02_justfile-eval-filtering

## Approach

One new script, `bin/eval-run.sh`, becomes the sole place that knows how to pick and run promptfoo
suites. All four `justfile` eval recipes (`eval`, `eval-md`, `smoke`, `regress`) shrink to one-line
delegations into it. You'll be able to pass a plain substring of a suite's directory path —
`groom/decompose`, `groom/`, or nothing at all — to any of the four recipes to pick one suite, every
suite of a playbook, or everything in the repo; `--dry-run` shows what would run without spending on
promptfoo. The script runs one promptfoo process per matched suite in sequence (never a merged
multi-config run, which would silently cross-product suites' prompts and tests against each other),
and rolls the per-suite results into one `TOTAL` line when more than one suite ran. The existing
`bin/eval-md.sh` markdown-report path is folded into the same script behind a `--md` flag and then
deleted, so there is one selector parser instead of two. The explicit `-c <config>` form the justfile
documents today keeps working unchanged.

## Milestones

| # | Milestone | SP | Delivers |
|---|-----------|----|----------|
| 1 | Suite resolution and `--dry-run` | 5 | `bin/eval-run.sh` resolves a selector to the matching suite config paths and can print that list under `--dry-run` without invoking promptfoo |
| 2 | Sequential execution, aggregation and `--md` | 7 | one promptfoo process per resolved suite, an announce line naming the set up front, a rolled-up `TOTAL` line, and a `--md` flag producing one combined markdown report |
| 3 | Recipe delegation, `bin/eval-md.sh` retirement and docs | 5 | the four `justfile` recipes delegate to `bin/eval-run.sh`, `bin/eval-md.sh` is deleted, and the justfile comment block plus `CLAUDE.md` describe the selector instead of the by-hand `-c` form |

## Totals

17 SP across 3 milestones — well under the 35 SP split threshold.

## Plan

`/home/anton/Dev/@A/notes/projects/claude-booping/plans/20260801-12-02_justfile-eval-filtering.md` —
status `awaiting-plan-review`.

## Checks

- **Decomposition** — skipped: no task sits at or over the 5 SP re-decompose threshold (the largest
  are 3 SP each — task 1.1's script skeleton and flag parser, task 2.1's announce line and sequential
  suite loop), and the 17 SP sprint total sits well under the 35 SP split threshold. The plan file
  was not touched.
- **Cross-review (codex)** — 5 findings, 2 RISK and 3 NOTE. All 5 were folded into the plan; none
  were deferred, so no risk register was needed.
- **References** — 8 checked, 0 corrected; the plan file is untouched. 2 rows citing bash manual
  behaviour were settled against the installed bash 5.3.15 after the canonical source returned
  HTTP 429; the cited URLs are unchanged.

## Next

Approval moves the plan to `ready-for-dev` and hands it to `/develop`. A change request to
milestones, tasks or estimates loops back to the refinement pass; a change request to architecture
or scope loops back to design.
