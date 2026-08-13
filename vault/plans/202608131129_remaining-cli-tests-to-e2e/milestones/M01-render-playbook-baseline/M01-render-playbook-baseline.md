---
id: "01"
title: "render-playbook baseline — composed render, notices and the CLI surface"
sp: 4
status: done
plan: "vault/plans/202608131129_remaining-cli-tests-to-e2e/index.md"
---

# M01: render-playbook baseline — composed render, notices and the CLI surface

`booping render-playbook` has a txtar case directory whose cases pin the whole composed render, the graph notices, and the command's flag surface and exit codes.

**Scope**: the `render-playbook` subcommand, no flags beyond `--step`, `--project` and `--output`. Files: new `booping-python/e2e/cases/render-playbook/*.txtar`. This milestone establishes the fixture conventions every later render-playbook milestone reuses — a playbook at `fixtures/home/Claude/_playbooks/{name}/playbook.md` with `playbook.yaml` and one `{step}/prompt.md` per step, and a `fixtures/cwd/.booping` marker plus vault only where a project is needed. Ported from the `happy path`, `notices`, `io frontmatter` and `CLI-level` sections of `tests/test_render_playbook.py`; nothing is deleted here.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Composed-render cases over one multi-wave fixture playbook: full section order in one stdout block, the preamble passing through verbatim, the step table's rows in dependency order with their summary and gate cells, and a clean render carrying no notice line | `booping-python/e2e/cases/render-playbook/*.txtar` | 1 | done |
| 1.2 | Step-section cases: the delegation bullet order for a runner-performed step, a `<model>:<effort>` detached step and a named detached step; a detached section dropping its dependency and sibling bullets; a single-member wave showing `After:` and no `Parallel:`; the gate directive relayed verbatim; the summary leading the bullets | `booping-python/e2e/cases/render-playbook/*.txtar` | 1 | done |
| 1.3 | Notice cases, one fixture playbook per fault: a step named in the graph with no directory, an unknown dependency, a cycle, no `graph:` at all, an inline step sharing a parallel wave, a `graph:` in both manifest surfaces, a bad manifest, and the non-blocking orphan-step note. Plus the io-keys case: `io:`-style frontmatter keys never reach the render | `booping-python/e2e/cases/render-playbook/*.txtar` | 1 | done |
| 1.4 | CLI-surface cases: unknown playbook exits 1; a `requires_project` playbook without a project exits 1 and with `--project` renders; `--output PATH` writes the render and leaves stdout empty; `--step` prints the bare body and appends the log line; an unknown `--step` exits 1; the default render reaches stdout | `booping-python/e2e/cases/render-playbook/*.txtar` | 1 | done |

## Definition of Done

### Task 1.1

- [x] A case renders a fixture playbook with at least two waves and pins the entire stdout: preamble, `## Playbook Steps` table, then one `## Step:` section per step, in that order.
- [x] The preamble body appears character-for-character as written in `playbook.md`, with no added heading.
- [x] The step table's `Dependencies`, summary and review-gate cells are asserted in the same stdout block, and the row order follows the topological waves rather than manifest order.
- [x] The happy-path case's stdout contains no `**STOP — tell the user:**` and no `**Note — tell the user:**` line.
- [x] Every fixture playbook this milestone writes is named `fx-{behaviour}`, and no case's pinned output carries a name-clash notice — the convention every later render-playbook milestone inherits.

### Task 1.2

- [x] A runner-performed step's section shows its bullets in the documented order, and its `Run:` fetch line names `booping render-playbook {name} --step {step}`.
- [x] A `detached: opus:high`-style step renders the generic sub-agent bullet naming both model and effort; a named `detached: some-agent` step renders the named-agent bullet.
- [x] A detached step's section carries no dependency or sibling bullets, asserted by the absence of those lines in its section slice.
- [x] A step alone in its wave renders an `After:` bullet and no `Parallel:` bullet.
- [x] A step declaring a review gate relays the gate text verbatim.

### Task 1.3

- [x] Each of the eight fault fixtures renders at exit 0 with its notice line in stdout, and the notice text is pinned in full — no wildcard over the part that names the offending step, dependency or playbook.
- [x] The cycle and unknown-dependency notices name the steps involved.
- [x] The orphan-step note appears without a `**STOP` line, and the render still carries its step sections — proving it is non-blocking.
- [x] A playbook whose frontmatter carries `io:`-shaped keys renders no trace of them in any section.

### Task 1.4

- [x] `booping render-playbook nope` exits 1 with a message naming the playbook, and stdout is empty.
- [x] A `requires_project: true` playbook exits 1 with no project attached; the same case's sibling with `--project {vault}` exits 0 and renders.
- [x] `--output out.md` exits 0, leaves stdout empty, and `expected/cwd/out.md` carries the render.
- [x] `--step {name}` prints only that step's body — no table, no preamble — and appends one line to `expected/cwd/{vault}/.booping.log` with the timestamp wildcarded.
- [x] `--step nope` exits 1 with a message naming the step.

## Verify

```
cd booping-python && uv run pytest e2e -k render-playbook
```

Every case passes without `--txtar-update`, and a follow-up `--txtar-update` run leaves the working tree clean.
