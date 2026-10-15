---
id: "01"
title: "site-index \u2014 the index page from a YAML project file"
sp: 4
status: pending
plan: "plans/202610152242_specs-sites-gitlab-pages/index.md"
---

# M01: site-index — the index page from a YAML project file

`booping specs site-index --projects FILE --out DIR` renders one index page in the specs site's look from a YAML list of projects, byte-identical for the same input.

**Scope**: new verb `site-index` under `booping specs` in `booping-python/src/booping/commands/specs.py` — flags `--projects PATH` (required in this milestone, read as a YAML file; M02 adds `-` for stdin JSON and makes it the default), `--out DIR` (default `specs-site-index`), `--title TEXT` (default `Specs`). New module `booping-python/src/booping/specs/site/index.py`: `Project` (frozen dataclass `name`, `url`, `description`), `load_projects(data) -> list[Project]` over an already-parsed value (this milestone: list of mappings with `name`, `url`, optional `description`; full validation is M02), `build_index(projects, title) -> dict[str, str]` returning `index.html` and `style.css`. Rendering reuses the site's Jinja environment: rename the private `_env()` in `pages.py` to public `environment()` (update its callers in `pages.py`) and import it in `index.py`; the page uses the `Crumb` dataclass from `pages.py` and extends `base.html.j2`; new template `templates/site_index.html.j2` extends it. `style.css` is the site's file, byte-identical. Writing goes through `write.write_site(files, out, [])` — same `.booping-site` marker and non-empty-out refusal. Output content is locked in `../../clarifications.md` C3: entries sorted by `(name.casefold(), name)`; description whitespace collapsed to single spaces and stripped; `<title>{title} — specs</title>`, one crumb `{title}` with no link, `<h1>{title}</h1>`, then `<div class="table-wrap"><table>` with header `Project | Description` and one row per project, the name an `<a href>` to the URL (autoescaped); zero projects → `<p>No projects.</p>` instead of the table. Stdout: exactly `specs site-index: {n} projects -> {out}`. A refused out dir is `error: {message}`, exit 1.

Tests (integration tier, `booping-python/e2e/cases/specs/`, hand-derived expected bytes): three projects given out of order in a YAML file, one with a multi-line description and one with none → full `index.html`, `style.css` presence and the marker asserted; zero projects (`[]`) → the `No projects.` page, exit 0; `--title` changes title, crumb and H1; a non-empty out dir without the marker is refused, exit 1.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | `index.py` (`Project`, `load_projects`, `build_index`) and the `site_index.html.j2` template on the shared environment. | `booping-python/src/booping/specs/site/index.py`, `booping-python/src/booping/specs/site/pages.py`, `booping-python/src/booping/specs/site/templates/site_index.html.j2` | 2 | pending |
| 1.2 | `site-index` verb: argparse wiring, YAML file read, write via `write_site`, stdout line. | `booping-python/src/booping/commands/specs.py` | 1 | pending |
| 1.3 | The four e2e cases above. | `booping-python/e2e/cases/specs/site-index-*.txtar` | 1 | pending |

## Definition of Done

### Task 1.1

- [ ] `build_index` output depends only on its arguments: no timestamp, no environment, rows sorted as C3 states.
- [ ] `style.css` in the result equals `booping-python/src/booping/specs/site/style.css` byte for byte.
- [ ] `booping specs site` output is unchanged — the existing `site-*.txtar` cases pass untouched.

### Task 1.2

- [ ] `booping specs site-index --help` lists `--projects`, `--out`, `--title` with their defaults.
- [ ] Success prints exactly `specs site-index: {n} projects -> {out}` on stdout and nothing on stderr.

### Task 1.3

- [ ] The four cases exist under `booping-python/e2e/cases/specs/`, named `site-index-{kebab-description}.txtar`, and pass.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/e2e/cases/specs/site-renders-one-root-with-links-and-marks.txtar` — case shape: fixtures, cmd, stdout, full expected file bytes.
- `booping-python/e2e/cases/specs/site-refuses-a-non-empty-out-without-marker.txtar` — the refusal case to mirror.
- `booping-python/src/booping/specs/site/templates/index.html.j2` — the table markup to match.

## Verify

`cd booping-python && uv run pytest e2e -k 'site' -q`
