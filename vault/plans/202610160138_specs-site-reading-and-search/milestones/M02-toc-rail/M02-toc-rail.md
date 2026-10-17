---
id: "02"
title: "On this page rail, open questions and the phone details"
sp: 3
status: done
plan: "plans/202610160138_specs-site-reading-and-search/index.md"
---

# M02: On this page rail, open questions and the phone details

A record page gets a sticky "On this page" rail with its open questions on wide screens, and the same blocks in one `<details>` under the lead below 1100px.

**Scope**: `booping-python/src/booping/specs/site/pages.py` (`_record_view` adds `toc` — `h2` entries with nested `h3` entries from `Rendered.headings`, then the "Referenced by" entry — and `questions` — the record's marks, clarify then unknown, each `{href: "#L{line}", kind, text}`), `templates/record.html.j2` (fills `{% block rail %}`; the `.toc-m` `<details>` after the lead), `templates/_macros.html.j2` (one `toc_blocks` macro used by both places), `site.js` (`IntersectionObserver` setting `aria-current="location"` on the rail link of the section in view), `style.css` (sticky rail, rail shown ≥ 1100px, `.toc-m` shown below it, phone styles). Exactly `../../clarifications.md` C3. Reuses labels `on_this_page`, `open_questions` (plural) and the `i-clarify` / `i-unknown` icons.

Tests (integration, `booping-python/tests/specs/site_pages_test.py`): a record with two `##`, one `###` and one `[clarify]` + one `[unknown]` mark renders a rail whose ToC nests the `###` under its `##`, ends with "Referenced by", and whose questions list links `#L{line}` clarify first; the same record renders a `.toc-m` `<details>` whose summary reads `On this page · 2 open questions`; a record with one heading and no marks renders no rail and no `.toc-m` and its page body has class `norail`. Rebaseline `site-*.txtar` goldens and read the diff: rail and `.toc-m` only.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | `toc` and `questions` in `_record_view`; `toc_blocks` macro; rail and `.toc-m` in `record.html.j2`; tests. | `booping-python/src/booping/specs/site/pages.py`, `booping-python/src/booping/specs/site/templates/record.html.j2`, `booping-python/src/booping/specs/site/templates/_macros.html.j2`, `booping-python/tests/specs/site_pages_test.py` | 2 | done |
| 2.2 | Sticky rail and breakpoints in CSS; scroll-spy in `site.js`; golden rebaseline. | `booping-python/src/booping/specs/site/style.css`, `booping-python/src/booping/specs/site/site.js`, `booping-python/e2e/cases/specs/site-*.txtar` | 1 | done |

## Definition of Done

### Task 2.1

- [x] Rail and `.toc-m` hold the same ToC and questions blocks, built once by `toc_blocks`.
- [x] Visibility rules of C3 hold on the test fixtures (ToC ≥ 2 entries, rail when either block exists).

### Task 2.2

- [x] Rail is sticky and visible at ≥ 1100px; below, the rail is hidden and `.toc-m` shown; no horizontal scroll at 390px.
- [x] Without JS no link is marked current; with JS exactly the section in view is marked.
- [x] `site-*.txtar` goldens rebaselined; their diff is the rail and `.toc-m` only.

Return: the list of changed and created files, nothing else.

## References

- `../../../202610152329_specs-site-redesign/design/specs-site-mockup.html` — `.rail`, `.rail .q`, `.toc-m` markup and CSS (`rail()` and record page functions).
- `booping-python/src/booping/specs/site/templates/base.html.j2` — the existing `rail_html` / `{% block rail %}` / `norail` plumbing.

## Verify

`cd booping-python && uv run pytest tests/specs/site_pages_test.py e2e -k site -q`
