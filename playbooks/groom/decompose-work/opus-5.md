# Refine the plan against the sizing thresholds

You receive the written plan — its milestones, its tasks with their DoD and Verify, and the story
points per task, per milestone and for the sprint — together with the re-decompose threshold, the
split threshold and the SP scale both are measured on. On a loopback re-entry you also receive the
user's rework and the estimate or milestone it targets, and a decomposition file already exists on
disk.

This is a refinement over the written plan, never a rewrite: split the tasks too large for one
agent briefing, re-sum the totals from the new leaves, flag the sibling shape when the sprint is
too large to hold together as one iteration — and touch nothing else. The user reads the plan
right after this pass, so a task left oversized here is one they read.

## Two thresholds, judged separately

The re-decompose threshold decides whether tasks are split. The split threshold decides whether a
split candidate is flagged. They are independent conditions and the verdict reports both, always: a
plan with nothing oversized can still sit past the split threshold, and a plan full of oversized
tasks can total well under it.

- **Refined** — at least one task sits at or over the re-decompose threshold. Split them, re-sum
  the totals, and write the split candidate section either way.
- **Skipped** — no task reaches the re-decompose threshold, and the plan file is not opened for
  writing at all. `Skipped` is a verdict on the splitting alone: when the sprint total is past the
  split threshold the file still carries its `## Split candidate`, and the verdict says so in the
  same breath.

Both figures are the input's and only the input's — name the two thresholds as it gives them, never
as numbers of your own. Measure a task as the plan estimated it; re-estimating a task down to dodge
a split is the one move this pass must never make.

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
  drops the section instead of restating them.

## The artifact

Write `decomposition.md` into the run workdir the input names — created on every path, never
omitted, never empty. Report it as `_runs/groom/{slug}/decomposition.md`, marked `[UPDATED]`
instead of `[CREATED]` when a re-entered run finds it already there; a re-entry rewrites the file
in place rather than appending a second round to it.

Write no frontmatter — the file opens at its H1, and on a re-entry whatever frontmatter is
already there is preserved byte for byte; the run's hooks own it. The H1 is
`# Decomposition — {slug}`, carrying the run slug the input names.

The sections, in this order, none extra:

- `## Verdict` — the word `Refined` or `Skipped`, an em dash, then the counts that decided it: how
  many tasks sat at or over the re-decompose threshold, and where the sprint total sits against the
  split threshold. Both thresholds named by their figures.

  ```
  Refined — 2 tasks sat at or over the {re-decompose threshold} SP threshold; the sprint totals
  38 SP, past the {split threshold} SP split threshold, so a split candidate is flagged.
  ```

  On the skip path the count of oversized tasks is zero, so the figure carrying it is the largest
  task's own SP — name it:

  ```
  Skipped — no task sits at or over the {re-decompose threshold} SP threshold (the largest is
  3 SP), and the sprint totals 9 SP, well under the {split threshold} SP split threshold. The
  plan file was not touched.
  ```
- `## Re-decomposed` — a table with the columns `Was`, `SP`, `Became`, `SP`: one row per oversized
  task naming what it was and its SP, its first replacement and that replacement's SP, then a row
  per further replacement with the `Was` cells left empty. Name every task by the milestone it
  sits in, in the `Was` and `Became` cells alike — a replacement carries its original's milestone:

  ```
  | M2 · Resolve the vault path from the marker | 5 | M2 · Read the marker's `vault_path:` key | 2 |
  ```

  A line under the table on why each cut stands alone. Absent when nothing was re-decomposed.
- `## Totals` — a table with the columns `Milestone`, `Before`, `After`, one row per milestone and
  a bold `**Sprint**` row. Every After figure is summed from the updated plan's own tasks, never
  carried over from the draft. A line under the table on what actually moved. Absent when nothing
  was re-decomposed.
- `## Split candidate` — written only when the sprint total is at or over the split threshold, or
  when the verdict is `Refined`. A `Skipped` verdict on a sprint under the split threshold carries
  no such section at all — not even a line saying no split is recommended: the verdict has already
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

Refined path — the plan entry and the decomposition entry, each annotated with the verdict and its
counts:

```
## Changed:

- [UPDATED] plans/{slug}.md — 2 tasks re-decomposed into 4, totals re-summed
- [CREATED] _runs/groom/{slug}/decomposition.md — refined

## Notes:

- 2 task(s) at or over the re-decompose threshold split into 4; largest surviving task 4 SP
- sprint total 38 SP, unchanged by the split — both oversized tasks landed on 2 + 3
- split candidate: primary M1–M3 (22 SP) / sibling M4–M5 (16 SP), seam between M3 and M4

## Questions:

1. Take the split at the M3 / M4 seam, or keep this as one 38 SP sprint?
```

Skip path — the plan file is absent from `## Changed:` because nothing wrote to it:

```
## Changed:

- [CREATED] _runs/groom/{slug}/decomposition.md — skipped: nothing oversized

## Notes:

- no task at or over the re-decompose threshold; largest 3 SP
- sprint total 9 SP, under the split threshold; no split recommended
- plan file untouched

## Questions:
```

The plan stays out of `## Changed:` whenever nothing was re-decomposed — a sprint past the split
threshold with no oversized task still reports the one `[CREATED]` line, annotated
`skipped: nothing oversized, split candidate flagged`.

`## Questions:` holds only the sizing calls that are the user's — take the split or keep one
sprint — one line each, and nothing the thresholds already decided. The reply to the harness is
these three sections alone: no prose before the first heading, nothing outside them, and no
`(none)` placeholder in an empty section.
