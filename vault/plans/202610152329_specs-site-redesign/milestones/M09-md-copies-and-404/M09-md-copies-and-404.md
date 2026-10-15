---
id: "09"
title: "Machine layer — .md copies and 404 page with --site-url"
sp: 3
status: done
plan: "plans/202610152329_specs-site-redesign/index.md"
---

# M09: Machine layer — .md copies and 404 page with --site-url

Every record page has its markdown source beside it and announces it, and a site built with `--site-url` carries a `404.html` whose links work at any depth Pages serves it from.

**Scope**: `pages.py` adds `{root}/{type}/{stem}.md` per record — the record file's bytes verbatim (`bytes`, written binary-safe by M01's `write_site`) — and `record.html.j2` adds `<link rel="alternate" type="text/markdown" href="{stem}.md">` in `<head>` (a `{% block head %}` in `base.html.j2`). `booping specs site` gains `--site-url URL` (`booping-python/src/booping/commands/specs.py`): http(s) only, else `error: …` exit 1, like `site-index`'s URL check; when given, `build_site` adds `404.html` from a new `templates/not_found.html.j2` — the shell with an empty sidebar selection, H1 `ui not_found`, a link `ui not_found_home` to `index.html` — with `<base href="{URL path, trailing slash}">` emitted right after `<meta charset>` and `prefix` empty (`../../clarifications.md` C9). The shipped Pages template `src/ci/gitlab/specs-site.gitlab-ci.yml` passes `--site-url "$CI_PAGES_URL"`. Without the flag no `404.html` is written.

Tests (integration, e2e): `booping-python/e2e/cases/specs/site-writes-md-copies-beside-records.txtar` — the `.md` equals the fixture record byte for byte, the record page carries the alternate link; `site-site-url-writes-a-404-with-base-href.txtar` — `--site-url https://lab.pages.example/proj` → `404.html` holds `<base href="/proj/">` and a link to `index.html`; `site-rejects-a-non-http-site-url.txtar` — `--site-url javascript:alert(1)` exits 1 with the error line.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 9.1 | `.md` copies and the alternate link; its e2e case. | `booping-python/src/booping/specs/site/pages.py`, `booping-python/src/booping/specs/site/templates/record.html.j2`, `booping-python/src/booping/specs/site/templates/base.html.j2`, `booping-python/e2e/cases/specs/site-writes-md-copies-beside-records.txtar` | 1 | done |
| 9.2 | `--site-url`, `not_found.html.j2`, `404.html`, the Pages template line; the two e2e cases. | `booping-python/src/booping/commands/specs.py`, `booping-python/src/booping/specs/site/pages.py`, `booping-python/src/booping/specs/site/templates/not_found.html.j2`, `src/ci/gitlab/specs-site.gitlab-ci.yml`, `booping-python/e2e/cases/specs/site-*.txtar` | 2 | done |

## Definition of Done

### Task 9.1

- [x] Every record page in the output has a sibling `.md` identical to its source file.

### Task 9.2

- [x] `booping specs site --help` lists `--site-url`.
- [x] `404.html` resolves its stylesheet, script and home link against the base path.
- [x] The three e2e cases pass.

Return: the list of changed and created files, nothing else.

## References

- `/home/anton/Dev/@A/shatterlings/crates/specs/src/site.rs` — `not_found` and `site_path` (lines ~968–979, ~1111–1119).
- `booping-python/e2e/cases/specs/site-index-rejects-a-javascript-url.txtar` — the URL-rejection case shape.

## Verify

`cd booping-python && uv run pytest e2e -k site -q`
