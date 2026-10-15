---
id: "06"
title: "Search UI \u2014 header combobox, phone overlay, search.html"
sp: 4
status: pending
plan: "plans/202610160138_specs-site-reading-and-search/index.md"
---

# M06: Search UI — header combobox, phone overlay, search.html

Every page's header gets a search box (`/` to focus, a keyboard dropdown), the phone gets a full-screen search overlay, and `search.html?q=` lists all results.

**Scope**: `booping-python/src/booping/specs/site/templates/base.html.j2` (the search form and listbox in the header when the page has the site's nav; the phone search `.iconbtn`; `<script src="{prefix}search.js" defer>`), new `templates/search.html.j2`, new `booping-python/src/booping/specs/site/search.js` (written to the site root like `site.js`), `pages.py` (`search.html`, the `search.js` asset, `data-prefix` for script and result URLs), `style.css` (box, dropdown, overlay, results), `src/config.yaml` (`search`, `search_placeholder`, `search_all`, `search_results` plural, `search_none`, `search_needs_js` in `en` and `ru`). Exactly `../../clarifications.md` C7. `search.js` reads only `window.SPECS_INDEX` / `window.SPECS_BODY` from M05's files. `site-index` pages and its template get no search markup.

Tests (integration, `booping-python/tests/specs/site_pages_test.py`): a record page's header holds the form with `action` to `search.html` at the right prefix, the combobox attributes of C7 and the `search.js` script; `search.html` exists, loads `search-index.js` and `search-body.js`, and holds the no-JS `search_needs_js` text with the `records.html` link; a `site-index` render has no search form and no `search.js`; labels resolve in `ru`. Rebaseline `site-*.txtar` goldens and read the diff: header search markup, `search.js`, `search.html` only.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | Header form, phone button, `search.html.j2`, pages and labels; tests. | `booping-python/src/booping/specs/site/templates/base.html.j2`, `booping-python/src/booping/specs/site/templates/search.html.j2`, `booping-python/src/booping/specs/site/pages.py`, `src/config.yaml`, `booping-python/tests/specs/site_pages_test.py` | 2 | pending |
| 6.2 | `search.js` — lazy loading, normalise/stem/score, combobox keys, `/`, overlay, `search.html` results; CSS; golden rebaseline. | `booping-python/src/booping/specs/site/search.js`, `booping-python/src/booping/specs/site/style.css`, `booping-python/e2e/cases/specs/site-*.txtar` | 2 | pending |

## Definition of Done

### Task 6.1

- [ ] Header and `search.html` markup as C7, at every page depth (`prefix` correct), `site-index` untouched.
- [ ] All new labels resolve in `en` and `ru`.

### Task 6.2

- [ ] `search.js` implements C7's normalisation, stem, AND matching, weights, order, lazy loading via `<script src>`, keys and overlay; no `fetch`, no dependency.
- [ ] Without JS the header form submits to `search.html`, which shows `search_needs_js`; everything else on every page is unchanged.
- [ ] From `file://` in headless Chromium: `решени` finds a record titled «Решение…», `елка` finds «Ёлка», Down/Enter opens the result, `/` focuses the box, at 390px the overlay opens and Esc returns focus — checked by the worker with headless Chromium (`/usr/bin/chromium`) over a site rendered to `/tmp` from a fixture holding those two titles, and again by the runner in Final Verification.
- [ ] Dropdown and overlay colours use existing tokens only (`site_contrast_test.py` green); `site-*.txtar` goldens rebaselined, diff as stated above.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/src/booping/specs/site/filter.js` — vanilla script style, `localeCompare` with the page `lang`, how a page-specific script is loaded.
- `../../../202610152329_specs-site-redesign/design/specs-site-mockup.html` — header `.search` box, `<kbd>/</kbd>` hint and the phone `.iconbtn`.
- https://www.w3.org/WAI/ARIA/apg/patterns/combobox/ — editable combobox with listbox popup.

## Verify

`cd booping-python && uv run pytest tests/specs/site_pages_test.py tests/specs/site_contrast_test.py e2e -k site -q`
