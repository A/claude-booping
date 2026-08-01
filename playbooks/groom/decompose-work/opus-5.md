# Refine the plan against the sizing thresholds

You hold the written plan at `plans/{slug}/plan.md` — its milestones, its tasks with their DoD and
Verify, and the story points per task, per milestone and for the sprint. On a loopback re-entry you
also hold the user's rework and the estimate or milestone it targets, and `index.md` already
carries a `## Refinement` section.

This is a refinement over the written plan, never a rewrite: split the tasks too large for one
agent briefing, re-sum the totals from the new leaves, flag the sibling shape when the sprint is
too large to hold together as one iteration — and touch nothing else. The user's first read of the
plan happens at `present`, right after this pass, so a task left oversized here is one they read.

## Two thresholds, judged separately

The **{{ config.sprint.redecompose_threshold }} SP re-decompose threshold** decides whether tasks are split. The **{{ config.sprint.default_threshold_sp }} SP split threshold** decides whether a split candidate is flagged.
They are independent conditions and the verdict reports both, always: a plan with nothing oversized
can still sit past the split threshold, and a plan full of oversized tasks can total well under it.

- **Refined** — at least one task sits at or over the re-decompose threshold. Split them, re-sum
  the totals, and write the split candidate subsection either way.
- **Skipped** — no task reaches the re-decompose threshold, and `plan.md` is not opened for writing
  at all. `Skipped` is a verdict on the splitting alone: when the sprint total is past the split
  threshold the section still carries its `### Split candidate`, and the verdict says so in the
  same breath.

Measure a task as the plan estimated it; re-estimating a task down to dodge a split is the one move
this pass must never make.

## Re-decomposing

- Cut at a seam in the task's own work — the two things it was really doing — never at its
  midpoint. "Part 1" and "part 2" is not a decomposition.
- Every replacement stands alone: its own DoD, its own Verify, satisfiable on its own. A pair whose
  first half only verifies once the second lands is one task wearing two rows.
- Where the obvious cut is add-the-new-path then delete-the-old-path, take a vertical slice
  instead — each half moving one path end to end, leaving nothing half-wired between them.
- Keep the plan's own shape for a task: its row in the milestone table with its own SP, its own DoD
  block, and the milestone's Verify covering it. A replacement stays in the milestone its original
  was in.
- Re-decomposition redistributes; it does not reduce. Re-sum every milestone from its own tasks and
  the sprint from its milestones, and set the plan's `sp:` frontmatter to that sprint total.
- Nothing else in the plan changes — not the architecture, not the surviving tasks' DoD or Verify,
  not `summary:`, not a template section the draft filled in. Only the split tasks and the SP
  figures differ.

## The split candidate

- Argue the seam from the plan's own dependencies: the primary is shippable without the sibling,
  the sibling is useless without the primary. A cut at the SP midpoint is not a seam.
- Name the primary and the sibling by their milestone ranges and their SP; the two figures sum to
  the sprint total.
- It is a recommendation and nothing more. Create no sibling plan and no backlog stub — `present`
  puts the split to the user, and each sibling is groomed in its own run.
- When the sprint is under the split threshold, say so in one line and recommend no split — on the
  refined path only. A `Skipped` verdict under the threshold has already reported both figures, and
  drops the subsection instead of restating them.

## The section to write

`## Refinement` in `plans/{slug}/index.md` — the only thing this step writes besides the plan.
Preserve the file's frontmatter and the sections other steps own; the section is written on both
paths, never omitted, never empty, and on a re-entry it is revised in place rather than having a
second round appended to it.

The section opens with its verdict line, then carries these H3s, in this order, none extra:

- the **verdict line**, before any H3 — the word `Refined` or `Skipped`, an em dash, then the
  counts that decided it: how many tasks sat at or over the re-decompose threshold, and where the
  sprint total sits against the split threshold. Both thresholds named by their figures.

  ```
  Refined — 2 tasks sat at or over the {{ config.sprint.redecompose_threshold }} SP threshold; the sprint totals 38 SP,
  past the {{ config.sprint.default_threshold_sp }} SP split threshold, so a split candidate is flagged.
  ```

  On the skip path the count of oversized tasks is zero, so the figure carrying it is the largest
  task's own SP — name it, and say that the plan file was not touched:

  ```
  Skipped — no task sits at or over the {{ config.sprint.redecompose_threshold }} SP threshold (the largest is 3 SP),
  and the sprint totals 9 SP, well under the {{ config.sprint.default_threshold_sp }} SP split threshold.
  The plan file was not touched.
  ```
- `### Re-decomposed` — a table with the columns `Was`, `SP`, `Became`, `SP`: one row per oversized
  task naming what it was and its SP, its first replacement and that replacement's SP, then a row
  per further replacement with the `Was` cells left empty. Name every task by the milestone it
  sits in, in the `Was` and `Became` cells alike — a replacement carries its original's milestone:

  ```
  | M2 · Resolve the vault path from the marker | 5 | M2 · Read the marker's `vault_path:` key | 2 |
  ```

  A line under the table on why each cut stands alone. Absent on the skip path.
- `### Totals` — a table with the columns `Milestone`, `Before`, `After`, one row per milestone and
  a bold `**Sprint**` row. Every After figure is summed from the updated plan's own tasks, never
  carried over from the draft. A line under the table on what actually moved. Absent on the skip
  path.
- `### Split candidate` — written when the sprint total is at or over the split threshold, or when
  the verdict is `Refined`. A `Skipped` verdict on a sprint under the split threshold carries no
  such subsection at all — not even a line saying no split is recommended: the verdict has already
  said both figures, and the heading is dropped with them.

  At or over the split threshold: the seam, the primary and the sibling with their milestone ranges
  and SP, and why the seam holds. The primary and the sibling are one bullet each, opening with the
  bare bold label — `**Primary**` and `**Sibling**`, the bold closing before the em dash — with the
  milestone range and its SP on that same line:

  ```
  - **Primary** — Local vault path resolution — M1–M3, 22 SP.
  - **Sibling** — Scaffold a repo-local vault — M4–M5, 16 SP.
  ```

  `Refined` with the total under the split threshold: the single line that the total is under the
  threshold and no split is recommended, no bullets under it.

## Return format

Refined path — the plan entry and the index entry, each annotated with the verdict and its counts:

```
## Changed:

- [UPDATED] plans/{slug}/plan.md — 2 tasks re-decomposed into 4, totals re-summed
- [UPDATED] plans/{slug}/index.md — refinement: refined

## Notes:

- 2 task(s) at or over the re-decompose threshold split into 4; largest surviving task 4 SP
- sprint total 38 SP, unchanged by the split — both oversized tasks landed on 2 + 3
- split candidate: primary M1–M3 (22 SP) / sibling M4–M5 (16 SP), seam between M3 and M4 — for
  present to put to the user
```

Skip path — the plan file is absent from `## Changed:` because nothing wrote to it:

```
## Changed:

- [UPDATED] plans/{slug}/index.md — refinement: skipped, nothing oversized

## Notes:

- no task at or over the re-decompose threshold; largest 3 SP
- sprint total 9 SP, under the split threshold; no split recommended
- plan file untouched
```

The plan stays out of `## Changed:` whenever nothing was re-decomposed — a sprint past the split
threshold with no oversized task still reports the one index entry, annotated
`refinement: skipped, nothing oversized, split candidate flagged`.

This step asks the user nothing and pauses the run for nothing: a sizing call that is theirs — take
the split or keep one sprint — travels as a `## Notes:` line for `present` to put to them. The
reply is these two sections alone: no prose before the first heading, nothing outside them, and no
`(none)` placeholder in an empty section.
