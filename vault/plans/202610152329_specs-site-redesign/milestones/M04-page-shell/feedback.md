# Feedback

## Final Verification — visual check, 2026-10-16

Found after the milestone closed, by the runner's headless-Chromium check of the swarmlight vault rendered with `lang: ru` at 390×844 (screenshots under `/tmp/shots/`, `*-m-*.png`).

- Phone breadcrumbs: on a type page and a record page the first crumb («Обзор») sits lower than the `›` separator and the last crumb — the items do not share a baseline (likely the 44px tap-target min-height applied to crumb links without aligning the row). The plan's Responsive line says the phone shows the last crumb level only; the render shows the first and the last.
- Drawer focus: at phone width, opening the drawer with the menu button puts focus on the skip link («Перейти к содержимому»), not the first sidebar link as the contract's drawer behaviour describes.
- Next attempt: fix both in `style.css` / `site.js` / `base.html.j2` per the mockup (`../../design/specs-site-mockup.html`); keep desktop crumbs unchanged; add or extend a test in `site_pages_test.py` where markup changes; rebaseline only goldens whose markup changes and read their diffs.
