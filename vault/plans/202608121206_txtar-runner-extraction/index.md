---
title: "Extract txtar contract runner into a standalone reusable module"
type: "refactoring"
status: in-progress
sp: 28
related_to: null
created: 2026-08-12 12:06
planned: null
started: 2026-08-12 12:29
completed: null
code_reviews: []
sessions:
- 34ff9ec3-9d14-4743-9821-7332f1d30d6d
- bed09e76-af36-42d7-bc2e-007148375af4
retro: null
summary: txtar e2e runner extracted to published pytest-txtar plugin; booping 
  e2e becomes its first consumer via conftest spec
commit: be3341cca08a2cd17f9b9ca7293539bc6dee3708
agents.research-codebase: a27ba047fc5513fbc
agents.research-web: a0c03e94f23b44a18
agents.cross-review: ac9039959537468ef
reviewed_at: 2026-08-12 12:28
agents.develop-loop-M01: a3928f420b347d470
---

# Extract txtar contract runner into a standalone reusable module

## Context

- **Current state** — the contract-corpus runner lives inside booping's e2e directory: `booping-python/e2e/run.py` (361 lines) plus a vendored txtar parser `_txtar.py` and the case-format spec `e2e/README.md`. The machinery (txtar cases, sandboxed runs, normalized assertions, `--update` rebaselining) is generic, but the binary under test, the `booping` command-word substitution, the sandbox roots and the normalization tokens are hard-coded module constants — reuse in another project means copy-and-edit.
- **Motivation** — the pattern is wanted in other projects, and web research found no Python package combining txtar parsing, sandboxed CLI execution and a golden-update flow (the Go `testscript` pattern); publishing fills a real gap.
- **Scope** — extract the runner into a published `pytest-txtar` package (pytest plugin over a pytest-free core), rewire booping's e2e suite as its first consumer, split the package into its own GitHub repo and publish v0.1.0 to PyPI. NOT in scope: changing any of the 38 cases, changing the case-format semantics, extending corpus coverage to more booping commands.

## Decisions

- **Pytest is the runner**: `*.txtar` files collect as native pytest items; the custom select/report/main loop is deleted, not ported — selection (`-k`), parallelism, reporting and exit codes come from pytest. Alternative (standalone CLI runner kept alongside) rejected: duplicate runner surface to maintain for no consumer.
- **Layered package**: `pytest_txtar.txtar` (format parser) and a pytest-free core (`case`/`sandbox`/`compare`/`update`) below a thin `plugin.py` — non-pytest consumers can import the core; the split was an explicit user ask.
- **Naming**: distribution `pytest-txtar`, module `pytest_txtar`. PyPI `txtar` is taken by a parser-only package (verified 2026-08-12); `pytest-txtar` is free and states the shape.
- **Configuration via hook**: consumers implement `pytest_txtar_spec(config) -> TxtarSpec` in `conftest.py` (commands mapping, roots, cwd root, env, tokens). Alternative (ini options / config file) rejected: normalizers and paths are Python values; a hook keeps one configuration surface.
- **Build in-repo, split last**: the package grows at `{repo}/pytest-txtar/` with booping wired via a `[tool.uv.sources]` path dependency, and moves to its own repo only in M04 — develop's workers stay in one repo; the split is mechanical. Alternative (new repo from day one) rejected: every iteration would cross repos.
- **Publish channel**: PyPI trusted publishing (OIDC) from GitHub Actions — no stored token; booping ends on `pytest-txtar>=0.1.0`. Git-tag dependency rejected as the end state: publishing was the request.
- **Licensing**: MIT for the package, with a BSD-3-Clause attribution block for the `golang.org/x/tools/txtar` port (upstream license verified).

## Architecture

```
pytest-txtar/  (M01–M03 in-repo, M04 its own repo)
  src/pytest_txtar/
    txtar.py      # format parser (port of golang.org/x/tools/txtar, BSD-3 attribution)
    case.py       # Case model, load_case, tree validation      ┐
    sandbox.py    # sandbox build, env, run_case(case, spec)    │ pytest-free core,
    compare.py    # normalizer, [..] wildcard, Mismatch, diff   │ parameterized by TxtarSpec
    update.py     # updated_archive                             ┘
    hooks.py      # pytest_txtar_spec hookspec
    plugin.py     # pytest_collect_file → TxtarFile/TxtarItem, --txtar-update
booping-python/e2e/
  conftest.py     # implements pytest_txtar_spec with booping's constants
  cases/**/*.txtar  # unchanged, 38 cases
```

Booping integration points: `justfile` `e2e` recipe (`uv run pytest e2e`, patterns → `-k`), `.github/workflows/ci.yml` untouched (calls `just e2e`), `booping-python/pyproject.toml` dev dependency (path source until M04, then PyPI).

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [Package core — txtar parser and pytest-free runner core](milestones/M01-package-core/M01-package-core.md) | 8 | done |
| 02 | [Pytest plugin layer](milestones/M02-pytest-plugin/M02-pytest-plugin.md) | 8 | pending |
| 03 | [Booping e2e rewire onto pytest-txtar](milestones/M03-booping-rewire/M03-booping-rewire.md) | 5 | pending |
| 04 | [Repo split and PyPI publish](milestones/M04-repo-split-publish/M04-repo-split-publish.md) | 7 | pending |

## Implementation Order

Strictly linear: M01 → M02 → M03 → M04. No parallel milestones.

## Key Files Reference

| File | Role |
|------|------|
| `booping-python/e2e/run.py` | source of the core extraction (M01), deleted in M03 |
| `booping-python/e2e/_txtar.py` | source of `pytest_txtar/txtar.py` (M01), deleted in M03 |
| `booping-python/e2e/README.md` | generic spec content moves to the package README (M03) |
| `pytest-txtar/src/pytest_txtar/` | the extracted package, M01–M02 |
| `justfile` | `e2e` recipe rewired in M03 |

## Final Verification

- [ ] `just ci` green (lint, typecheck, pytest, snapshots, mdcheck, e2e) with e2e running through pytest-txtar.
- [ ] All 38 corpus cases pass unmodified; `uv run pytest e2e --txtar-update` rewrites nothing on the green corpus.
- [ ] `pytest-txtar` 0.1.0 live on PyPI; booping resolves it from PyPI with no `[tool.uv.sources]` entry and no in-repo package copy.
- [ ] External repo CI green; publish workflow uses trusted publishing with no stored secret.

## Testing Strategy

N/A — deterministic. Package core and plugin carry their own pytest suites (unit + pytester); the 38-case corpus is the acceptance harness for the booping rewire.

## Deployment / config impact

N/A — no env vars, no infra. Booping's CI workflow is unchanged (`just e2e` interface preserved); the new repo carries its own CI + trusted-publishing workflow (M04).

## Authorization / data access

N/A — no endpoints, no tenant data.

## Out of scope

- Extending the corpus beyond the existing 38 scaffold cases or converting more booping commands.
- Any change to case-format semantics (sections, wildcard rules, normalization tokens' meaning).
- A standalone non-pytest CLI runner for the package.
- Windows support beyond what the current runner already has (POSIX-oriented sandbox env).
- Publishing docs site / readthedocs for the package — README is the documentation at v0.1.0.

## CLAUDE.md impact

| Section | Change | Owning task |
|---------|--------|-------------|
| `## Commands` | `just e2e` bullet: pytest-based runner, rebaseline via `uv run pytest e2e --txtar-update` | M03.3 |
| `## Layout` | `booping-python/` bullet: corpus + conftest consume the external `pytest-txtar` package; spec lives in the package | M03.3 |
