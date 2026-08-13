---
id: "01"
title: "Core CLI corpus cases — set, coercion, errors, diff, stderr, log"
sp: 3
status: done
plan: "vault/plans/202608121417_frontmatter-update-e2e-migration/index.md"
---

# M01: Core CLI corpus cases — set, coercion, errors, diff, stderr, log

Goal: `booping frontmatter-update`'s scalar-set behaviors, error paths, diff/stderr output contract, and log side effect are each asserted by a named txtar case under `booping-python/e2e/cases/frontmatter-update/`, green via `pytest e2e`.

Scope: new `.txtar` files only, under `booping-python/e2e/cases/frontmatter-update/`. No changes to `e2e/conftest.py`, the `pytest-txtar` plugin, or `src/booping/commands/frontmatter_update.py`. Follow the existing scaffold corpus conventions (`e2e/cases/scaffold/*.txtar`): kebab-case behavior filename, description line at top, sections `fixtures/{home|xdg|cwd}/**`, `cmd`, `exit`, `stdout`, `stderr`, `expected/{home|xdg|cwd}/**`, `[..]` wildcards for volatile spans. Author expected sections by hand or via `uv run pytest e2e --txtar-update -k frontmatter` after eyeballing actual output.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Scalar-set cases: sets a key with a literal value; preserves other keys and body; sets multiple keys in one call; second identical call prints no diff and exits 0 | `booping-python/e2e/cases/frontmatter-update/*.txtar` | 1 | done |
| 1.2 | Coercion cases, parametrized as one case per family: int, float, bool, null, ambiguous string gets quoted, YAML-1.1 `yes` quirk stays string, newline/tab-bearing value (gap case) — each asserting the typed value in the expected file bytes | `booping-python/e2e/cases/frontmatter-update/*.txtar` | 1 | done |
| 1.3 | Error and output-contract cases: missing plan file (exit 1, stderr message), malformed pair (exit 1), nothing to do (exit 1); unified-diff shape on stdout (`---`/`+++`/`@@`); success summary line on stderr not stdout; `.booping.log` gains one `[..]`-wildcarded line when a vault is attached (mirror `scaffold/logs-one-line-when-a-vault-is-attached.txtar`) | `booping-python/e2e/cases/frontmatter-update/*.txtar` | 1 | done |

## Definition of Done

### Task 1.1

- [x] Each behavior is its own kebab-named `.txtar` case with a one-line description.
- [x] Expected file bytes assert the full resulting frontmatter, not just the changed key.
- [x] `uv run pytest e2e -k frontmatter` passes without `--txtar-update`.

### Task 1.2

- [x] Every coercion family from the unit suite's scalar-typing tests has a corpus case with the hand-derived expected literal.
- [x] Newline/tab gap case asserts the value round-trips through the file unmangled or errors cleanly — whichever the CLI actually does, captured as the contract.

### Task 1.3

- [x] Each error path asserts exit code and stderr message together.
- [x] Diff-shape case asserts `--- `/`+++ `/`@@` header lines on stdout.
- [x] Log case wildcards the timestamp with `[..]` and asserts exactly one appended line.

## Verify

```
cd booping-python && uv run pytest e2e -k frontmatter -v
```

All new cases listed and passing; zero cases rewritten when run again with `--txtar-update` (clean baseline).
