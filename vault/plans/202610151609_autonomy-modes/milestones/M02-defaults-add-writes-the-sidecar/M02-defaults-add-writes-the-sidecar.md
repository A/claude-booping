---
id: "02"
title: "booping defaults add writes the defaults sidecar"
sp: 4
status: done
plan: "plans/202610151609_autonomy-modes/index.md"
---

# M02: booping defaults add writes the defaults sidecar

`booping defaults add` appends the next `D{n}` entry to `defaults.md` beside the run artefact, seeding the file when missing, and prints `{sidecar}#D{n}`.

**Scope**: new top-level command `defaults` with one verb `add` — argparse shell `booping-python/src/booping/commands/defaults.py` registered in `booping-python/src/booping/cli.py`, logic in `booping-python/src/booping/defaults.py`. Flags and output per `index.md` `## Output contract` → `### booping defaults add`; entry shape per `### defaults.md`. Sidecar = the target's directory + `defaults.md`; first write seeds `# Defaults`; next id = highest `D{n}` + 1; heading time from `core.macros.date` with `+%Y-%m-%d %H:%M`. `--target` must resolve inside the vault; `--asked`, `--default` and `--why` are whitespace-normalised to one line before writing. Every check runs before the one write. Create `docs/defaults.md`, the format doc, in the shape of `docs/corrections.md`: where the sidecar sits, the entry shape, numbering, that `booping defaults add` is its only writer, and that a run with no artefact lists its defaults in its final report instead.

Tests: integration tier, txtar cases under `booping-python/e2e/cases/defaults/` — first add seeds the file and prints `plans/p/defaults.md#D1`; a second add appends `D2` below `D1`; a code-review target writes into `codereviews/{dir}/defaults.md` with the artefact link to `{ts}.md`; a multi-line `--asked` is written on one line; a target outside the vault, a missing target, an empty `--default` and a missing required flag are exit 1 with nothing written. Expected files hand-written.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | `defaults` command, `add` verb, seeding, numbering, entry rendering. | `booping-python/src/booping/cli.py`, `booping-python/src/booping/commands/defaults.py`, `booping-python/src/booping/defaults.py` | 2 | done |
| 2.2 | The txtar cases named in Tests. | `booping-python/e2e/cases/defaults/add-*.txtar` | 1 | done |
| 2.3 | Create the format doc. | `docs/defaults.md` | 1 | done |

## Definition of Done

### Task 2.1

- [x] `booping defaults --help` lists `add`; `add --help` lists `--target --step --asked --default --why`.
- [x] The written entry matches `index.md` `### defaults.md` line for line; stdout is `{sidecar}#D{n}` alone.
- [x] Every error path prints one `error: …` line on stderr, exits 1, leaves stdout empty and the sidecar untouched.

### Task 2.2

- [x] Every case pins the heading time through `macro_stubs` in the fixture `vault/config.yaml`.
- [x] One case per behaviour named in Tests.

### Task 2.3

- [x] `docs/defaults.md` restates no flag list — it links `booping defaults add --help` and holds only the format.

Return: the list of changed files, nothing else.

## References

- `booping-python/src/booping/correction.py` and `booping-python/src/booping/commands/correction.py` — the same sidecar writer; copy its seeding, numbering, target-relative links and error shape, minus the transcript lookup.
- `booping-python/e2e/cases/correction/add-the-first-entry-seeds-the-sidecar.txtar` — case layout and the `macro_stubs` date pin.
- `docs/corrections.md` — format-doc shape.

## Verify

`just e2e -k defaults`
