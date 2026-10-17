---
id: "02"
title: "site-index — stdin JSON and input validation"
sp: 3
status: done
plan: "plans/202610152242_specs-sites-gitlab-pages/index.md"
---

# M02: site-index — stdin JSON and input validation

`booping specs site-index` reads its project list as JSON from stdin by default (`--projects -`) and rejects malformed input with one named error.

**Scope**: `booping-python/src/booping/commands/specs.py` — `--projects` default becomes `-`; `-` parses stdin with `json.loads`, any other value parses the file with `yaml.safe_load`. `booping-python/src/booping/specs/site/index.py` `load_projects` validates per `../../clarifications.md` C3 and raises one error naming the entry as `projects[{i}]` (0-based, input order): top level not a list; entry not a mapping; a key other than `name`, `url`, `description` (message `projects[{i}]: unknown key `{key}``, the first unknown key in sorted order); `name` missing, not a string or empty after strip; `url` missing, not a string, or not starting `http://` or `https://`; `description` neither a string nor null; a duplicate `name` (message names both indexes). Unreadable input — missing file, YAML or JSON syntax error — is `error: --projects {PATH or -}: {reason}`, `{reason}` being `no such file` for a missing file and the parser exception's first line otherwise. Every one surfaces as a single `error: {message}` stderr line, exit 1, nothing written to the out dir.

Tests (integration tier, `booping-python/e2e/cases/specs/`, hand-derived): stdin JSON via `sh -c 'booping specs site-index --out site < projects.json'` renders the same `index.html` bytes as a YAML file with the same entries; one case each for a `javascript:` URL, an unknown key, a duplicate name and a non-list top level → exact stderr line, exit 1, no out dir created; invalid JSON on stdin → exit 1.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Stdin JSON as the default source; file stays YAML. | `booping-python/src/booping/commands/specs.py` | 1 | done |
| 2.2 | Validation in `load_projects` with indexed messages. | `booping-python/src/booping/specs/site/index.py` | 1 | done |
| 2.3 | The six e2e cases above. | `booping-python/e2e/cases/specs/site-index-*.txtar` | 1 | done |

## Definition of Done

### Task 2.1

- [x] `--projects` defaults to `-`; `--help` says stdin is JSON and a file is YAML.

### Task 2.2

- [x] Every rejection listed in Scope gives exactly one `error: projects[{i}]: …` (or input-level `error: …`) line on stderr, exit 1, and leaves no out dir behind.

### Task 2.3

- [x] The six cases exist and pass; the M01 cases still pass.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/e2e/cases/specs/site-rejects-a-malformed-root-flag.txtar` — failure-case shape (exit, stderr, no expected files).
- The M01 cases `booping-python/e2e/cases/specs/site-index-*.txtar` — fixture and expected-bytes shape to reuse.

## Verify

`cd booping-python && uv run pytest e2e -k 'site-index' -q`
