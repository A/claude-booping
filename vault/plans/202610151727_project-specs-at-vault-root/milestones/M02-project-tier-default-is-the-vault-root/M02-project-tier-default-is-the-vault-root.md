---
id: "02"
title: "Project tier default resolves to the vault root"
sp: 3
status: in-progress
plan: "plans/202610151727_project-specs-at-vault-root/index.md"
---

# M02: Project tier default resolves to the vault root

With `core.specs.tiers.project.path: null` the project tier root is the vault directory itself, whether the vault sits in the repo or outside it; an explicit `path` still resolves against the repo root.

**Scope**: `booping-python/src/booping/specs/tiers.py` `project_root()` and its docstring — `path` null with a vault → the vault; null with no vault attached → `{repo}/specs`, unchanged; explicit relative → `{repo}/{path}`; absolute or `~`-prefixed → as is. `src/config.yaml`, the comment above `project: {path: null}` becomes: `# Repo-relative; path null → the vault root itself (type directories beside plans/).` The unit tests whose fixtures seed project records at `vault/specs/{type}/` move them to `vault/{type}/`, their expected strings following: `booping-python/tests/specs/tiers_test.py`, `tests/specs/rules_test.py`, `tests/rendering_test.py`, `tests/templates/test_skill_rules.py`.

Until M03 the e2e corpus and until M07 this repo's own `just specs-check` are red — expected, both follow later in this plan.

Tests: unit tier, `tests/specs/tiers_test.py` — null path with an in-repo vault → the vault; null with a vault outside the repo → the vault; null with no vault → `{repo}/specs`; `specs` → `{repo}/specs`; an absolute path → itself. Expected paths hand-written.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Resolver default, docstring, config comment. | `booping-python/src/booping/specs/tiers.py`, `src/config.yaml` | 2 | pending |
| 2.2 | The five resolution cases in Tests; the other three test files follow the new default. | `booping-python/tests/specs/tiers_test.py`, `booping-python/tests/specs/rules_test.py`, `booping-python/tests/rendering_test.py`, `booping-python/tests/templates/test_skill_rules.py` | 1 | pending |

## Definition of Done

### Task 2.1

- [ ] `bin/booping config-get core.specs.tiers.project` still prints `path: null`; the comment above it is the text in Scope.
- [ ] `project_root()` returns the vault for a null path whenever a vault is given.

### Task 2.2

- [ ] One test per resolution case in Tests; no test asserts `vault/specs` as a default any more.

Return: the list of changed files, nothing else.

## References

- `booping-python/tests/specs/tiers_test.py` — the existing resolution tests to reshape.

## Verify

`cd booping-python && uv run pytest tests/specs/tiers_test.py tests/specs/rules_test.py tests/rendering_test.py tests/templates/test_skill_rules.py -q`
