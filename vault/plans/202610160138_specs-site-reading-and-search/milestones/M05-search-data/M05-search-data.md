---
id: "05"
title: "Search data — search-index.js and search-body.js"
sp: 3
status: done
plan: "plans/202610160138_specs-site-reading-and-search/index.md"
---

# M05: Search data — search-index.js and search-body.js

The site writes `search-index.js` and `search-body.js`, the data the client search reads, in the exact format C6 locks.

**Scope**: new `booping-python/src/booping/specs/site/search.py` (`search_index_js(site, labels, states) -> str`, `search_body_js(site, rendered) -> str`), `markdown.py` (`Rendered.text`: the plain text C6 defines, collected in `render_body`), `pages.py` (`build_site` adds both files at the site root). Exactly `../../clarifications.md` C6. `machine.py`, `index.json` and `llms.txt` are not changed; `site-index` writes neither file.

Tests (integration, new `booping-python/tests/specs/site_search_test.py`): over a two-root fixture with a Russian record (`ё` in its title, a `[clarify]` mark, tags), `search-index.js` equals a hand-written expected string (prefix, compact JSON, `ensure_ascii=False`, page order, `flags` order, `null`s, trailing newline); `search-body.js` maps each id to the hand-derived plain text (marks kept as `[clarify]` text, whitespace collapsed); two builds give identical bytes. Add one e2e case `booping-python/e2e/cases/specs/site-writes-search-index-and-body.txtar` asserting both files' content over a one-root vault, then rebaseline the other `site-*.txtar` goldens and read the diff: the two new files only.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | `Rendered.text`; `search.py`; wiring in `build_site`; unit tests. | `booping-python/src/booping/specs/site/markdown.py`, `booping-python/src/booping/specs/site/search.py`, `booping-python/src/booping/specs/site/pages.py`, `booping-python/tests/specs/site_search_test.py` | 2 | done |
| 5.2 | New e2e case; golden rebaseline. | `booping-python/e2e/cases/specs/site-writes-search-index-and-body.txtar`, `booping-python/e2e/cases/specs/site-*.txtar` | 1 | done |

## Definition of Done

### Task 5.1

- [x] Both files match C6 byte for byte on the test fixtures, Cyrillic unescaped.
- [x] Output is identical across two builds.

### Task 5.2

- [x] The new txtar case passes and pins both files.
- [x] Other `site-*.txtar` goldens rebaselined; their diff is the two new files only.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/src/booping/specs/site/machine.py` — `index_json` / `llms_txt`: page-order iteration and JSON options to mirror.
- `booping-python/e2e/cases/specs/site-writes-llms-txt-and-index-json.txtar` — e2e case shape to copy.

## Verify

`cd booping-python && uv run pytest tests/specs/site_search_test.py e2e -k site -q`
