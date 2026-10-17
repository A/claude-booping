---
type: adr
title: A script cuts the drafted plan into milestone files
summary: The script `booping plan split` cuts the one-file plan on its milestone headings, byte for byte, into index.md and the milestone files; a model splits only what the script flags.
created_by: claude
created_at: 2026-10-16
updated_at: 2026-10-18
status: accepted
values: [value/0015, value/0012, value/0010]
issues: []
sources: [vault/idea/0003-groom-depth-scales-with-task.md]
---

## Context

Groom drafts the whole plan as one file (adr/0030), while develop reads `index.md` plus one file
per milestone (`milestones/M{nn}-*/`) for per-milestone status, feedback and delegation, and packs
milestones into briefings by SP (adr/0022). Something has to turn the draft into that layout without
changing the plan's text. The 9 milestone-shape rules the model misses even when told (adr/0030)
also need a place other than the prompt.

A split benchmark (`booping-benchmarks/groom/split/report.md`) took 12 single-file plans from the
groom benchmark (V3 and V3a on s1, m2, c1) and scored each way of splitting: structure of the files,
coverage of the plan's lines, invented lines, SP groups, cost.

| Way | Plans passing every threshold | Coverage / invention | Cost / time per plan |
|---|---|---|---|
| Script on the plan's headings | 12 / 12 | 100% / 0% | $0 / under 1 s |
| Sonnet writes the files | 12 / 12 | 99.8% / 0.1% | $0.71 / 4.6 min |
| Haiku maps line ranges, a script cuts | 8 / 12 | 99.8% / 0% | $0.34 / 3.6 min |
| Haiku writes the files | 6 / 12 | 98.2% / 1.5% | $0.25 / 4 min |

All 12 plans carried milestone headings with Tasks / DoD / References / Verify sub-headings; SP came
from frontmatter or the milestone table. Haiku rewriting dropped labels, joined lines and garbled a
diagram on long plans; its line maps drifted by 1–2 lines and put DoD under Tasks.

## Criteria

- The plan's text reaches the milestone files unchanged.
- Develop and the worker agents read the same layout as today.
- Cheap enough to run on every plan.

## Decision

`booping plan split` cuts the drafted plan on its milestone headings (`### M{nn} — <title>` with
`sp:`, `depends_on:` and the sub-headings Tasks, Definition of Done, References, Verify), byte for
byte, into `index.md` and the milestone files; it writes the milestone table and the SP groups
(adr/0022) and never splits a code fence. It exits non-zero when the plan has no milestone headings
and flags a milestone without `sp`; only such a plan goes to a model (Opus) for the split. After
the split booping checks the milestone contract — one Verify command, named files, DoD per task —
and a failing milestone goes back to the draft with the finding.
The benchmark below measured Sonnet; the fallback runs on Opus, because rewriting a draft is
judgement work ([rule/0031](../rule/0031-judgement-runs-on-opus.md)).

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [Script on headings](#script-on-headings) | accepted | medium | high | Exact and free on all 12 plans |
| [Sonnet writes the files](#sonnet-writes-the-files) | rejected | low | high | Passes, but pays $0.71 a plan for what a script does; a model split, on Opus, is kept as the fallback |
| [Haiku maps, a script cuts](#haiku-maps-a-script-cuts) | rejected | medium | high | Line numbers drift; sections land wrong |
| [Haiku writes the files](#haiku-writes-the-files) | rejected | low | high | Edits the plan's text on long plans |

### Script on headings

A deterministic cut on the headings the draft prompt fixes.

- **Pros:** 100% coverage and 0% invention by construction; free; testable with e2e cases on real
  plan shapes; failures are explicit exit codes.
- **Cons:** the plan format is a hard contract for the drafting model; placement inside a milestone
  is only as right as the draft's own sub-headings.
- **Complexity:** medium — a new command, its tests, the contract check.
- **Reversibility:** high.

### Sonnet writes the files

A model reads the plan and writes `index.md` and the milestone files.

- **Pros:** passes every threshold on all 12; needs no fixed format.
- **Cons:** $0.71 and 4.6 minutes on every plan; a model copy can still drift.
- **Complexity:** low.
- **Reversibility:** high.

### Haiku maps, a script cuts

Haiku returns line ranges per milestone section and the groups; a script slices them.

- **Pros:** no rewritten text (0% invention).
- **Cons:** no first map met the every-line-once rule; boundaries drift by 1–2 lines, splitting
  code fences and putting DoD under Tasks; 8/12.
- **Complexity:** medium.
- **Reversibility:** high.

### Haiku writes the files

The cheapest model rewrites the plan into the files.

- **Pros:** cheapest model call.
- **Cons:** removes labels, joins lines, rewords assumptions, garbles diagrams on long plans; 6/12.
- **Complexity:** low.
- **Reversibility:** high.

## Consequences

- New `booping plan split`, with e2e cases on real plan shapes including the 12 benchmark plans;
  groom calls it after the draft.
- `_partials/milestone_contract.md` turns into the post-split check.
- Develop, `pi-developer`, `booping-developer` and `develop-pi` keep reading the
  milestone files as they are.
- Renaming the milestone file to `milestones/M{nn}-*/index.md` (owner, 2026-10-16) is a separate
  change with its own migration.
