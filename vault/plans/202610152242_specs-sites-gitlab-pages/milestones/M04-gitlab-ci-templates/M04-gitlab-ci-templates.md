---
id: "04"
title: "GitLab CI templates — the project pages job and the index job"
sp: 2
status: in-progress
plan: "plans/202610152242_specs-sites-gitlab-pages/index.md"
---

# M04: GitLab CI templates — the project pages job and the index job

booping ships two GitLab CI templates a project includes by URL: one publishes the project's specs site with `pages`, the other rebuilds the group index on a schedule.

**Scope**: two new files under `src/ci/gitlab/`, per `../../clarifications.md` C1, C2 and C4; no project or host name anywhere in them.

- `specs-site.gitlab-ci.yml` — job `pages`: `image: ghcr.io/astral-sh/uv:python3.12-trixie`; `variables:` `BOOPING_REPO: https://github.com/A/claude-booping.git`, `BOOPING_REF: master`, `UV_CACHE_DIR: $CI_PROJECT_DIR/.uv-cache`; `cache:` key `booping-uv`, path `.uv-cache`; `script:` `git clone --depth 1 --branch "$BOOPING_REF" "$BOOPING_REPO" /tmp/booping` then `/tmp/booping/bin/booping specs site --out public`; `artifacts: paths: [public]`; `rules: - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH`.
- `specs-index.gitlab-ci.yml` — job `pages`, same image, variables (plus `SPECS_TOPIC: booping-specs`) and cache; `script:` the same clone, then `/tmp/booping/src/ci/gitlab/list-specs-projects.py > projects.json` and `/tmp/booping/bin/booping specs site-index --projects - --out public < projects.json`; `artifacts: paths: [public]`; `rules:` `if: $CI_PIPELINE_SOURCE == "schedule"` and `if: $CI_PIPELINE_SOURCE == "web"`. The token variable `SPECS_INDEX_TOKEN` is not declared in the file — it is a masked project CI variable, and no line echoes it.
- Each file opens with a comment block of at most 6 lines: what it does, the `include: remote:` line that consumes it, the variables to set.

Tests (integration tier, `booping-python/tests/ci/templates_test.py`): each template parses with `yaml.safe_load`; has exactly one job `pages` with `artifacts.paths == ["public"]`; every `/tmp/booping/...` path a script line runs exists in this repo relative to the repo root (so a rename breaks the test); the index template never names `SPECS_INDEX_TOKEN` outside its header comment.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | The two templates. | `src/ci/gitlab/specs-site.gitlab-ci.yml`, `src/ci/gitlab/specs-index.gitlab-ci.yml` | 1 | pending |
| 4.2 | Template tests. | `booping-python/tests/ci/templates_test.py` | 1 | pending |

## Definition of Done

### Task 4.1

- [ ] Both files match the Scope job by job; neither names `lab`, `zorya` or any other host besides `github.com/A/claude-booping` and the uv image.

### Task 4.2

- [ ] The four checks pass for both templates.

Return: the list of changed and created files, nothing else.

## References

- GitLab CI `pages` job and `include:remote`: https://docs.gitlab.com/ci/yaml/
- `src/ci/gitlab/list-specs-projects.py` (M03) — the script the index template runs.

## Verify

`cd booping-python && uv run pytest tests/ci -q`
