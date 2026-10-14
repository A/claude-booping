---
id: "03"
title: "booping specs site command, roots config and e2e cases"
sp: 8
status: pending
plan: "vault/plans/202610142320_specs-site/index.md"
---

# M03: booping specs site command, roots config and e2e cases

`booping specs site [--out DIR] [--root NAME=PATH ...]` selects its roots, builds the site with M01–M02 and reports one summary line, its warnings and the exit codes `index.md` → I/O contract locks.

**Scope.** `booping-python/src/booping/commands/specs.py` (new `site` verb beside `ls`/`next`/`check`/`init`, same `set_defaults(func=…)` idiom, same `_assemble`/`_resolve`/`_known_types`/`_fail` helpers); `src/config.yaml` (`core.specs.site.roots: []` with a comment); txtar cases under `booping-python/e2e/cases/specs/`. Root selection (C2):

1. `--root NAME=PATH` given (repeatable) → exactly those, in flag order. `PATH` relative to the working directory, `~` expanded. A missing `=`, a `NAME` outside `[A-Za-z0-9][A-Za-z0-9._-]*`, a `PATH` that is not a directory → exit 1.
2. Otherwise: `_resolve(...)` tiers whose `root` is a directory, in order core, global, project — named by `tier.namespace`, the project tier (no namespace) by `ctx.project.name`; then each `core.specs.site.roots` entry `{name, path}` in listed order, `path` resolved like the global tier's (`~` expanded, absolute as is, else relative to `home_dir` — reuse `_resolve_path` from `booping/specs/tiers.py`). Any root — tier or configured — resolving (symlinks followed) to an already-selected path is skipped silently; one whose directory is missing gives a warning line and is skipped; a configured entry with a bad name or no `path` → exit 1.
3. Two selected roots with the same name → exit 1. No root at all → exit 1.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | `site` verb: flags, root selection, build + write, stdout/stderr, exit codes, `--help` | `booping-python/src/booping/commands/specs.py` | 3 | pending |
| 3.2 | `core.specs.site.roots: []` in core config with its comment | `src/config.yaml` | 1 | pending |
| 3.3 | txtar cases on a small fixture | `booping-python/e2e/cases/specs/site-*.txtar` | 4 | pending |

## Definition of Done

### Task 3.1

- [ ] stdout on success is exactly one line: `specs site: {R} roots, {N} records, {P} pages, {W} warnings -> {out}` — `{out}` as given on the command line (default `specs-site`), `{P}` the number of `.html` files written.
- [ ] stderr carries one line per warning, sorted by path then line: `{path}:{line}  warning  site  {message}` with `{path}` from `display_path` in `booping/specs/check.py`; a skipped configured root is `{path}  warning  site  root {name} not found, skipped` (no line). Nothing else on stderr on success.
- [ ] Errors print `error: {message}` via `_fail` and exit 1 (bad `--root`, bad configured entry, duplicate name, no roots, any `SiteError` from `write_site`) or 2 (config could not be loaded).
- [ ] `booping specs site --help` lists `--out` (default shown) and `--root NAME=PATH` (repeatable).
- [ ] A `logger.log(...)` line like the sibling verbs.

### Task 3.2

- [ ] `core.specs.site.roots` defaults to `[]`; the comment says each entry is `{name, path}`, `path` home_dir-relative, read by `booping specs site`, set in the global tier. No other key added.

### Task 3.3

- [ ] Cases (CLI surface, integration tier), each with exact `stdout`, `stderr`, `exit`:
  - `site-renders-one-root-with-links-and-marks` — `--root proj=specs` over a fixture of a value, a rule and an ADR (frontmatter `values:` ref, body link with anchor, one `[clarify]`, one link to a missing file); `expected/cwd/specs-site/proj/adr/0001-….html` and `expected/cwd/specs-site/proj/index.html` asserted in full, plus `expected/cwd/specs-site/.booping-site`.
  - `site-resolves-a-namespaced-ref-across-roots` — two `--root` flags, a `rule` in root `b` with `values: [a:value/0001]`; the rule page asserted in full.
  - `site-adds-configured-roots-to-the-tiers` — xdg config pins `core.specs.tiers.core.path` to a fixture dir under `~` and sets `core.specs.site.roots` with one existing and one missing entry; no `--root`; asserts the summary line, the skip warning and `expected/cwd/specs-site/index.html` in full.
  - `site-refuses-a-non-empty-out-without-marker` — exit 1, `stderr` the error line, the pre-existing file untouched.
  - `site-rejects-a-malformed-root-flag` — `--root nameonly`, exit 1.
- [ ] stdout, stderr, exit and `.booping-site` are hand-written; the full-page `expected/` sections are written once by `--txtar-update` and then read against `index.md` → I/O contract before they are kept (C9).

## References

- `booping-python/e2e/cases/specs/ls-tier-global-reads-the-home-dir-specs.txtar` — xdg config fixture + global tier.
- `booping-python/e2e/cases/specs/init-project-tier-outside-vault-creates-repo-specs-and-links-it.txtar` — `expected/cwd/…` assertions on written files.
- `booping-python/e2e/README.md` — corpus conventions (unasserted vs empty sections).

## Verify

`just e2e -k site-`

Return only: the list of changed files and the pytest summary line.
