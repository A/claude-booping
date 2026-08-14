---
id: "02"
title: "List-op and macro corpus cases \u2014 remove, append, stubbed and real macros, gap cases"
sp: 3
status: pending
plan: "vault/plans/202608121417_frontmatter-update-e2e-migration/index.md"
---

# M02: List-op and macro corpus cases — remove, append, stubbed and real macros, gap cases

Goal: `--remove`/`--append` list operations and Jinja macro interpolation are asserted by named txtar cases under `booping-python/e2e/cases/frontmatter-update/`, including one case proving real macro shell execution across the subprocess boundary.

Scope: new `.txtar` files under `booping-python/e2e/cases/frontmatter-update/`, plus one fixture config per case at `fixtures/xdg/booping/config.yaml` — the single place both macro forms are seeded: a top-level `macro_stubs:` mapping for the stubbed cases, `core.macros.*` for the real-execution case. `frontmatter-update` has no `--stub-macro` flag, so the flag is not an option here. No changes to `e2e/conftest.py`, `pytest-txtar`, or command source. Conventions and authoring procedure as in M01 (see `e2e/cases/scaffold/*.txtar`).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | List-op cases: `--append` creates a list on a null key and on an absent key; extends an existing list; identical append twice is idempotent (second run no diff); `--append` onto a scalar exits 1 with stderr message; `--remove` drops a key; combined pairs + removals + appends in one call; append-only call with nothing to change exits 1 | `booping-python/e2e/cases/frontmatter-update/*.txtar` | 1 | pending |
| 2.2 | Stubbed-macro interpolation cases: value `{{ macro('...') }}` resolved from a stubbed macro (fixture `macro_stubs:` / `--stub-macro`) lands typed in the file; unknown macro name exits 2 with stderr; malformed Jinja exits 2; macro-rendered date-like value stays a string | `booping-python/e2e/cases/frontmatter-update/*.txtar` | 1 | pending |
| 2.3 | Real macro execution case (gap case): fixture config defines a macro as a real shell command (`echo 1`); `booping frontmatter-update plan.md key="{{ macro('...') }}"` writes the command's actual output into the frontmatter — proving live macro execution through the CLI subprocess boundary, replacing the abandoned live-git unit test | `booping-python/e2e/cases/frontmatter-update/*.txtar` | 1 | pending |

## Definition of Done

### Task 2.1

- [ ] Every `--remove`/`--append` behavior from the unit suite has a corpus case asserting diff, resulting file bytes, stderr summary, and exit code.
- [ ] Idempotency case runs the command twice via sequential `cmd` lines and asserts the second produces no diff.

### Task 2.2

- [ ] Every stubbed case seeds its stub as a top-level `macro_stubs:` mapping in `fixtures/xdg/booping/config.yaml`.
- [ ] Exit-2 macro failure cases assert stderr content, not just the code.

### Task 2.3

- [ ] The macro in fixture config is a genuine argv command (`echo`), not a stub — the asserted frontmatter value (`1`) can only come from executing it.
- [ ] Case is deterministic: no clock, git, or network in the macro.

## References

- `booping-python/e2e/README.md` — the case-format spec. It is in the repo; do not go looking for the `pytest-txtar` plugin's own documentation.
- `booping-python/e2e/cases/scaffold/malformed-stub-macro-pair-is-rejected.txtar` — how a case seeds `fixtures/xdg/booping/config.yaml`.
- `booping-python/src/booping/macros.py` — `macro_stubs` resolution and real macro execution. Read it for behavior questions instead of probing the CLI.
- The M01 cases already in `booping-python/e2e/cases/frontmatter-update/` — the shape this milestone extends.

## Verify

```
cd booping-python && uv run pytest e2e -k frontmatter -q
```

All M01 and M02 cases pass with no case rewritten.
