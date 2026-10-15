---
id: "05"
title: "Docs — site-index, publishing on GitLab Pages, CLAUDE.md"
sp: 2
status: in-progress
plan: "plans/202610152242_specs-sites-gitlab-pages/index.md"
---

# M05: Docs — site-index, publishing on GitLab Pages, CLAUDE.md

`documentation/specs.md` documents `booping specs site-index` and how to publish specs sites on GitLab Pages under one index; CLAUDE.md lists the new verb and the shipped `src/ci/` directory.

**Scope**: audience — booping users setting up publishing; only what they run and configure, no internal churn (booping:rule/0008).

- `documentation/specs.md`: a `### booping specs site-index` section after `### booping specs site` — flags, input shape (stdin JSON, file YAML, keys, validation), output content and determinism as `../../clarifications.md` C3 locks it, one example: a two-project JSON array piped on stdin (`booping specs site-index --out public < projects.json`) and the stdout line it prints; a `site-index` column in the `### Exit codes` table (0 index written; 1 unreadable or invalid project list, or the out directory refused; 2 config could not be loaded). A new `## Publishing on GitLab Pages` section after `## Commands`' subsections: the model of adr/0029 in two sentences (a site per project, an index at the group's Pages root listing projects by topic); per-project setup — a repo-local vault, `include: remote:` of `https://raw.githubusercontent.com/A/claude-booping/master/src/ci/gitlab/specs-site.gitlab-ci.yml`, pin `BOOPING_REF` to a release tag; index setup — a project named `{group}.{pages-domain}` (served at the group's Pages root), `include: remote:` of `specs-index.gitlab-ci.yml`, a read-only token (`read_api`) as a masked CI variable `SPECS_INDEX_TOKEN`, a pipeline schedule, optional `SPECS_TOPIC` / `SPECS_PAGES_BASE`; adding a project = setting the topic; how the jobs get booping (shallow clone, uv image) and that neither needs mdcheck, naming `cargo install markdown-checker --version 0.1.1 --locked` for a project that adds its own `specs check` job; the limits — subgroup projects are not listed, archived projects are skipped.
- `CLAUDE.md`: the `bin/booping` subcommand list gains `site-index` under `specs`; the Layout list gains `src/ci/` — shipped CI templates and their helper script, consumed by URL, not by the CLI.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | `site-index` command section, exit-code column, and the publishing section. | `documentation/specs.md` | 1 | pending |
| 5.2 | CLAUDE.md commands and layout lines. | `CLAUDE.md` | 1 | pending |

## Definition of Done

### Task 5.1

- [ ] Every flag, default, variable and path named in the docs matches the shipped code and templates.
- [ ] No host or group name from the owner's homelab appears — examples use `{group}` and `{pages-domain}`.

### Task 5.2

- [ ] The two CLAUDE.md lines exist; nothing else in CLAUDE.md changes.

Return: the list of changed and created files, nothing else.

## References

- `documentation/specs.md` `### booping specs site` — the section shape to copy.
- `src/ci/gitlab/specs-site.gitlab-ci.yml`, `src/ci/gitlab/specs-index.gitlab-ci.yml` (M04) — the variables to document.

## Verify

`just docs`
