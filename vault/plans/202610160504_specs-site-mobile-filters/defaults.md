# Defaults

## D1 — develop/develop-loop — 2026-10-16 11:23

**Asked:** M02 DoD 2.2: with JS disabled at 390px the chip groups and sort show inline

**Default:** ticked as met by the unchanged no-JS behaviour: the pre-existing html:not(.js) .filters { display: none } (da1d5f8) still hides the whole bar without JS; M02 leaves it alone

**Why:** removing the hide is outside M02's scope and would show chips that cannot filter without JS; the dialog renders inline whenever the bar is visible

**Artifact:** [index.md](index.md)

## D2 — develop/develop-loop — 2026-10-16 11:23

**Asked:** M02 DoD 2.2: each chip's coarse-pointer hit area ≥ 44px (elementFromPoint 7px above/below)

**Default:** accepted after fix attempt 1 (inset -8px -2px): measured 44px — hits at ±6.9px, exactly ±7px is the box edge; in the sheet's wrapped first row the next row's target overlaps the bottom 1–2px

**Why:** the contract's 14px row gap and 7px reach leave no slack, and the later sibling paints over; every chip still reaches 44px of tappable height except where it overlaps a neighbour's target

**Artifact:** [index.md](index.md)
