---
id: "10"
title: "site-index in the new design"
sp: 2
status: done
plan: "plans/202610152329_specs-site-redesign/index.md"
---

# M10: site-index in the new design

`booping specs site-index` renders its project list in the same design as the sites it links: shell, fonts, theme toggle, labels and `lang`.

**Scope**: `booping-python/src/booping/specs/site/index.py`, `templates/site_index.html.j2`, `booping-python/src/booping/commands/specs.py`. The index page uses M04's shell with no sidebar column (`.norail` and an empty `nav`, the grid collapsing to one column), H1 `title`, then `<ul class="rows">` with one `.row` per project — name linked to its URL, description below — in the existing sort order; zero projects keep the `No projects.` message, now `ui no_projects` (add the id to both label sets in `src/config.yaml`). `_run_site_index` loads labels and lang from `core.specs.site` like `_run_site` (M02). Output files: `index.html`, `style.css`, `fonts.css` and licences (M01), `site.js` (M04).

Tests (integration, e2e): rebaseline the `site-index-*.txtar` goldens and read the diff — only markup and the added files change, sort order and validation untouched; the existing title case still sets title, crumb and H1.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 10.1 | Index page on the shell with labels; `ui no_projects`. | `booping-python/src/booping/specs/site/index.py`, `booping-python/src/booping/specs/site/templates/site_index.html.j2`, `booping-python/src/booping/commands/specs.py`, `src/config.yaml` | 1 | done |
| 10.2 | Golden rebaseline of the site-index cases. | `booping-python/e2e/cases/specs/site-index-*.txtar` | 1 | done |

## Definition of Done

### Task 10.1

- [x] The index page has the skip link, header, theme toggle and footer of a site page, and no sidebar.

### Task 10.2

- [x] All `site-index-*.txtar` cases pass; their diffs touch markup and file lists only.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/src/booping/specs/site/templates/site_index.html.j2` — current page.
- `booping-python/e2e/cases/specs/site-index-renders-projects-sorted-from-a-yaml-file.txtar` — the golden to rebaseline.

## Verify

`cd booping-python && uv run pytest e2e -k site-index -q`
