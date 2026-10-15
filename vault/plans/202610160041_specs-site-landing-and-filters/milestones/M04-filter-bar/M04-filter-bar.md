---
id: "04"
title: "Filter bar — chips, sort, hash state in filter.js"
sp: 4
status: pending
plan: "plans/202610160041_specs-site-landing-and-filters/index.md"
---

# M04: Filter bar — chips, sort, hash state in filter.js

Type pages and `records.html` get filter chips and a sort control whose state lives in `location.hash`, so a filtered view is a link.

**Scope**: `booping-python/src/booping/specs/site/templates/_macros.html.j2` (`filter_bar` macro), `templates/type.html.j2`, `templates/records.html.j2`, `templates/base.html.j2` (an optional `scripts` block), `booping-python/src/booping/specs/site/filter.js` (new, written to the output root like `site.js`), `pages.py`, `style.css`, `src/config.yaml` labels. Exactly `../../clarifications.md` C3. Server side: `filter_facets(rows, facets, flags) -> list[Facet(key, chips: [Chip(value, label, count)])]` in `pages.py` computing chips and counts from the page's rows (C3 rendering rules: count-0 chips dropped, facets with fewer than two chips dropped except `flag`); chip labels from labels (type plural, root name, status label, flag label with its icon from the sprite). `filter_bar` renders `<div class="filters" data-default-sort="{sort}">`: per facet a labelled group (`role="group" aria-label`) of `<button type="button" class="chip" data-key data-value aria-pressed="false">` icon + label + `<span class="n">count</span>`; a labelled `<select class="sort">` with the page's sort options; a `<p class="count" role="status">` with the visible-row count (plural label); an empty-state `<p class="empty" hidden>` (label "Nothing matches the filter"). `filter.js` (vanilla, no dependencies, one IIFE, ≤ ~120 lines): parse the hash → set `aria-pressed` and the select; filter `.row` elements by their `data-*` (OR within a facet, AND across; `data-flags` is a space list); sort by moving row nodes (keys from `data-order`, `data-updated`, `data-title` with `localeCompare(…, document.documentElement.lang)`, `data-created-by` for `review`); update count and empty state; on chip click / select change write the hash via `history.replaceState` (bare path when default); listen to `hashchange`. Without JS: CSS `html:not(.js) .filters { display: none }`, all rows visible. Pages without a filter bar do not load `filter.js`.

Tests (integration, `site_pages_test.py`): a type page's chip set and counts for a fixture with two statuses and one flagged record are hand-derived (no `type` facet; no `source` facet with one root); `records.html` with two roots renders a `source` facet; chip `data-value`s equal the row attribute values they filter; `filter.js` is written and referenced only by pages with a filter bar; `test_build_is_repeatable` passes. Rebaseline `site-*.txtar` goldens and read the diff: filter bars and `filter.js` only.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | `filter_facets` and `filter_bar` on type pages and `records.html`; labels en/ru; tests. | `booping-python/src/booping/specs/site/pages.py`, `booping-python/src/booping/specs/site/templates/_macros.html.j2`, `booping-python/src/booping/specs/site/templates/type.html.j2`, `booping-python/src/booping/specs/site/templates/records.html.j2`, `src/config.yaml`, `booping-python/tests/specs/site_pages_test.py` | 2 | pending |
| 4.2 | `filter.js`, loading it from `base.html.j2`, no-JS CSS; golden rebaseline. | `booping-python/src/booping/specs/site/filter.js`, `booping-python/src/booping/specs/site/templates/base.html.j2`, `booping-python/src/booping/specs/site/style.css`, `booping-python/src/booping/specs/site/pages.py`, `booping-python/e2e/cases/specs/site-*.txtar` | 2 | pending |

## Definition of Done

### Task 4.1

- [ ] Chips, counts and facet visibility follow C3 on the test fixtures.
- [ ] Every chip and sort option label resolves from labels in `en` and `ru`.

### Task 4.2

- [ ] `filter.js` implements C3's semantics, hash format, `replaceState` and `hashchange` handling.
- [ ] Without the `js` class the filter bar is hidden and every row is visible.
- [ ] Opening `{root}/{type}/index.html#status=accepted` from `file://` in headless Chromium shows only accepted rows (runner checks in Final Verification).

Return: the list of changed and created files, nothing else.

## References

- `../../../202610152329_specs-site-redesign/design/specs-site-mockup.html` — `.chip`, `.chips`, `aria-pressed` styling and `FILTERS` behaviour (its flat AND is replaced by C3).
- `booping-python/src/booping/specs/site/site.js` — script style and how a static asset is written.

## Verify

`cd booping-python && uv run pytest tests/specs/site_pages_test.py e2e -k site -q`
