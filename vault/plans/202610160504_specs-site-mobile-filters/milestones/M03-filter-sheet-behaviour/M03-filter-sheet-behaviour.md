---
id: "03"
title: "Filter sheet, compact row and removable chips behaviour"
sp: 4
status: done
plan: "/home/anton/Dev/@A/claude-booping-specs/vault/plans/202610160504_specs-site-mobile-filters/index.md"
---

# M03: Filter sheet, compact row and removable chips behaviour

On a phone the compact row names the pressed-filter count and the sort, opens the sheet where chips and sort apply live, and the active filters show under it as small chips that remove themselves on tap.

**Scope**: new `booping-python/src/booping/specs/site/filter-format.js`, `booping-python/src/booping/specs/site/filter.js`, `booping-python/src/booping/specs/site/pages.py` (ship the new file), the filtered page templates' script tags, new `booping-python/tests/specs/site_filter_format_test.py`, `booping-python/tests/specs/site_pages_test.py`, the `booping-python/e2e/cases/specs/site-*.txtar` goldens. Exactly `../../clarifications.md` C3, C4, C6, on the M02 markup:

- `filter-format.js` (pure, no DOM, copying `comments-format.js`'s shape) defines `SpecsFilters.row(label, pressedCount, sortText)` → the compact-row string, and `SpecsFilters.removable(pressed, removeTemplate)` → for `pressed` = `[{key, value, label}]` in chip order, `[{key, value, text, aria}]` with `text` = `label` and `aria` = `removeTemplate` with `{label}` filled. It is shipped beside `filter.js` by `build_site` and loaded (`defer`, before `filter.js`) by exactly the pages that load `filter.js`; `filter.js` calls it for both strings.

- `button.filter-open` text after every `apply()` = `SpecsFilters.row(...)`: `data-label`, then ` ({n})` when `n` > 0 (`n` = pressed chips), then ` · ` and the selected sort option's text.
- `div.filter-active` re-rendered after every `apply()`: one `button.chip.chip-x` per pressed chip in DOM order, text = the chip's label without its `.n` count, then a `×` in `span` with `aria-hidden="true"`, `aria-label` = `data-remove` with `{label}` filled; click → un-press the source chip, `apply()`, `write()`, then focus the next `.chip-x` or, when none is left, `button.filter-open`. All text via `textContent`.
- Sheet: `button.filter-open` click → `sheet.showModal()`; `.filter-close`, `.filter-done`, Escape (native) and a click on the backdrop (target is the dialog itself) → `sheet.close()`; on close focus returns to `button.filter-open`; a `matchMedia("(max-width: 760px)")` change to not-matching closes an open sheet. Chip and sort changes inside the sheet go through the existing handlers (live apply, hash write).
- Everything else in `filter.js` (facets, sorts, hash format, `read()` on `hashchange`, `p.empty` found as `bar.nextElementSibling`) unchanged; a page without `.filter-sheet` keeps working (guard every new lookup).

Tests: `site_filter_format_test.py` (unit, node runs the shipped `filter-format.js`, the `site_comments_format_test.py` runner pattern; a missing `node` fails, never skips) — `row("Filters", 0, "Review order")` = `Filters · Review order`; `row("Filters", 2, "By title")` = `Filters (2) · By title`; `row("Фильтры", 1, "Для ревью")` = `Фильтры (1) · Для ревью`; `removable` keeps input order, fills `{label}` in `Remove filter: {label}` and `Убрать фильтр: {label}`, and returns `[]` for none; expectations hand-written. `site_pages_test.py::test_filter_script_is_written_and_loaded_only_by_filtered_pages` extended to `filter-format.js`. The DOM wiring (sheet, focus, chip removal) is held by the worker's headless check (DoD) and the runner's browser check (index Final Verification). The `site-*.txtar` goldens change in the shipped `filter.js`, the new `filter-format.js` and the filtered pages' script tags.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | `filter-format.js`, shipped and loaded by filtered pages; its node test. | `booping-python/src/booping/specs/site/filter-format.js`, `booping-python/src/booping/specs/site/pages.py`, `booping-python/src/booping/specs/site/templates/*.html.j2` (filtered pages' script tags), `booping-python/tests/specs/site_filter_format_test.py`, `booping-python/tests/specs/site_pages_test.py` | 1 | done |
| 3.2 | Compact-row text and the removable active chips. | `booping-python/src/booping/specs/site/filter.js` | 2 | done |
| 3.3 | Sheet open/close, focus return, breakpoint close; golden rebaseline. | `booping-python/src/booping/specs/site/filter.js`, `booping-python/e2e/cases/specs/site-*.txtar` | 1 | done |

## Definition of Done

### Task 3.1

- [x] `site_filter_format_test.py` passes and fails when either function's output changes.
- [x] `filter-format.js` is written and loaded by exactly the pages that load `filter.js`.

### Task 3.2

- [x] In headless Chromium at 390px on `review.html#flag=unreviewed` (built from this repo), the row reads `Filters (1) · Review order` and one removable chip shows the flag's label; tapping it empties the active row, the row reads `Filters · Review order`, the hash loses `flag=` and every row is visible again.
- [x] Pressing two chips in the sheet shows `Filters (2) · …` and two removable chips in chip order.

### Task 3.3

- [x] The row opens the sheet as a bottom sheet; the close button, the "Show records" button, Escape and a backdrop tap each close it and focus returns to the row; resizing to 1300px with the sheet open closes it and the inline bar shows.
- [x] `site-*.txtar` rebaselined with `just e2e -k site --txtar-update`; diff limited to the `filter.js` and `filter-format.js` bodies and the filtered pages' script tags.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/src/booping/specs/site/comments-format.js` and `booping-python/tests/specs/site_comments_format_test.py` — the pure-module and node-runner shape to copy.
- `booping-python/src/booping/specs/site/comments.js` — `showModal()` / `close()` and focus return for `dialog.cmt-sheet`.
- `booping-python/src/booping/specs/site/filter.js` — `active()`, `apply()`, `write()`: the state the new code reads.
- `../../clarifications.md` — C3, C4, C6.

## Verify

`cd booping-python && uv run pytest tests/specs/site_filter_format_test.py tests/specs/site_pages_test.py e2e -k site -q`
