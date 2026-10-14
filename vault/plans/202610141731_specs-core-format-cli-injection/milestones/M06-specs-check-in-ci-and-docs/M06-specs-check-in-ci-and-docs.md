---
id: "06"
title: "specs-check on the CLI, docs and CLAUDE.md"
sp: 4
status: pending
plan: "plans/202610141731_specs-core-format-cli-injection/index.md"
---

# M06: specs-check on the CLI, docs and CLAUDE.md

`just specs-check` runs `booping specs check`, and every surface that names the specs format or the CLI points at the shipped location and the new commands — no stale reference left in the sprint.

**Scope**: the `specs-check` recipe in `justfile` becomes a one-line call of `bin/booping specs check` from the repo root (the project tier of this repo is `vault/specs/`); it stays in the `ci` line in its current position. The Check section of `vault/specs/README.md` and of `src/specs/README.md` states what the check covers now. Public docs: a new `documentation/specs.md` page for users — the format in brief (link to the shipped guide on GitHub), the three tiers and where each lives, namespaced refs, and the three verbs with their flags and exit codes; `documentation/project_config.md` documents `core.specs`; `mkdocs.yml` nav lists the page after "Project config". Audience filter for the docs (rule/0008): only what a user configures or invokes — no Python module names, no check implementation details, no mention of the shatterlings port. `CLAUDE.md` updates per the plan's CLAUDE.md impact. Tests: none new — the recipe is exercised by `just ci`, docs by `just docs`.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | Replace the `specs-check` bash loop with `bin/booping specs check`; update both README Check sections. | `justfile`, `vault/specs/README.md`, `src/specs/README.md` | 1 | pending |
| 6.2 | Create `documentation/specs.md`; append the `core.specs` keys to `documentation/project_config.md` in its existing per-key style; add the nav entry. | `documentation/specs.md`, `documentation/project_config.md`, `mkdocs.yml` | 2 | pending |
| 6.3 | `CLAUDE.md`: Commands (`specs` in the `bin/booping` list, `just specs-check` described), Layout (`src/specs/`), Config (`core.specs` bullet), Vault paragraph (format → `src/specs/README.md`). | `CLAUDE.md` | 1 | pending |

## Definition of Done

### Task 6.1

- [ ] `just specs-check` runs `bin/booping specs check` and its exit code is the command's.
- [ ] Neither README says link targets or unique numbers are "not checked yet".

### Task 6.2

- [ ] `just docs` builds without warnings about the new page or nav.
- [ ] `documentation/specs.md` names no Python module, no internal check function and no other project.
- [ ] Every `core.specs` key from `src/config.yaml` appears in `documentation/project_config.md`.

### Task 6.3

- [ ] `rg -n 'vault/specs/README|vault/specs/schemas' CLAUDE.md justfile documentation` prints nothing.
- [ ] `CLAUDE.md` lists `specs` among the `bin/booping` subcommands.

Return: the list of changed files, nothing else.

## References

- `documentation/project_config.md` — per-key reference style for `core.specs`.
- `documentation/vault.md` — a user-facing page's voice and depth.
- `CLAUDE.md` Commands / Layout / Config sections — the bullets being extended.

## Verify

```
just docs
```

Builds without warnings. `just specs-check` over booping's own records is the runner's Final Verification — record findings are vault work, not this milestone's.
