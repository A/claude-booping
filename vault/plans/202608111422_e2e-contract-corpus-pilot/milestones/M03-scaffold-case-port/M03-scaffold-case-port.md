---
id: "03"
title: "Port scaffold behaviors to corpus cases"
sp: 7
status: done
plan: "plans/202608111422_e2e-contract-corpus-pilot/index.md"
---

# M03: Port scaffold behaviors to corpus cases

**Goal**: every CLI-observable behavior currently covered by `tests/commands/scaffold_test.py` and the CLI-reachable behaviors from `tests/context/scaffold_test.py` exist as txtar cases under `e2e/cases/scaffold/`.

**Scope**: new `.txtar` files only; both old test files stay in place until M04 (parallel green). Source of the behavior inventory: the two test files themselves — port behaviors, not test names. Expected sections are authored via `--update` and then **reviewed against the old test's hand-written expectation** — a baseline is accepted only when it matches what the superseded test asserted; a mismatch is a finding to report, never a baseline to keep.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Destination semantics + receipt shape: missing dest (parents created), empty dir, non-empty dir fill-in, existing-file skip line, `--force` overwrite, force never touching unrelated dirs, identical-bytes silent no-op, unified-diff receipt shape (`/dev/null` for new files, `created dir` lines, `scaffolded N paths — …` summary). ~10 cases. | `booping-python/e2e/cases/scaffold/*.txtar` | 2 | done |
| 3.2 | Seed rendering + filename keys + error paths: `--set` repeatable/later-wins, values as Jinja globals in bodies and filename keys, unsafe rendered names (`/`, `.`, `..`) exit 1, Jinja error atomicity (exit 1, zero writes), malformed `--set`/`--stub-macro` exit 1, unresolved config path / non-tree value exit 1, dest-is-file pre-flight exit 1. ~11 cases. | `booping-python/e2e/cases/scaffold/*.txtar` | 2 | done |
| 3.3 | Real config trees + chain + logging: `core.groom_playbook.scaffold`, `core.groom_playbook.milestone_scaffold`, `core.setup_playbook.scaffold` (Bases-fence content in `sprints.md`), `core.playbook_authoring_playbook.scaffold`; the scaffold→scaffold→query multi-cmd chain; the vault-attached `[scaffold]` log line (fixture ships a `.booping` marker in `cwd/`). ~6 cases. | `booping-python/e2e/cases/scaffold/*.txtar` | 2 | done |
| 3.4 | Re-engineer the CLI-reachable `context/scaffold_test.py` behaviors as observable cases. Method: for each behavior, design a fixture tree that makes it visible at the CLI boundary, then assert only what the CLI emits — internal assertions on `Node` graphs or exception types translate to receipt line order (stdout) and error text (stderr + exit 1); the expected stderr text is taken from what `bin/booping` actually prints for that input, cross-checked against the message the old test asserted. Cases: declaration-order preservation (a tree whose declared order differs from sorted order — receipt print order proves walk order), nested-path `ScaffoldError` messages (segment under scalar, invalid node shape). ~3 cases. | `booping-python/e2e/cases/scaffold/*.txtar` | 1 | done |

## Definition of Done

### Task 3.1

- [x] Each named behavior has at least one case; the skip line and the summary-line counters are asserted verbatim (normalized paths).
- [x] The identical-bytes case asserts absence of a diff hunk and an unchanged overwrite counter.

### Task 3.2

- [x] Every error case asserts exit code, stderr content, and — for atomicity — an empty `stdout` receipt (user-accepted equivalence: the format has no absent-file section; `_apply` prints a line per dir/file/skip, so an empty receipt is only producible by a run that wrote nothing).
- [x] Filename-key cases cover templated key, literal key, unsafe rendered name, missing `--set` variable.

### Task 3.3

- [x] Real-tree cases reference core config paths with no fixture config (three-tier merge provides them).
- [x] The chain case runs three commands in one sandbox and asserts the final `query` output.
- [x] The logging case asserts the `[scaffold]` line reaches the vault log file via `expected/`.

### Task 3.4

- [x] Order case's tree makes print order distinguishable from sorted order.
- [x] Error-message cases assert stderr text, not Python exception types.

### All tasks

- [x] `just e2e` green over the full corpus; old pytest files also still green (parallel).
- [x] A coverage cross-check table (old test → covering case(s), or "dropped: internal-only") is returned in the worker's final report — not written to any file — with every test in both files accounted for; the runner presents it to the user before M04 starts.

## Verify

```
just e2e scaffold
cd booping-python && uv run pytest tests/commands/scaffold_test.py tests/context/scaffold_test.py
```
