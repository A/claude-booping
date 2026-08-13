---
title: "Migrate render-playbook and playbook-transition tests to the txtar e2e corpus"
type: "refactoring"
status: in-progress
sp: 37
related_to: null
created: 2026-08-13 11:30
planned: null
started: 2026-08-13 13:17
completed: null
code_reviews: []
sessions:
- 086d1f82-966e-4ba7-ae16-b89491381d25
- 250e5f1f-d15b-444c-8832-9efff5086ebf
retro: null
summary: render-playbook and playbook-transition units become txtar e2e cases; 
  both unit files deleted after cross-check
commit: 54ecd6967f2f7015a698810a295697326167c7db
agents.cross-review: a9556762c74fc37da
reviewed_at: 2026-08-13 12:48
---

# Migrate render-playbook and playbook-transition tests to the txtar e2e corpus

## Context

Five commands already own txtar contract cases — `scaffold` (pilot, plan 202608111422), `frontmatter-update` (202608121417), `config-get`, `marker-set` and `query` (202608130839) — and their CLI-shaped units were deleted as each migration closed. Two large surfaces still sit at the unit tier and reach their command through Python imports rather than `bin/booping`:

- `tests/test_render_playbook.py` — 131 tests, 1772 lines. Ten shell out to the binary; the rest call `compose()` / `compose_step()` in-process against the `tests/__fixtures__/render-playbook-home` tree (37 files, 12 fixture playbooks).
- `tests/commands/playbook_transition_test.py` — 46 tests, 759 lines. All but `test_cli_end_to_end` call `cmd._run(argparse.Namespace(...))` directly, planting fixture playbooks into an isolated `HOME` by `cp -r`.

Both commands are pure argv in → stdout, stderr, exit code, files out, which is exactly what the corpus expresses. After this lands, no CLI-boundary behaviour of either command is pinned by a Python unit test, both unit files are gone, and `pytest-txtar` is the single contract surface for seven of booping's thirteen subcommands. No production code changes and no user-visible behaviour change.

## Decisions

- **Tier line**: the corpus owns everything observable in the composed render or the transition report — section order, notices, subgraph expansion, the State section, Jinja modes, inline steps, the include search chain, lessons surfaces, `--set` overrides, macro stubs; bootstrap, edge validation, hooks, `--target` addressing (user call). `compose()` and `compose_step()` keep no in-process tests of their own: every fact they carry is readable from the rendered output.
- **Unit fate**: `tests/test_render_playbook.py` and `tests/commands/playbook_transition_test.py` are deleted wholesale after cross-check. The five `parse_set_overrides` tests move to `tests/utils_test.py` first — that function is pure `booping.utils` logic shared by `render`, `render-playbook` and `scaffold`, and its malformed-pair `ValueError` is a library contract, not a CLI one.
- **Fixture-tree fate is asymmetric**: `tests/__fixtures__/render-playbook-home` has no other consumer and is deleted with its file; `tests/__fixtures__/playbook-transition-home` stays — `tests/commands/playbook_state_test.py` and `tests/commands/playbook_run_integration_test.py` both plant from it and are out of scope.
- **Case granularity — one render pins many facts**: the units slice a single `compose()` result twenty ways (section order, then preamble, then the graph table, then each directive). A case pins the whole stdout at once, so a case count well under the test count is coverage-preserving, not coverage-losing. A separate case is written only when the *input* differs — a different manifest, flag, or fixture tree. Expect ~55–70 render-playbook cases against 131 tests.
- **Executable hook scripts via a `chmod` cmd line**: `pytest-txtar` fixtures carry content, not permissions ("A failure that needs an unwritable path or another OS-level fault is not expressible"), and `playbook_transition.py:268` rejects a script that fails `os.access(X_OK)`. The sandbox runs raw argv with no shell, so a leading `chmod +x ../home/Claude/_playbooks/{pb}/_scripts/{name}` cmd line is enough — probed during grooming and confirmed working, including the hook's side-effect file asserted through `expected/`. The non-executable rejection path needs no `chmod` and is a case in its own right.
- **A missing workdir is a fixture concern**: `playbook-transition` errors with `workdir not found` rather than creating one, so every transition case seeds its run directory with a `fixtures/cwd/{workdir}/.keep` entry — except the case that pins that error.
- **Notice overlap is accepted, not deduplicated**: `tests/context/playbook_test.py` (809 lines, out of scope) covers graph resolution and manifest parsing one layer down. The corpus pins the operator-facing notice *text* at exit 0; the units pin the resolution. Both stay.
- **Fixture playbooks are namespaced `fx-{behaviour}`**: every fixture playbook name carries the `fx-` prefix, so no fixture can collide with a shipped playbook now or when a new core playbook is added. The check is mechanical — `booping render-playbook` resolves names across all three roots, and a collision would surface as a name-clash notice in the case's own pinned output.
- **Fixture economy**: `pytest-txtar` has no shared fixtures — each case restates its tree. Cases inline the smallest playbook that shows the behaviour, never a copy of the 12-playbook fixture home.
- **Gap cases are in scope, behaviour fixes are not**: a behaviour the units never covered gets a case; a bug found while porting is recorded in the milestone and left unfixed.
- **Sprint runs past the 35 SP threshold by the user's call**: the split at the command seam was offered and declined — both migrations are the same port loop and land as one iteration.

