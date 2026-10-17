# Feedback — M02-compact-chips-and-filter-sheet-markup

**Blocked (1/2)**: coarse-pointer chip hit area is 42px tall, DoD 2.2 requires ≥ 44px.

- Checked (runner, resumed run): Verify green — `site_pages_test.py`, `site_contrast_test.py`, `e2e -k site` 122 passed. Markup, labels, compact chips, inline sheet at 1300px, compact row at 390px with JS: all as the contract says.
- Wrong: in headless Chromium at 390px with touch emulation (`pointer: coarse` matches), sheet open, `elementFromPoint` 7px above each chip returns the chip, 6.5px below returns the parent `.chips` / the dialog. `.chip::before { inset: -7px -2px }` is positioned against the chip's padding box, so the 1px border eats 1px each side: hit area = 28 + 2×7 = 42px.
- Next attempt: make the coarse-pointer hit area reach ≥ 44px tall, 7px beyond the chip's border box above and below (e.g. `inset: -8px -2px`). Keep everything else of the tree as it is; re-run Verify.
- Not a fix target: with JS disabled the whole `.filters` bar is hidden by the pre-existing `html:not(.js) .filters { display: none; }` — leave it.
