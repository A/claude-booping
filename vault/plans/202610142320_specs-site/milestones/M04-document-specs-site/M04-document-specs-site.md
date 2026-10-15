---
id: "04"
title: "Document the specs site"
sp: 3
status: done
plan: "vault/plans/202610142320_specs-site/index.md"
---

# M04: Document the specs site

The public docs and the repo guide describe `booping specs site` and the `core.specs.site.roots` key, so the owner can build one site over every project from `home_dir`.

**Scope.** `documentation/specs.md`, `documentation/project_config.md`, `CLAUDE.md` (the `bin/booping … specs (…)` command list), `.gitignore` (the default out dir `specs-site/`). Audience: a booping user building and reading a site — what the command does, its flags, root selection, the out-directory guard, the warnings, the exit codes, and a `home_dir` example config. Not for them: module names, markdown-it-py, templates, how pages are assembled.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | `### booping specs site` under `## Commands`, a `site` column in `### Exit codes`, root selection with a global-config example for an aggregated site | `documentation/specs.md` | 2 | done |
| 4.2 | `core.specs.site.roots` bullet in `### core.specs` linking to the specs page; `site` in CLAUDE.md's `specs` verb list; `specs-site/` in `.gitignore` | `documentation/project_config.md`, `CLAUDE.md`, `.gitignore` | 1 | done |

## Definition of Done

### Task 4.1

- [x] The section states the flags, root selection order (C2), what each page holds (top index, root index with marks, type page with every record in full, record page with Referenced by), the out-directory marker rule, the summary and warning line shapes, and that output is deterministic and offline.
- [x] Exit-codes table gains a `site` column: 0 built (warnings may be printed), 1 bad root / no roots / out directory refused, 2 config could not be loaded.
- [x] Audience filter: nothing a user does not touch — no module, library or template names.
- [x] `just docs` builds (mkdocs `strict: true`).

### Task 4.2

- [x] `project_config.md` documents `core.specs.site.roots` (`{name, path}`, home_dir-relative, global tier) and links to the specs page section.
- [x] CLAUDE.md lists `site` among the `specs` verbs; no other CLAUDE.md line changes.

## References

- `documentation/specs.md` — `### booping specs check` and `### Exit codes`, the shape to follow.
- `documentation/project_config.md` — `### core.specs`.

## Verify

`just docs`

Return only: the list of changed files and the last line of the build output.
