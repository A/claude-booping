---
id: "02"
title: "Compact chips and the filter sheet markup"
sp: 4
status: in-progress
plan: "/home/anton/Dev/@A/claude-booping-specs/vault/plans/202610160504_specs-site-mobile-filters/index.md"
---

# M02: Compact chips and the filter sheet markup

Chips are compact at every width with touch-sized hit areas, and every filtered list page carries the compact filter row and the filter sheet — inline and unchanged in look on desktop and without JS, a hidden-until-opened bottom sheet on phones.

**Scope**: `booping-python/src/booping/specs/site/templates/_macros.html.j2` (`filter_bar`), `src/config.yaml` (`core.specs.site.labels.{en,ru}.ui`), `booping-python/src/booping/specs/site/style.css`, `booping-python/tests/specs/site_pages_test.py`, the `booping-python/e2e/cases/specs/site-*.txtar` goldens. Exactly `../../clarifications.md` C1, C3, C5, C6:

- `filter_bar` becomes, inside `div.filters`: `button.filter-open` (`type="button"`, `aria-haspopup="dialog"`, `data-label="{{ ui('filters') }}"`, text `{{ ui('filters') }}`), `div.filter-active` (empty; `data-remove="{{ ui('filter_remove') }}"`), then `dialog.filter-sheet` (`aria-label` = `filters`) holding `div.filter-head` (`h2` `filters` + `button.iconbtn.filter-close` with `aria-label` = `close`, the comment sheet's close icon), the existing `.chips` groups each preceded by a `p.facet` with the facet label, the existing sort `label`, and `button.filter-done` (`filters_show`); the `.count` line stays inside `div.filters` after the dialog; `p.empty` stays where it is today, the next sibling after `div.filters` (`filter.js` finds it as `bar.nextElementSibling`). Chip, sort and data attributes keep their current names and values (`filter.js` and the hash format do not change here).
- Labels: `filters`, `filter_remove` (with `{label}`), `filters_show` in both language blocks, beside `facet_*` (C3 wording).
- CSS, every width: `.chip` per C5 (30px, `2px 10px`, 13px, inner gap 4px), `.chips` gap 6px; `@media (pointer: coarse) { .chip { position: relative; } .chip::before { content: ""; position: absolute; inset: -7px -2px; } }`; the phone rule `.chip { min-height: 44px }` and the sideways-scrolling `.chips` phone rules removed. `dialog.filter-sheet:not(:modal)` is a static inline block with the dialog chrome reset (`display: block; position: static; padding: 0; border: 0; background: none; color: inherit; max-width: none;`); `.filter-head`, `.facet`, `.filter-done` are hidden unless `.filter-sheet:modal`; `.filter-open` and `.filter-active` hidden everywhere except `html.js` at `max-width: 760px`.
- CSS, `html.js` at `max-width: 760px`: `dialog.filter-sheet:not([open])` hidden; `.filter-open` a full-width 44px row with the sort select gone from the page; `.filter-active` a wrapping row of chips (gap 6px row 14px) that takes no space when empty; `dialog.filter-sheet:modal` as `dialog.cmt-sheet`'s bottom sheet (full width, `margin: auto 0 0`, `max-height: 80vh`, rounded top, inner scroll, `::backdrop` dimmed, `cmt-up` slide-in, none under `prefers-reduced-motion`), chip groups wrapping with row gap 14px, `.filter-done` full width 44px at the bottom.

Tests (integration, the built site — `site_pages_test.py`): on `records.html` the `.filters` holds `button.filter-open`, `div.filter-active`, and a `dialog.filter-sheet` containing every `.chips` group and `select.sort`, with `.count` outside the dialog; the type and review pages carry the same; the Russian site renders `Фильтры`, `Показать записи` and `Убрать фильтр: {label}` in the expected attributes (extend `test_russian_filter_labels`); expectations hand-written. `site_contrast_test.py` stays green.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | `filter_bar` markup and the three labels in both languages; page tests. | `booping-python/src/booping/specs/site/templates/_macros.html.j2`, `src/config.yaml`, `booping-python/tests/specs/site_pages_test.py` | 2 | pending |
| 2.2 | Compact chips with coarse-pointer hit areas; inline sheet on desktop; phone compact row, active row and bottom sheet CSS; golden rebaseline. | `booping-python/src/booping/specs/site/style.css`, `booping-python/e2e/cases/specs/site-*.txtar` | 2 | pending |

## Definition of Done

### Task 2.1

- [ ] New `site_pages_test.py` cases pass and fail when the dialog wrapper or a label is removed.
- [ ] `filter.js` still filters and sorts unchanged (it finds `.chip` and `select.sort` by query inside `.filters`).

### Task 2.2

- [ ] In headless Chromium on a built site at 1300px the filter bar looks as before with chips 30px tall (no sheet head, no compact row); at 390px with JS the page shows the compact row and no chip groups or sort select; with JS disabled at 390px the chip groups and sort show inline.
- [ ] At 390px with touch emulation (`hasTouch`, `isMobile`) each chip's hit area is ≥ 44px tall (`elementFromPoint` 7px above and below the chip's box returns the chip).
- [ ] `site_contrast_test.py` passes.
- [ ] `site-*.txtar` rebaselined with `just e2e -k site --txtar-update`; diff limited to the filter markup, the three labels and `style.css`.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/src/booping/specs/site/templates/_comments.html.j2` — `dialog.cmt-sheet` and its close button: the shell to copy.
- `booping-python/src/booping/specs/site/style.css` — `dialog.cmt-sheet` rules and the `(pointer: coarse)` block (lines ~440–480).
- `../../clarifications.md` — C1, C3, C5, C6.

## Verify

`cd booping-python && uv run pytest tests/specs/site_pages_test.py tests/specs/site_contrast_test.py e2e -k site -q`