## Architecture

Cases live in `booping-python/e2e/cases/render-playbook/*.txtar` and `booping-python/e2e/cases/playbook-transition/*.txtar`, one kebab-named file per behaviour, collected by the `pytest-txtar` plugin through the existing `e2e/conftest.py` spec: `commands={booping: bin/booping}`, `roots=(home, xdg, cwd)`, `cwd_root=cwd`, `env={HOME: home, XDG_CONFIG_HOME: xdg}`. The spec is unchanged by this plan — no runner work, no new root, no new token.

The sandbox maps onto both commands' discovery directly. `home_dir` defaults to `~/Claude`, so a fixture playbook is written at `fixtures/home/Claude/_playbooks/{name}/`, the global discovery root; a vault-local playbook is `fixtures/cwd/{vault}/_playbooks/{name}/` behind a `fixtures/cwd/.booping` marker, which is also what makes the local-over-global precedence cases expressible. Steps are directories holding `prompt.md`; hook scripts are `_scripts/{name}` under the playbook dir or under a discovery root's `_scripts/`.

`get_plugin_root()` resolves from the installed module path and takes no override, so every case additionally sees the real repository — its core playbooks, its `src/config.yaml`, and its `playbooks/_scripts/`. The corpus is therefore not fully hermetic, and the plan bounds that on purpose: fixture playbooks are `fx-`-prefixed so they cannot collide with a shipped name, and exactly one case is allowed to depend on shipped content — M05's core-tier include, which no fixture can supply. Any other case that would break when a core playbook or a shipped script changes is written differently instead.

Volatile spans use the `[..]` wildcard (log timestamps, macro-rendered dates where a `--stub-macro` is not the point of the case); sandbox absolute paths normalize to `{HOME}` / `{XDG}` / `{CWD}`. Multi-step behaviour is expressed as consecutive `cmd` lines whose output concatenates — a bootstrap followed by a move, or a transition followed by a `playbook-state` read-back — and a non-final line that exits non-zero aborts the case.

Corpus runtime grows with case count: 145 cases run serially in 62s today (~0.43s each, dominated by `uv run` startup), so this plan lands the corpus at roughly 260 cases and `just e2e` at roughly two minutes. No parallelisation work is in scope.

Rebaseline flow, from `booping-python/`: `uv run pytest e2e --txtar-update -k <expr>`, reviewing the rewritten sections as the assertion. Runner: `just e2e`, and `just ci` for the full gate.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [render-playbook baseline — composed render, notices and the CLI surface](milestones/M01-render-playbook-baseline/M01-render-playbook-baseline.md) | 4 | done |
| 02 | [render-playbook subgraphs](milestones/M02-render-playbook-subgraphs/M02-render-playbook-subgraphs.md) | 4 | done |
| 03 | [render-playbook state machines](milestones/M03-render-playbook-state-machines/M03-render-playbook-state-machines.md) | 3 | done |
| 04 | [render-playbook Jinja modes and inline steps](milestones/M04-render-playbook-jinja-and-inline-steps/M04-render-playbook-jinja-and-inline-steps.md) | 4 | done |
| 05 | [render-playbook include chain and macro stubs](milestones/M05-render-playbook-includes-and-macros/M05-render-playbook-includes-and-macros.md) | 2 | done |
| 06 | [render-playbook lessons surfaces](milestones/M06-render-playbook-lessons/M06-render-playbook-lessons.md) | 3 | done |
| 07 | [render-playbook --set overrides and the parse_set_overrides move](milestones/M07-render-playbook-set-overrides/M07-render-playbook-set-overrides.md) | 2 | done |
| 08 | [render-playbook cross-check and unit deletion](milestones/M08-render-playbook-cross-check/M08-render-playbook-cross-check.md) | 3 | done |
| 09 | [playbook-transition bootstrap, edges and the report](milestones/M09-transition-bootstrap-and-edges/M09-transition-bootstrap-and-edges.md) | 3 | pending |
| 10 | [playbook-transition hooks](milestones/M10-transition-hooks/M10-transition-hooks.md) | 4 | pending |
| 11 | [playbook-transition --target addressing](milestones/M11-transition-target-addressing/M11-transition-target-addressing.md) | 3 | pending |
| 12 | [playbook-transition cross-check and unit deletion](milestones/M12-transition-cross-check/M12-transition-cross-check.md) | 2 | pending |

