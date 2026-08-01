---
reviewed_at: 20260731 19:57
---
[← index](../../index.md)

# decompose-work — Tests

## Fixtures

| Fixture            | Requirements                                                                                                                                                                                                                                                                                                    |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| oversized-plan     | the written plan `plans/20260801-14-30_local-vault-directories.md` — 5 milestones, every task carrying its own DoD and Verify, per-task and per-milestone SP, sprint 38 SP mirrored in `sp:` frontmatter; two tasks at 5 SP (M2 resolve the vault path from the marker, M4 scaffold a repo-local vault), each splittable at a clean seam; the 5 SP re-decompose threshold, the 35 SP split threshold and the SP scale |
| right-sized-plan   | the written plan `plans/20260801-16-05_fix-stale-session-cookie.md` — 3 milestones, 6 tasks, largest 3 SP, sprint 9 SP in `sp:`; same thresholds and scale                                                                                                                                                       |
| split-only-plan    | trap — `plans/20260801-17-40_notification-center.md`: 6 milestones, no task over 4 SP, sprint 41 SP, with a real seam between the delivery pipeline (M1–M3, 22 SP) and the preferences UI (M4–M6, 19 SP); provokes one blanket `Skipped` that never flags the split, the two thresholds being read as one condition |
| entangled-oversize | trap — `plans/20260801-18-20_indexed-plan-store.md`: 4 milestones, sprint 18 SP, one 5 SP task "move plan reads from flat files to the indexed store" whose obvious cut is add-the-reader / delete-the-writer; provokes a pair that only works once both land                                                     |

## Tests

