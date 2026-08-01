---
status: done
reviewed_at: 20260731 19:52
fixtures_reviewed_at: 20260731 20:07
suite_reviewed_at: 20260731 20:34
---

[← index](../../index.md)

# decompose-work

## Contract

- **Delegation** — inline: the runner renders the step and performs it itself, in the main
  context.
- **Needs** —
  - the written plan — its milestones, its tasks with their DoD and Verify, and the story
    points per task, per milestone and for the sprint
  - the re-decompose threshold, the split threshold, and the SP scale both are measured on
  - the user's rework and the estimate or milestone it targets, when the run has looped back
    into decomposition
- **Value** — the plan is right-sized before the user ever reads it: every task sitting at or
  over the re-decompose threshold is broken into tasks a single agent briefing can carry, the
  totals are re-summed from the new leaves upward, and a sprint past the split threshold is
  flagged as a sibling *shape* rather than silently executed. The pass is a refinement over the
  written plan, never a rewrite — it splits tasks and re-sums, and touches nothing else. With no
  conditional edges in the framework, a plan that is already right-sized is answered with a skip
  note instead of an absent record, so `verify-references` and `present` never have to work out
  whether the pass ran.
- **Output files** —
  - `[UPDATED] plans/{slug}/index.md` — the `## Refinement` section, written on both paths,
    never omitted, never empty:
    - the verdict first — `Refined` or `Skipped`, with the counts that decided it: how many
      tasks were at or over the re-decompose threshold, and where the sprint total sits against
      the split threshold
    - `### Re-decomposed` — one row per oversized task: what it was and its SP, what it became
      and their SP; absent on the skip path
    - `### Totals` — per-milestone before and after, and the sprint total on both; absent on the
      skip path
    - `### Split candidate` — the seam, the primary and the sibling with their SP, and why the
      seam holds; or the one line that the total is under the threshold and no split is
      recommended
    - both thresholds are rendered from config into the prompt — the step never authors them as
      literals of its own
  - `[UPDATED] plans/{slug}/plan.md`, on the refined path only:
    - each oversized task replaced by the tasks it split into, each standing alone with its own
      DoD and its own Verify — no pair that only works when both land
    - milestone SP totals re-summed from the new tasks, the sprint total re-summed from the
      milestones, and the plan's `sp:` frontmatter set to that sprint total
    - nothing else changes — not the architecture, not the surviving tasks' DoD or Verify, not
      `summary:`, not the template sections the draft filled in
    - on the skip path the plan file is not opened for writing at all, and does not appear in
      the step report
  - no sibling plan and no backlog stub — a split is a recommendation here; `present` puts it to
    the user and each sibling is groomed in its own run
- **Step report** — `## Changed:` list, each entry annotated with the verdict and its counts;
  `## Notes:` — the re-decomposition count, the largest surviving task, the re-summed sprint
  total, and the split candidate or the note that none is recommended. A sizing call that is the
  user's travels as a note for `present` to ask — this step asks nothing itself.
- **Review gate** —
  - none — the user's first read of the plan happens at `present`, on the refined plan
  - the edge out of decomposing cannot fire while any task still sits at or over the
    re-decompose threshold, or while a milestone or sprint total does not sum from its parts
  - a change request from the approval gate that touches milestones, tasks or estimates loops
    the run back here; one that reopens an architecture call goes to design instead

## Example artifact

`plans/20260801-local-vault-directories/index.md`, the `## Refinement` section, refined path:

```markdown
## Refinement

Refined — 2 tasks sat at or over the 5 SP re-decompose threshold; the sprint totals 38 SP,
past the 35 SP split threshold, so a split candidate is flagged.

### Re-decomposed

| Was | SP | Became | SP |
| --- | --- | --- | --- |
| M2 · Resolve the vault path from the marker | 5 | M2 · Read the marker's `vault_path:` key | 2 |
| | | M2 · Resolve relative, absolute and `~` forms against the repo root | 3 |
| M4 · Scaffold a repo-local vault | 5 | M4 · Add the `--local [dir]` flag and its default | 3 |
| | | M4 · Write the marker key and the vault `.gitignore` | 2 |

Each half stands alone — its own DoD, its own Verify. Nothing is left half-configured between
the two.

### Totals

| Milestone | Before | After |
| --- | --- | --- |
| M1 · Marker discovery | 6 | 6 |
| M2 · Path resolution | 8 | 8 |
| M3 · Callers honour the override | 8 | 8 |
| M4 · Scaffolding | 8 | 8 |
| M5 · Docs and migration notes | 8 | 8 |
| **Sprint** | **38** | **38** |

Re-decomposition redistributes; it does not reduce. Both splits landed on 2 + 3, so every total
is unchanged — what changed is that the largest task is now 4 SP.

### Split candidate

The seam sits between M3 and M4: M1–M3 make the resolution behaviour work for a hand-written
marker, M4–M5 add the scaffolding that writes one. The second half is useless without the
first, and the first is shippable without the second.

- **Primary** — Local vault path resolution — M1–M3, 22 SP.
- **Sibling** — Scaffold a repo-local vault — M4–M5, 16 SP; parked as a `backlog` stub with
  `split_from:` pointing at the primary, groomed in its own run once the primary merges.
```

On the skip path the section carries the verdict alone:

```markdown
## Refinement

Skipped — no task sits at or over the 5 SP re-decompose threshold (the largest is 3 SP), and
the sprint totals 9 SP, well under the 35 SP split threshold. The plan file was not touched.
```

## Return Format

Refined path:

```markdown
## Changed:

- [UPDATED] plans/20260801-local-vault-directories/plan.md — 2 tasks re-decomposed into 4, totals re-summed
- [UPDATED] plans/20260801-local-vault-directories/index.md — refinement: refined

## Notes:

- 2 task(s) at or over the 5 SP threshold split into 4; largest surviving task 4 SP
- sprint total 38 SP, unchanged by the split — both oversized tasks landed on 2 + 3
- split candidate: primary M1–M3 (22 SP) / sibling M4–M5 (16 SP), seam between M3 and M4 — for
  present to put to the user
```

Skip path — the plan file is absent from `## Changed:` because nothing wrote to it:

```markdown
## Changed:

- [UPDATED] plans/20260801-fix-stale-session-cookie/index.md — refinement: skipped, nothing oversized

## Notes:

- no task at or over the 5 SP threshold; largest 3 SP
- sprint total 9 SP, under the 35 SP split threshold; no split recommended
- plan file untouched
```