## I/O contract

Both surfaces are pinned as they stand today — this plan documents the contract the corpus asserts, it does not change it.

**`booping render-playbook`**

- Arguments / flags: `booping render-playbook <name> [--step NAME] [--project PATH] [--output PATH] [--set KEY=VALUE] [--stub-macro DOTTED.PATH=LITERAL] [--no-lessons] [--inline-steps]`.
- stdin: not read.
- stdout: the composed markdown render — notices, preamble, optional `## Lessons`, `## Playbook Steps` table, one `## Step:` section per step, `## Subgraph:` intros, optional `## State` section. With `--step`, the bare step body plus its step-targeted lessons. With `--output PATH`, stdout is empty and the render lands in the file.
- stderr: one log line per invocation when a vault is attached; graph and render problems do **not** go here.
- Exit codes: `0` on success, including every in-band `**STOP — tell the user:**` and `**Note — tell the user:**` notice; `1` for an unknown playbook, an unknown `--step`, a malformed `--set` pair, and a `requires_project` playbook with no project.

**`booping playbook-transition`**

- Arguments / flags: `booping playbook-transition <playbook> <to> [--state NAME] [--instance SLUG] [--target PATH] [--workdir PATH]`.
- stdin: not read.
- stdout: the mutation report — `created {artifact}` on bootstrap, `{from} → {to}`, one `frontmatter: k=v` line per key written, one `script {name}: ok` line per script hook run.
- stderr: the failing hook's own stderr, relayed verbatim, and the `error: …` line on any refusal.
- Exit codes: `0` on a taken or idempotent edge; `1` for user error — unknown playbook, unknown state, a playbook without `states:`, an illegal edge (stderr lists the allowed targets), a missing workdir, a missing artifact with a non-initial target, `--target` and `--instance` together, a missing or degenerate frontmatter block; `2` for a hook fault — a script that exits non-zero, a script that is missing or not executable, an unknown hook verb, a `frontmatter-update` file target that is missing or needs an instance it was not given.

## Final Verification

- [ ] `just e2e` green, with `e2e/cases/render-playbook/` and `e2e/cases/playbook-transition/` collected.
- [ ] `just pytest` green with both unit files deleted and `tests/__fixtures__/render-playbook-home/` gone.
- [ ] `just ci` green end to end.
- [ ] `rg -n "render_playbook|playbook_transition" booping-python/tests` returns only out-of-scope consumers (`playbook_state_test.py`, `playbook_run_integration_test.py`, `tests/context/playbook_test.py`).
- [ ] Every deleted test has a named corpus case recorded in M08 and M12 cross-check tables.
- [ ] `booping-python/e2e/README.md` documents the `chmod` pattern for executable hook fixtures.

## Out of scope

- The other unmigrated commands — `playbook-state`, `session-stats`, `render`, `build`, `debug-context`, `debug-template`. Each is its own later run.
- `tests/context/**`, `tests/templates/**`, `tests/scripts/**`, `tests/macros_test.py`, `tests/rendering_test.py`, `tests/migrations_test.py` — not CLI-boundary tests.
- Any change to `pytest-txtar` itself, including a file-mode marker that would retire the `chmod` line. If the pattern proves noisy across M10, it is filed upstream as a follow-up, not implemented here.
- Corpus parallelisation (`pytest-xdist`) and any other runtime work.
- Fixing any behaviour a port exposes as wrong.

## CLAUDE.md impact

No CLAUDE.md changes required — the `booping-python/` layout entry already states that the contract corpus lives in `e2e/` and that `scaffold` is verified there rather than by the unit tests. That sentence names `scaffold` only as the pilot example and stays accurate. The `just e2e` and `just ci` lines are unchanged.
