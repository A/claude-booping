---
id: "01"
title: "render cases and the render-playbook gate"
sp: 4
status: done
plan: "vault/plans/202608131522_final-cli-commands-to-e2e/index.md"
---

# M01: render cases and the render-playbook gate

`booping render` is pinned at the CLI by txtar cases, the migration gate is pinned for both render surfaces, and `tests/commands/render_test.py` is deleted.

**Scope**: the `render` subcommand's whole flag surface (`--output`, `--set`, `--stub-macro`) and the migration gate shared with `render-playbook`. Files: new `booping-python/e2e/cases/render/*.txtar`; new cases in the existing `booping-python/e2e/cases/render-playbook/`; deleted `booping-python/tests/commands/render_test.py`. All fourteen existing tests already shell out to `bin/booping`, so this is a translation, not a re-derivation. Two of them need a different assertion than the unit used: plugin-root resolution is pinned by exit code rather than by the real template's text, and the gate notice's shipped-id is covered by `[..]` on a single line.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Write the `render` core cases: a relative template path resolved against the plugin root from a cwd where that path does not exist (exit 0 only, no stdout assertion), an inline `.j2` under `cwd` rendered to stdout, and `--output` writing the render to a file with stdout empty | `booping-python/e2e/cases/render/*.txtar` | 1 | done |
| 1.2 | Write the `--set` and `--stub-macro` cases: an override beating the core config value, repeated pairs where the later wins, a deep merge leaving sibling keys intact, a declared macro executing for real, `--stub-macro` returning the literal without executing, a stub key carrying call arguments, and the two malformed-pair exits | `booping-python/e2e/cases/render/*.txtar` | 2 | done |
| 1.3 | Write the gate cases in `cases/render-playbook/`: a behind vault gating `render`, a behind vault gating `render-playbook`, `migrate` exempt from the gate, `migrate --step survey` exempt, and `--project` pinning marker resolution to that root; then delete `tests/commands/render_test.py` | `booping-python/e2e/cases/render-playbook/*.txtar`, `booping-python/tests/commands/render_test.py` | 1 | done |

## Definition of Done

### Task 1.1

- [x] A case runs `booping render src/templates/skills/playbook.md.j2` from the `cwd` root, which contains no `src/` directory, and asserts exit 0 with no `stdout` section — a cwd-resolution regression exits 1 and fails the case.
- [x] A case seeds its own `.j2` under `fixtures/cwd/` and pins the rendered stdout in full.
- [x] A case with `--output out.md` asserts empty stdout and an `expected/cwd/out.md` section carrying the render.
- [x] No case in `cases/render/` asserts the text of a file under `src/templates/`.

### Task 1.2

- [x] The same fixture template renders the core default in one case and the overridden value in its `--set` sibling.
- [x] Repeated `--set` pairs on one invocation render the later value.
- [x] A `--set` on a nested key leaves its sibling keys present in the render.
- [x] A case invokes a `core.macros` entry for real and matches its output with `[..]`, not a literal.
- [x] A `--stub-macro` case renders the literal, and a sibling case pins a stub key that carries call arguments.
- [x] A `--set` argument with no `=` exits 1 with the malformed-pair message on stderr and empty stdout; the `--stub-macro` equivalent exits 1 with its own message.

### Task 1.3

- [x] A `.booping` marker seeded with a `latest_migration` behind the shipped ids makes `booping render` print the `**STOP — tell the user:**` notice on stdout at exit 0, with `[..]` covering the shipped id on that line.
- [x] The same marker gates `booping render-playbook` identically.
- [x] `booping render-playbook migrate` behind the same marker renders the playbook instead of the notice.
- [x] `booping render-playbook migrate --step survey` is likewise exempt.
- [x] A `--project` case shows the marker resolved from the named root rather than from cwd.
- [x] `tests/commands/render_test.py` no longer exists and `uv run pytest tests` is green without it.

## Verify

```
cd booping-python && uv run pytest e2e -k "render" && test ! -e tests/commands/render_test.py
```

The render and render-playbook cases are green with no `--txtar-update`, and the unit file is gone.