| Fixture            | Tier    | Title                 | Check logic                                                                                                                                                          |
| ------------------ | ------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| oversized-plan     | smoke   | FILE-AT-PATH          | written at `_runs/groom/20260801-14-30_local-vault-directories/decomposition.md`; H1 `# Decomposition — 20260801-14-30_local-vault-directories`                       |
| oversized-plan     | smoke   | FRONTMATTER-NULL      | frontmatter is exactly `reviewed_at: null`                                                                                                                           |
| oversized-plan     | smoke   | SECTIONS-REFINED      | H2s exactly Verdict, Re-decomposed, Totals, Split candidate — in that order, none extra                                                                              |
| oversized-plan     | smoke   | VERDICT-COUNTS        | Verdict reads `Refined` and carries both counts — 2 tasks at or over the 5 SP threshold, and the sprint total against the 35 SP split threshold                       |
| oversized-plan     | smoke   | REDECOMPOSED-TABLE    | Re-decomposed columns Was, SP, Became, SP; both 5 SP tasks appear as Was rows; every Became row is under 5 SP                                                         |
| oversized-plan     | smoke   | TOTALS-RESUMMED       | Totals carries Before and After per milestone plus a Sprint row; each After equals the sum of that milestone's tasks in the updated plan, Sprint After the sum of them |
| oversized-plan     | smoke   | PLAN-TASKS-REPLACED   | in the plan neither 5 SP task survives; each is replaced by two or more tasks, every one carrying its own DoD and its own Verify                                      |
| oversized-plan     | smoke   | NO-TASK-OVERSIZED     | no task in the updated plan sits at or over 5 SP                                                                                                                     |
| oversized-plan     | smoke   | PLAN-SP-SYNCED        | plan `sp:` frontmatter equals the Sprint After figure; each milestone's stated total equals the sum of its own tasks                                                  |
| oversized-plan     | smoke   | SPLIT-CANDIDATE-SHAPE | Split candidate names the seam, the primary and the sibling with their milestone ranges and SP; the two SP figures sum to the sprint total                            |
| oversized-plan     | smoke   | NO-SIBLING-CREATED    | `plans/` gains no file, no backlog stub is written, and the run workdir gains only `decomposition.md`                                                                 |
| oversized-plan     | smoke   | RETURN-ANNOTATED      | Changed carries `[UPDATED] plans/…` and `[CREATED] …/decomposition.md`, each annotated with the verdict and its counts; Notes carries the re-decomposition count, the largest surviving task, the re-summed sprint total and the split candidate |
| oversized-plan     | regress | SPLITS-STAND-ALONE    | each replacement task's DoD and Verify are satisfiable on their own — a pair whose first half's Verify only passes once the second lands fails                        |
| oversized-plan     | regress | SPLITS-AT-SEAMS       | each split follows a seam in the original task's work (read the marker key / resolve the path forms), not an arbitrary halving into part 1 and part 2                 |
| oversized-plan     | regress | NOTHING-ELSE-TOUCHED  | surviving tasks' DoD and Verify, the architecture and template sections and `summary:` come through unchanged — only the split tasks and the SP figures differ        |
| oversized-plan     | regress | SEAM-ARGUED           | the split candidate argues why the seam holds: the primary shippable without the sibling, the sibling useless without the primary                                     |
| oversized-plan     | regress | QUESTIONS-USER-CALLS  | Questions holds only sizing calls that are the user's — take the split or keep one sprint — one line each, nothing the thresholds already decide                      |
| right-sized-plan   | smoke   | SKIP-FILE-WRITTEN     | written at `_runs/groom/20260801-16-05_fix-stale-session-cookie/decomposition.md` with the same H1 and `reviewed_at: null` shape — never omitted on the skip path     |
| right-sized-plan   | smoke   | SKIP-VERDICT-ONLY     | `## Verdict` is the only H2 — no Re-decomposed, Totals or Split candidate section                                                                                    |
| right-sized-plan   | smoke   | SKIP-VERDICT-COUNTS   | Verdict reads `Skipped` and carries both figures — largest task 3 SP against the 5 SP threshold, sprint 9 SP against the 35 SP threshold                              |
| right-sized-plan   | smoke   | SKIP-PLAN-UNTOUCHED   | `plans/20260801-16-05_fix-stale-session-cookie.md` is byte-identical to the fixture and absent from `## Changed:`                                                     |
| right-sized-plan   | smoke   | SKIP-RETURN           | Changed is the one `[CREATED]` line annotated skipped; Notes reports no oversized task, the total under the threshold and the plan untouched; Questions empty         |
| right-sized-plan   | regress | SKIP-GROUNDED         | the rationale cites the fixture's own figures — largest 3 SP, sprint 9 SP — not a generic claim that the plan is already right-sized                                  |
| split-only-plan    | smoke   | TRAP-SPLIT-FLAGGED    | `## Split candidate` present, naming the seam with primary and sibling SP, even though nothing was re-decomposed                                                      |
| split-only-plan    | smoke   | TRAP-BOTH-COUNTS      | the Verdict reports the two thresholds separately — no task at or over 5 SP, sprint 41 SP past the 35 SP split threshold                                              |
| split-only-plan    | smoke   | TRAP-NO-FAKE-SPLITS   | no plan task is split, the plan is untouched and absent from Changed, and Re-decomposed and Totals are both absent                                                    |
| split-only-plan    | regress | TRAP-SEAM-REAL        | the seam is argued from the plan's own dependencies — the delivery pipeline ships without the preferences UI — not cut at the SP midpoint                             |
| entangled-oversize | smoke   | TRAP-ENTANGLED-SPLIT  | the 5 SP task is gone from the plan, no task sits at or over 5 SP, and each replacement carries its own DoD and Verify                                                |
| entangled-oversize | smoke   | TRAP-NO-SPLIT         | Split candidate is the one line that the 18 SP total is under the 35 SP threshold and no split is recommended                                                         |
| entangled-oversize | regress | TRAP-VERTICAL-SLICE   | the cut is a vertical slice — each half moving one read path end-to-end — not an add-the-reader then delete-the-writer pair that leaves the store half-wired           |
