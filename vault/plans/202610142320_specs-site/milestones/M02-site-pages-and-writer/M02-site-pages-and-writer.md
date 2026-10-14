---
id: "02"
title: "Site pages, stylesheet and writer"
sp: 9
status: done
plan: "vault/plans/202610142320_specs-site/index.md"
---

# M02: Site pages, stylesheet and writer

A `Site` from M01 becomes a deterministic map of output files — top index, root indexes, type pages, record pages, one stylesheet — and a guarded writer puts that map on disk.

**Scope.** New `booping-python/src/booping/specs/site/pages.py`, `booping-python/src/booping/specs/site/write.py`, Jinja templates under `booping-python/src/booping/specs/site/templates/`, `booping-python/src/booping/specs/site/style.css`, tests `booping-python/tests/specs/site_pages_test.py`. Templates are Jinja2 with `autoescape=True`, loaded from the package directory; HTML is assembled only there, never by string concatenation in Python. The page content below is the locked contract (`index.md` → I/O contract); do not add pages, columns or sections.

- `build_site(site, known_types) -> dict[str, str]` — relative path → file content, pure. Paths: `style.css`, `index.html`, `{root}/index.html`, `{root}/{type}/index.html` for each type with at least one record in that root, `{root}/{type}/{stem}.html` per record.
- Every page: `<!doctype html>`, `<meta charset="utf-8">`, `<meta name="viewport" content="width=device-width, initial-scale=1">`, `<title>{page title} — specs</title>`, `<link rel="stylesheet" href="{prefix}style.css">` with `prefix` the `../` run up to the out root, a breadcrumb `<nav class="crumbs">` (`Specs` → `{root}` → `{type}` → `{type}/{NNNN}`, each but the last a relative link), no `<script>`, no external URL of the site's own.
- `index.html` — H1 `Specs`; one table: `Root` (link to the root index) | `Records` | one column per type present in any root, in `known_types` order (count linking to that root's type page; empty cell when 0) | `[clarify]` | `[unknown]` | `Unreviewed`.
- `{root}/index.html` — H1 `{root}`; a table `Type` (link) | `Records` | `[clarify]` | `[unknown]` | `Unreviewed`; then `<h2 id="marks">Marks</h2>` with `<h3>[clarify]</h3>` then `<h3>[unknown]</h3>`, each a list of every mark of that kind in site order: `<a href="{type}/{stem}.html#L{n}"><code>{type}/{NNNN}</code> {title}</a> — {mark text}`; a kind with none says `None.`
- `{root}/{type}/index.html` — H1 `{type}` with the record count; a contents list (`<code>{type}/{NNNN}</code>`, title linking to `#{stem}`, status badge); then every record in full as `<article id="{stem}">` holding the record block with an `h2` title linking to the record page, body rendered with `id_prefix="{stem}--"` and in-page `#anchor` links rewritten to `#{stem}--{anchor}`.
- `{root}/{type}/{stem}.html` — the record block with an `h1` title, body with an empty `id_prefix`; then `<h2 id="referenced-by">Referenced by</h2>` listing `Site.backlinks` as `<code>{ref}</code> {title}` links (prefixed `{root}:` when the source root differs), or `Nothing references this record.`
- Record block: title; a meta line — `<code>{type}/{NNNN}</code>`, `<span class="badge st-{status}">{status}</span>` (for a value with no status: its `kind` the same way), `<span class="badge unreviewed">unreviewed</span>` when `reviewed` is absent or empty, `<span class="chip mk-clarify">[clarify] {n}</span>` / `mk-unknown` when the record has marks; `summary` as `<p class="summary">`; a `<dl class="facts">` of every other frontmatter key in frontmatter order except `type`, `title`, `summary`, `status`, `kind` — a list renders item by item, an item that parses as a ref through `Site.resolve_ref`, any other value as escaped text (C7); then the body HTML. A link callback maps `Site.resolve_link` kinds to markup per C6: `record` → relative href to the record page (+ anchor), `external` → dest unchanged, `anchor` → as above per page kind, `offsite` → no href, class `offsite`, `unresolved` → no href, class `unresolved`.
- Warnings: `build_site` also returns (or exposes) the sorted list of `(path, line, message)` for each unresolved body link (`unresolved link {dest}`) and each frontmatter ref whose `RefMiss.warn` is true (`unresolved ref {ref}`) — each once per record, even though the record renders on two pages.
- `style.css` — system font stack, readable measure (~46rem main column), CSS variables with a `@media (prefers-color-scheme: dark)` override, badge colours grouped: `st-accepted st-live st-done st-resolved` good, `st-proposed st-planned st-open st-validating` in progress, `st-retired st-rejected st-superseded st-deferred` off, `st-value st-non-value` neutral, any other status the neutral fallback; `mark.mk-clarify` and `mark.mk-unknown` in two distinct colours, `.unresolved` struck/red-ish, `.offsite` muted; tables bordered and horizontally scrollable on narrow screens; `@media print` hides the breadcrumb.
- `write_site(files, out, roots) -> None` — refuses with `SiteError(message)` when: `out` is a file; `out` resolves inside any root's path; `out` exists, is non-empty and has no `.booping-site` marker. Otherwise creates `out` or removes its existing contents (marker case), writes the marker `.booping-site` containing `booping specs site\n` first — so a run that dies midway leaves a directory the next run may clear — then every file in sorted path order with `\n` line endings.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Templates and stylesheet | `booping-python/src/booping/specs/site/templates/*.html.j2`, `booping-python/src/booping/specs/site/style.css` | 4 | done |
| 2.2 | `build_site`: page assembly, link callback, counts, marks list, backlinks, warnings | `booping-python/src/booping/specs/site/pages.py` | 3 | done |
| 2.3 | `write_site` with the out-directory guards | `booping-python/src/booping/specs/site/write.py` | 2 | done |

## Definition of Done

### Task 2.1

- [x] Every page carries exactly the structure the Scope lists; no `<script>`, no absolute URL except a record's own external links.
- [x] Autoescape on; record text never reaches HTML unescaped except the `render_body` output.

### Task 2.2

- [x] `build_site` is a pure function: two calls over the same `Site` return equal maps.
- [x] Every relative `href` in every page resolves to a key of the map, and every `#fragment` to an `id` on the target page (the property the 2.3 tests assert).
- [x] Warnings are deduped per record and sorted by `(path, line)`.

### Task 2.3

- [x] Each refusal raises `SiteError` with a one-line message naming the path; nothing is written or removed on refusal.
- [x] A second run over a marked directory removes a page whose record was deleted.
- [x] The marker is on disk before the first page is written.

### Tests (part of 2.3's SP)

- [x] Test surface: `build_site` and `write_site` over a two-root fixture in `tmp_path` (a value, an ADR with frontmatter `values:` ref, a body link with anchor, a cross-root `ns:` ref, a `[clarify]` mark, an unresolved link). Cases: the link-integrity property over every page; the marks list entry and its `L{n}` target; backlinks on the value page; the cross-root ref href `../../{other}/value/{stem}.html`; warnings list; each `write_site` refusal (parametrized) and the marker rewrite. Hand-written expectations, real files, no mocks.

## References

- `booping-python/src/booping/rendering.py` — how the package builds its Jinja environment.
- `/home/anton/Dev/@A/shatterlings/crates/specs/site/style.css` — palette and badge/mark styling to port (CSS only; its Russian labels and filter input are not ported).
- `vault/plans/202610142320_specs-site/clarifications.md` — C3, C4, C6, C7.

## Verify

`cd booping-python && uv run pytest tests/specs/site_pages_test.py tests/specs/site_test.py -q`

Return only: the list of changed files and the pytest summary line.
