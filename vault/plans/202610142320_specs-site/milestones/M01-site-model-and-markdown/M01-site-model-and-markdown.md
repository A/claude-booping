---
id: "01"
title: "Site model and markdown rendering"
sp: 10
status: pending
plan: "vault/plans/202610142320_specs-site/index.md"
---

# M01: Site model and markdown rendering

A pure in-memory layer loads the records of several named roots, resolves refs and body links across them, and renders a record body to HTML with heading anchors and highlighted marks — no file written, no CLI yet.

**Scope.** New package `booping-python/src/booping/specs/site/` (`__init__.py`, `model.py`, `markdown.py`), the `markdown-it-py` dependency in `booping-python/pyproject.toml` + `booping-python/uv.lock`, unit tests `booping-python/tests/specs/site_test.py`. Reuse, do not copy: `load_record` / `parse_filename` / `parse_ref` (`booping/specs/records.py`), `types` (`booping/specs/tiers.py`). The interface below is what M02 and M03 build on — keep the names.

- `SiteRoot(name: str, path: Path)` — `name` matches the namespace grammar of `parse_ref` (`[A-Za-z0-9][A-Za-z0-9._-]*`).
- `load_site(roots, known_types) -> Site` — for each root, each known type directory, each file `parse_filename` accepts, in order: roots as given, types as `known_types` orders them, number ascending. Unknown type directories and unparseable filenames are skipped silently (that is `specs check`'s job).
- `SiteRecord` — `root`, `type`, `number`, `slug`, `stem` (`NNNN-slug`), `ref` (`type/NNNN`), `path` (resolved, symlinks followed), `frontmatter`, `body`, `body_first_line` (file line of the first body line), `page` (`{root}/{type}/{stem}.html`).
- `Site.resolve_ref(text, from_root) -> SiteRecord | RefMiss` — `type/NNNN` looks in `from_root`; `ns:type/NNNN` looks in the root named `ns`. `RefMiss.warn` is true when the target root is rendered but the record is missing, false when the namespace names no rendered root (C6). Text that does not parse as a ref → `None`.
- `Site.resolve_link(dest, from_record) -> LinkTarget` — kinds `external` (has `://`, `mailto:`, or is absolute), `anchor` (`#…` only), `record` (local path, resolved against the record's directory with symlinks followed, equal to some record's `path`; carries the record and the `#anchor` if any), `offsite` (local path exists, not a record), `unresolved` (local path missing, or resolving it fails — a symlink loop raises in `Path.resolve`, caught and treated as missing). Percent-decoding as `booping/specs/links.py` does.
- `Site.backlinks(record) -> list[SiteRecord]` — distinct records that reach `record` through a frontmatter ref or a body link, in site order, the record itself excluded.
- `slug(text) -> str` — lowercase; drop every character that is not a letter, digit, `_`, `-` or space; spaces to `-`; repeated slugs in one body get `-1`, `-2`, … (GitHub's algorithm, so the `#anchors` records already write keep working).
- `render_body(text, *, first_line, id_prefix, link, statuses) -> Rendered` — markdown-it-py `commonmark` preset with `table` enabled and `html` off (raw HTML is escaped). Every heading gets `id="{id_prefix}{slug}"`. Every `[clarify]` / `[unknown]` literal in text outside code spans and code blocks is wrapped `<mark class="mk mk-clarify">[clarify]</mark>` / `mk-unknown`; the block (paragraph, list item, table cell's row) holding the first mark of its source line range gets `id="{id_prefix}L{n}"`, `n` the file line where the block starts. `link(dest) -> (href | None, css_class | None)` is called per link: `href` None renders the link text in a `<span>` of that class. `Rendered` = `html`, `marks: list[Mark(line, kind, text)]` (`text` = the block's plain text, whitespace collapsed, cut to 160 characters with a trailing `…` when longer), `links: list[(line, dest)]`.
- A table cell whose whole text is in `statuses` (the set of every `status` value in the site, `Site.statuses`) gets the same badge markup the record header uses — `<span class="badge st-{status}">{status}</span>` (an ADR's Alternatives table).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Add `markdown-it-py` (`>=4.2,<5`) and write `render_body` + `slug` | `booping-python/pyproject.toml`, `booping-python/uv.lock`, `booping-python/src/booping/specs/site/markdown.py`, `booping-python/src/booping/specs/site/__init__.py` | 4 | pending |
| 1.2 | Write the root/record model: `SiteRoot`, `SiteRecord`, `load_site`, `resolve_ref`, `resolve_link`, `backlinks` | `booping-python/src/booping/specs/site/model.py` | 4 | pending |
| 1.3 | Unit tests over the pure logic | `booping-python/tests/specs/site_test.py` | 2 | pending |

## Definition of Done

### Task 1.1

- [ ] `markdown-it-py` added with `uv add` in `booping-python/` (lock updated by uv, not by hand).
- [ ] `render_body` and `slug` behave as the Scope states, including escaped raw HTML and marks left alone inside code.
- [ ] No module-level state; two calls with the same input return identical strings.

### Task 1.2

- [ ] `load_site` order, `resolve_ref`, `resolve_link` kinds and `backlinks` behave as the Scope states.
- [ ] A link through a symlinked directory resolves to the same record as the direct path.

### Task 1.3

- [ ] Test surface: `render_body`, `slug`, `Site` over records written into `tmp_path`. Cases, parametrized where the surface is the same: slug of punctuation/mixed-case/duplicate headings; mark in text vs inside a code span vs a fenced block, with its `L{n}` id and cut text; raw `<script>` escaped; ref `type/NNNN` same root, `ns:type/NNNN` other root, missing record in a rendered root (`warn` true), unknown namespace (`warn` false); body link to a record with anchor, through a symlink, to an existing non-record file, to a missing file, into a symlink loop (→ `unresolved`), to a URL, to `#anchor`; backlinks from a frontmatter ref and a body link, deduped.
- [ ] Expected values are hand-written literals; no mocks — real files in `tmp_path`.

## References

- `booping-python/src/booping/specs/records.py` — record loading, filename and ref grammar to reuse.
- `booping-python/src/booping/specs/links.py` — local-link detection and percent-decoding.
- `booping-python/tests/specs/records_test.py` — test shape over `tmp_path` fixtures.

## Verify

`cd booping-python && uv run pytest tests/specs/site_test.py -q`

Return only: the list of changed files and the pytest summary line.
