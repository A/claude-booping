---
id: "07"
title: "List pages — type, root and home pages as record and type lists"
sp: 3
status: done
plan: "plans/202610152329_specs-site-redesign/index.md"
---

# M07: List pages — type, root and home pages as record and type lists

Type pages list their records as scannable rows instead of concatenating full bodies, and the root and home pages list types as named reading scenarios instead of count matrices (`../../clarifications.md` C10).

**Scope**: `booping-python/src/booping/specs/site/templates/type.html.j2`, `root.html.j2`, `index.html.j2`, `_macros.html.j2`, `pages.py`. Type page: H1 `labels.type_plural(type)`, `<p class="lead">` the type's scenario, then `<ul class="rows">` with one `<li class="row">` per record in page order — `<code class="ref">` ref, `<a>` title to the record page, the summary below it, `state_badges(state)` on the right (mockup `.row`, `.why`). Root page: H1 root name, `<ul class="types">` with one item per type — plural label linked to the type page, the scenario line, the record count (`ui records`) — then the existing marks list as rows (`icon` + mark text + link to `{record}#L{n}` + record title). Home (`index.html`): H1 `site_title`, then per root an H2 with the root name and the same types list; the tier × type matrix and its count cells go. Remove the second, `stem--`-prefixed body render and the `id_prefix` path in `build_site` and `_link_renderer` — no page embeds a body any more; `render_body` keeps its `id_prefix` parameter only if another caller uses it, otherwise drop it with its tests. The `specs site` stdout line keeps its shape; its page count reflects the HTML pages written.

Tests (integration): `site_pages_test.py` — a type page holds one `.row` per record and no record body text; the home page holds no `<table>`; the root page lists each type with its count and each mark with a working `#L{n}` link (the `_Links` checker); `test_build_is_repeatable` still passes. Rebaseline `site-*.txtar` goldens and read the diff: type, root and home pages change, record pages do not.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | Type page as rows; drop the prefixed second render. | `booping-python/src/booping/specs/site/templates/type.html.j2`, `booping-python/src/booping/specs/site/pages.py`, `booping-python/src/booping/specs/site/markdown.py` | 2 | done |
| 7.2 | Root and home pages as type lists with scenarios; tests; golden rebaseline. | `booping-python/src/booping/specs/site/templates/root.html.j2`, `booping-python/src/booping/specs/site/templates/index.html.j2`, `booping-python/src/booping/specs/site/templates/_macros.html.j2`, `booping-python/tests/specs/site_pages_test.py`, `booping-python/e2e/cases/specs/site-*.txtar` | 1 | done |

## Definition of Done

### Task 7.1

- [x] Each record body is rendered once per build.
- [x] A type page's size grows with its record count by one row each, not by body length.

### Task 7.2

- [x] No page in the output contains a count matrix table.
- [x] The new tests pass; rebaselined goldens differ only on type, root and home pages.

Return: the list of changed and created files, nothing else.

## References

- `../../design/specs-site-mockup.html` — `list()` rows and `home()` scenario list markup.
- `booping-python/src/booping/specs/site/templates/root.html.j2` — the marks list being restyled.

## Verify

`cd booping-python && uv run pytest tests/specs e2e -k site -q`
