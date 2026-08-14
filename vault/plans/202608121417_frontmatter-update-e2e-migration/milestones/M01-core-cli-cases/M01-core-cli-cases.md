---
id: "01"
title: "Core CLI corpus cases — set, coercion, errors, diff, stderr, log"
sp: 3
status: in-progress
plan: "vault/plans/202608121417_frontmatter-update-e2e-migration/index.md"
---

# M01: Core CLI corpus cases — set, coercion, errors, diff, stderr, log

Goal: `booping frontmatter-update`'s scalar-set behaviors, error paths, diff/stderr output contract, and log side effect are each asserted by a named txtar case under `booping-python/e2e/cases/frontmatter-update/`, green via `pytest e2e`.

Scope: new `.txtar` files only, under `booping-python/e2e/cases/frontmatter-update/`. No changes to `e2e/conftest.py`, the `pytest-txtar` plugin, or `src/booping/commands/frontmatter_update.py`. Follow the existing scaffold corpus conventions (`e2e/cases/scaffold/*.txtar`): kebab-case behavior filename, description line at top, sections `fixtures/{home|xdg|cwd}/**`, `cmd`, `exit`, `stdout`, `stderr`, `expected/{home|xdg|cwd}/**`, `[..]` wildcards for volatile spans.

Authoring procedure, the only one: hand-write each case's description, `fixtures/**` and `cmd` sections, leave `exit`, `stdout`, `stderr` and `expected/**` empty, then fill them with `cd booping-python && uv run pytest e2e --txtar-update -k frontmatter` and read the rewritten file to confirm the recorded contract is the intended one. Never hand-derive an expected block, and never probe the CLI in a scratch directory to predict one.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Scalar-set cases: sets a key with a literal value; preserves other keys and body; sets multiple keys in one call; second identical call prints no diff and exits 0 | `booping-python/e2e/cases/frontmatter-update/*.txtar` | 1 | pending |
| 1.2 | Coercion cases, parametrized as one case per family: int, float, bool, null, ambiguous string gets quoted, YAML-1.1 `yes` quirk stays string, newline/tab-bearing value (gap case) — each asserting the typed value in the expected file bytes | `booping-python/e2e/cases/frontmatter-update/*.txtar` | 1 | pending |
| 1.3 | Error and output-contract cases: missing plan file (exit 1, stderr message), malformed pair (exit 1), nothing to do (exit 1); unified-diff shape on stdout (`---`/`+++`/`@@`); success summary line on stderr not stdout; `.booping.log` gains one `[..]`-wildcarded line when a vault is attached (mirror `scaffold/logs-one-line-when-a-vault-is-attached.txtar`) | `booping-python/e2e/cases/frontmatter-update/*.txtar` | 1 | pending |

## Definition of Done

### Task 1.1

- [ ] Each behavior is its own kebab-named `.txtar` case with a one-line description.
- [ ] Expected file bytes assert the full resulting frontmatter, not just the changed key.
- [ ] `uv run pytest e2e -k frontmatter` passes without `--txtar-update`.

### Task 1.2

- [ ] Every coercion family from the unit suite's scalar-typing tests has a corpus case with the recorded expected literal.
- [ ] Newline/tab gap case asserts the value round-trips through the file unmangled or errors cleanly — whichever the CLI actually does, captured as the contract.

### Task 1.3

- [ ] Each error path asserts exit code and stderr message together.
- [ ] Diff-shape case asserts `--- `/`+++ `/`@@` header lines on stdout.
- [ ] Log case wildcards the timestamp with `[..]` and asserts exactly one appended line.

## References

- `booping-python/e2e/README.md` — the case-format spec. It is in the repo; do not go looking for the `pytest-txtar` plugin's own documentation.
- `booping-python/e2e/cases/scaffold/smoke.txtar` — minimal case shape to copy.
- `booping-python/e2e/cases/scaffold/logs-one-line-when-a-vault-is-attached.txtar` — vault-attached `.booping.log` assertion with a `[..]` wildcard.
- `booping-python/src/booping/commands/frontmatter_update.py` — the implementation. Read it for behavior questions instead of probing the CLI.

## Verify

```
cd booping-python && uv run pytest e2e -k frontmatter -q
```

All new cases pass with no case rewritten.
