---
id: "03"
title: "GitLab discovery script — the group's booping-specs projects as site-index
  input"
sp: 3
status: done
plan: "plans/202610152242_specs-sites-gitlab-pages/index.md"
---

# M03: GitLab discovery script — the group's booping-specs projects as site-index input

`src/ci/gitlab/list-specs-projects.py` prints, as `site-index` stdin JSON, every project of the CI job's group that carries the specs topic, reading the GitLab API with a token it never prints.

**Scope**: new stdlib-only script (Python ≥ 3.12, no third-party import, executable, `#!/usr/bin/env python3`) per `../../clarifications.md` C4. Environment: `CI_API_V4_URL` (required), `CI_PROJECT_NAMESPACE` (required; the group path, URL-encoded with `urllib.parse.quote(..., safe="")`), `SPECS_INDEX_TOKEN` (required), `SPECS_TOPIC` (default `booping-specs`), `SPECS_PAGES_BASE` (default `CI_PAGES_URL`; one of the two required; trailing `/` stripped). Request `GET {api}/groups/{group}/projects?topic={topic}&archived=false&per_page=100&order_by=path&sort=asc&page={n}` with header `PRIVATE-TOKEN`, following the `x-next-page` response header; the last page is reached when that header is absent or an empty string (GitLab sends it empty). Output on stdout: a JSON array of `{"name": project.name, "url": "{base}/{project.path}", "description": project.description}` sorted by `(name.casefold(), name)` — the order `site-index` renders — `json.dumps(..., indent=2, ensure_ascii=False)` plus a newline. Failures — a required variable missing, a non-2xx response, a network error, a body that is not a JSON list — print one `list-specs-projects: {reason}` line to stderr and exit 1; a reason names the variable or the HTTP status and request URL, never the token. Nothing else is printed.

Tests (integration tier, `booping-python/tests/ci/list_specs_projects_test.py`): run the script as a subprocess against a fake GitLab served by `http.server.ThreadingHTTPServer` on `127.0.0.1:0` in a thread, pointing `CI_API_V4_URL` at it. Cases: two pages of projects (`x-next-page: 2` then empty) → merged, sorted output with Pages URLs from `SPECS_PAGES_BASE`, and the fake records the `PRIVATE-TOKEN` header, `topic`, `archived=false` and the URL-encoded group `lab%2Fsub`; `SPECS_PAGES_BASE` unset → `CI_PAGES_URL` used; a 401 → exit 1, stderr names `401`, and neither stream contains the token value; `SPECS_INDEX_TOKEN` unset → exit 1 naming the variable, no request made. Expected outputs hand-written in the test.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | The discovery script. | `src/ci/gitlab/list-specs-projects.py` | 2 | done |
| 3.2 | Subprocess tests against the fake server. | `booping-python/tests/ci/list_specs_projects_test.py`, `booping-python/tests/ci/__init__.py` | 1 | done |

## Definition of Done

### Task 3.1

- [x] The script imports only the standard library and is executable.
- [x] The token appears only in the request header — in no message, no exception text and no URL.

### Task 3.2

- [x] The four cases pass; the token-leak case asserts the token string is absent from stdout and stderr.
- [x] `just lint` and `just typecheck` cover the test file without new ignores.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/tests/specs/site_test.py` — test module style in this repo.
- GitLab API "List a group's projects": https://docs.gitlab.com/api/groups/ — parameters `topic`, `archived`, `per_page`, `order_by`; pagination header `x-next-page`.

## Verify

`cd booping-python && uv run pytest tests/ci -q`
