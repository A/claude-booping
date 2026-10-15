---
id: "01"
title: "booping correction add writes the corrections sidecar"
sp: 4
status: pending
plan: "plans/202610151532_corrections-log/index.md"
---

# M01: booping correction add writes the corrections sidecar

`booping correction add` appends the next `R{n}` entry to `corrections.md` beside the run artefact, seeding the file when missing, and prints `{sidecar}#R{n}`.

**Scope**: new top-level command `correction` with verb `add` (this milestone) — argparse shell `booping-python/src/booping/commands/correction.py` registered in `booping-python/src/booping/cli.py`, logic in a new `booping-python/src/booping/correction.py`. Flags `--target --step --did --said --why --session` per `index.md` `## I/O contract` (`--record` lands in M03). Sidecar = the target's directory + `corrections.md`; first write seeds `# Corrections`; next id = highest `R{n}` + 1; entry exactly as `index.md` `### corrections.md`, heading time from `core.macros.date` with `+%Y-%m-%d %H:%M`. This milestone always writes `**Dialogue:** not found — no session id` with the matching stderr warning when no session id is given; transcript lookup is M02. Every check runs before the one write, so an error never leaves a partial entry. Errors: missing target, empty `--said`, missing required flag — one `error: …` line, exit 1, nothing on stdout, nothing written.

Tests: integration tier, txtar cases under `booping-python/e2e/cases/correction/` — first add seeds the file and prints `plans/p/corrections.md#R1`; a second add appends `R2` below `R1`; a multi-line `--said` is blockquoted line by line; no `--why` writes `not stated`; a code-review target writes into `codereviews/{dir}/corrections.md` with the artefact link to `{ts}.md`; missing target and empty `--said` are exit 1 with no file written. Expected files hand-written.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | `correction` command, `add` verb, sidecar seeding, numbering, entry rendering. | `booping-python/src/booping/cli.py`, `booping-python/src/booping/commands/correction.py`, `booping-python/src/booping/correction.py` | 3 | pending |
| 1.2 | The txtar cases named in Tests. | `booping-python/e2e/cases/correction/add-*.txtar` | 1 | pending |

## Definition of Done

### Task 1.1

- [ ] `booping correction --help` lists `add`; `add --help` lists `--target --step --did --said --why --session`.
- [ ] The written entry matches `index.md` `### corrections.md` line for line, `**Record:**` absent; stdout is `{sidecar}#R{n}` alone.
- [ ] Every error path prints one `error: …` line on stderr, exits 1, leaves stdout empty and the sidecar untouched.

### Task 1.2

- [ ] Every case pins the heading time through `macro_stubs` in the fixture `vault/config.yaml`.
- [ ] One case per behaviour named in Tests; each failure case asserts stderr, an empty stdout and no `corrections.md` in `expected/`.

Return: the list of changed files, nothing else.

## References

- `booping-python/src/booping/commands/session_stats.py` — a top-level command's `add_parser` and `_fail` shape.
- `booping-python/src/booping/specs/open_items.py` — logic module apart from the argparse shell; the `core.macros.date` render (around line 151).
- `booping-python/e2e/cases/specs/open-items-add-by-hand-files-the-first-item.txtar` — case layout, `macro_stubs` date pin.

## Verify

`just e2e -k "correction and add"`
