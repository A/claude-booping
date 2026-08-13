---
title: "Migrate the last CLI commands to the txtar e2e corpus"
type: "refactoring"
status: in-progress
sp: 28
related_to: null
created: 2026-08-13 15:22
planned: null
started: 2026-08-13 16:15
completed: null
code_reviews: []
sessions:
- d26525cc-dca0-4570-bfd5-a097daef66a1
- 7a06a5f1-8b6e-42d2-8acb-9ab95d36d310
retro: null
summary: Last CLI commands reach the txtar corpus; build and debug-template 
  retired, tests/commands emptied
commit: 67853c9b4ec7cb1c84320bb87f52107bd01e91a8
reviewed_at: 2026-08-13 16:06
---

# Migrate the last CLI commands to the txtar e2e corpus

## Context

Seven subcommands already own txtar contract cases — `scaffold` (plan 202608111422), `frontmatter-update` (202608121417), `config-get`, `marker-set`, `query` (202608130839), `render-playbook` and `playbook-transition` (202608131129) — and each migration deleted its CLI-shaped unit file as it closed. Six commands are still outside the corpus, and `booping-python/tests/commands/` still exists to hold four of them.

This plan closes the split. `render`, `playbook-state` and `session-stats` gain cases and lose their units; `debug-context` gains its first coverage; `build` and `debug-template` are deleted rather than pinned. After it lands, `pytest-txtar` is the single CLI contract surface for all eleven surviving subcommands, `tests/commands/` is gone, and `booping-python/tests/` holds only library-tier tests.

**Goal after landing**: reading a command's contract means reading one directory of txtar files, and there is one build pipeline instead of two.

No production behaviour changes for any surviving command. Two dev-facing commands disappear; neither is reachable from a rendered surface, a playbook, or `just ci`.

## Decisions

- **`build` is retired, not migrated.** It takes no path arguments and resolves the plugin root from the installed module path, ignoring `HOME`, `XDG_CONFIG_HOME` and cwd — the only three roots the sandbox controls. A case would render the real `src/files/` and overwrite the repository's committed `skills/` and `agents/` mid-run. Its three templates carry exactly one Jinja expression each, an `effort:` frontmatter value, and the rendered destinations already hold the inlined value — verified at grooming: `skills/playbook/SKILL.md` and `agents/booping-developer.md` carry `effort: medium`, `agents/booping-researcher.md` carries `effort: high`, matching `src/config_files.yaml` exactly. So the templates, `src/config_files.yaml`, the subcommand and the `build` / `dev` justfile recipes all delete with **zero content change** to the three destinations, which stop being artefacts and become hand-authored source. Nothing regenerates them once the templates are gone; the only way they can drift before M09 lands is a `just build` run mid-sprint, which M09 guards against by confirming them unmodified immediately before the deletion.
- **`debug-template` is retired.** A `not implemented` stub printing to stderr at exit 1 since the original CLI plan (20260429), superseded by `render`. `booping/commands/debug.py` survives — it also owns `debug-context`.
- **`debug-context` gets exit-and-stderr cases only, stdout unasserted.** Its stdout is a full `Context` dump enumerating every core playbook, skill and agent, and `text_matches` rejects on unequal line counts before any wildcard applies, so `[..]` cannot absorb a list whose length changes when a playbook is added. Piping to a validator is not available either: cmd lines are `shlex.split` + `subprocess.run` with no shell, only `argv[0]` is rewritten to `bin/booping`, and stdout is captured in-process and never reaches disk for a second cmd line to read. A YAML-validity assertion would test PyYAML rather than booping, since `yaml.dump` cannot emit invalid YAML. The residual case — exit 0, empty stderr — pins the class of the `git_commit under project` regression and nothing more, and each case file says so in a comment.
- **`session-stats` is mostly not a CLI migration.** Of its ~41 tests, 28 call `locate_transcript`, `parse_transcript`, `summarize` or `build_report` directly and never touch the CLI: turn-span arithmetic, blocking-span subtraction, token and model extraction, malformed-line counting, denial-kind classification. Those stay at the library tier — the CLI is a thin JSON-and-frontmatter wrapper, and re-deriving each edge case from argv would mean a fixture corpus per test. 13 CLI-shaped tests migrate; one drops.
- **One test drops as redundant**: `test_cli_registers_session_stats_with_contract_defaults` inspects an argparse `Namespace` and produces no output. Its defaults (`mask="index.md"`, `force=False`, `dry_run=False`, `projects_root=None`) are covered behaviourally by cases that simply omit the flags.
- **Two tests stay as units on a mechanical blocker**: `test_report_writes_nothing` (playbook-state) needs `st_mtime` / `st_size` snapshots, and `compare` only reads files named in an `expected/` section — a case can show byte-identical content but cannot distinguish "not written" from "rewritten identically", which is the property under test for a read-only reporter.
- **The non-hermeticity budget widens from one case to a stated rule.** The prior plan allowed exactly one case to depend on shipped content. Here the rule is: a case may depend on shipped content **when the behaviour under test is about shipped content**, and it must depend on that content's *existence*, never its *extent*. The migration gate qualifies — its notice is one line carrying `latest shipped {id}`, so `[..]` covers the id at a stable line count, and the dependency reduces to "at least one migration ships", which is permanent. The `migrate` exemptions qualify. A case that would break when a core playbook is *added* does not qualify and is written differently.
- **`render`'s plugin-root resolution is pinned by exit code, not output.** `test_render_resolves_relative_path_against_plugin_root_not_cwd` asserts real `src/templates/skills/playbook.md.j2` text, which drifts on every live template edit. The case instead runs the render from a cwd where that relative path does not exist and asserts exit 0 — a cwd-resolution bug exits 1. Same property, no volatile text.
- **`render_test.py` is two commands.** Four of its tests drive `render-playbook` (the migration gate and the two `migrate` exemptions, plus `--project` marker pinning). Those cases land in the existing `cases/render-playbook/`, not in a new `cases/render/`.
- **`session-stats` transcripts move under the sandbox.** The unit fixtures live at `tests/fixtures/session_stats/` with `--projects-root` pointing inside the test tree. Cases seed transcripts at `fixtures/home/.claude/projects/{slug}/{id}.jsonl` to exercise the default root, and one case passes `--projects-root` explicitly against a cwd-rooted tree. Transcripts are hand-written to the minimum shape each case needs — never copied from the fixture tree, which stays for the library tests.
- **Fixture economy and `fx-` namespacing carry over** from the prior plan unchanged: each case restates the smallest tree that shows the behaviour, and every fixture playbook name is `fx-`-prefixed so it cannot collide with a shipped playbook.
- **One iteration despite the command count.** The user's call: these are smaller surfaces than the prior sprint's two, and the produced artefacts are almost entirely txtar cases, whose review burden is low. The total lands under the 35 SP threshold regardless.
- **Gap cases are in scope, behaviour fixes are not** — a behaviour the units never covered gets a case; a bug found while porting is recorded in the milestone and left unfixed.

## Architecture

Cases live in `booping-python/e2e/cases/{command}/*.txtar`, one kebab-named file per behaviour, collected by `pytest-txtar` 0.1.0 through the existing `e2e/conftest.py` spec: `commands={booping: bin/booping}`, `roots=(home, xdg, cwd)`, `cwd_root=cwd`, `env={HOME: home, XDG_CONFIG_HOME: xdg}`. The spec is unchanged by this plan — no runner work, no new root, no new token, no dependency bump. `pytest-txtar` 0.1.0 is the only published release, and it ships no file-mode marker and no whole-tree assertion, so the `chmod +x` cmd-line pattern for executable hook fixtures stays as the prior plan documented it.

New case directories: `cases/render/`, `cases/playbook-state/`, `cases/session-stats/`, `cases/debug-context/`. `cases/render-playbook/` gains the four gate and exemption cases.

`tests/conftest.py`'s autouse `isolated_xdg_config_home` fixture is exactly the `HOME` / `XDG_CONFIG_HOME` isolation the sandbox provides natively, so no ported case carries setup for it.

Three fixture trees are in play and their fates differ:

- `tests/__fixtures__/playbook-transition-home/` — its last two consumers are both in scope (`playbook_state_test.py` plants `runner`, `graphonly`, `targetless`, `sharded`; `playbook_run_integration_test.py` plants `runner`). Deleted with them. Its `runner/_scripts/*` and `targetless/_scripts/check-findings` are mode-755 shell scripts reached through `script` hooks, so any case bootstrapping those machines carries a leading `chmod +x` cmd line.
- `tests/fixtures/session_stats/` — **survives**. The 28 library tests still read its transcripts and vault artifacts.
- No fixture tree is created by this plan; cases inline their own trees.

After the retirement, the plugin has **one** rendering pipeline — runtime only, at skill-load time, through `booping render`. `src/files/`, `src/config_files.yaml` and the build stage disappear, and `git diff -- skills/ agents/` stops being a drift signal because those files have no upstream.

Corpus runtime grows with case count. The corpus stands at roughly 260 cases running serially at ~0.43s each, dominated by `uv run` startup; this plan adds roughly 45 cases, putting `just e2e` near two and a half minutes. No parallelisation work is in scope.

Rebaseline flow, from `booping-python/`: `uv run pytest e2e --txtar-update -k <expr>`, reviewing the rewritten sections as the assertion. Runner: `just e2e`, and `just ci` for the full gate.

### Execution order

Milestones run in id order, and three carry hard dependencies that id order already satisfies — stated here because the generated table has no dependency column:

- **M04** requires M02 and M03. It deletes `playbook_state_test.py`, which cannot happen until every argv-expressible test in that file has a case.
- **M07** requires M05 and M06. It deletes the CLI tests from `test_session_stats.py`, which cannot happen until their cases exist.
- **M10** requires all nine others. Its cross-check table is a projection of what they produced.

M01, M08 and M09 are independent of everything else and may run in any position. No milestone may delete a test before the milestone that covers it has closed.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [render cases and the render-playbook gate](milestones/M01-render-and-gate-cases/M01-render-and-gate-cases.md) | 4 | done |
| 02 | [playbook-state report shape and ordering](milestones/M02-playbook-state-report/M02-playbook-state-report.md) | 3 | done |
| 03 | [playbook-state target addressing and error exits](milestones/M03-playbook-state-addressing/M03-playbook-state-addressing.md) | 3 | done |
| 04 | [the run walk and the fixture-home retirement](milestones/M04-run-walk-and-fixture-retirement/M04-run-walk-and-fixture-retirement.md) | 3 | done |
| 05 | [session-stats read path](milestones/M05-session-stats-read-path/M05-session-stats-read-path.md) | 3 | done |
| 06 | [session-stats write path](milestones/M06-session-stats-write-path/M06-session-stats-write-path.md) | 3 | done |
| 07 | [the session-stats tier split](milestones/M07-session-stats-tier-split/M07-session-stats-tier-split.md) | 2 | done |
| 08 | [debug-context cases](milestones/M08-debug-context-cases/M08-debug-context-cases.md) | 1 | done |
| 09 | [retiring build and debug-template](milestones/M09-retire-build-and-debug-template/M09-retire-build-and-debug-template.md) | 4 | done |
| 10 | [corpus cross-check and tier audit](milestones/M10-cross-check-and-tier-audit/M10-cross-check-and-tier-audit.md) | 2 | done |

## I/O contract

Every surviving command is pinned as it stands today — this plan documents the contract the corpus asserts, it does not change it.

**`booping render`**

- Arguments / flags: `booping render <path> [--output PATH] [--set KEY=VALUE] [--stub-macro DOTTED.PATH=LITERAL]`. `<path>` is a `.j2` template; a relative path resolves against the plugin root, never cwd. `--set` and `--stub-macro` are repeatable, later pairs win, `--set` deep-merges over every config tier for this render only.
- stdin: not read.
- stdout: the rendered template text, or nothing when `--output` is given (the file is written instead, parents created).
- stderr: one log line per invocation when a vault is attached; `error: malformed --set pair (expected KEY=VALUE): …`; `error: malformed --stub-macro pair (expected DOTTED.PATH=LITERAL): …`; `error: {MacroError}`.
- Exit codes: `0` on success, **including** the migration gate — when the vault is behind, the `**STOP — tell the user:**` notice is emitted in place of the render and the process still exits 0. `1` for a malformed `--set` pair, a malformed `--stub-macro` pair, or a `MacroError` during rendering.

**`booping playbook-state`**

- Arguments / flags: `booping playbook-state <playbook> [--target PATH] [--workdir PATH]`. `--workdir` defaults to cwd; a relative `--target` resolves against the workdir and overrides every machine's declared `artifact:` for the whole report.
- stdin: not read.
- stdout: one YAML document — `{playbook, workdir, states: {name: {artifact, status|instances, next?}}}` — states ordered outer-graph-first, `sort_keys=False`. A `not-started` status carries a synthetic `next: [{to: <initial>, when: "run not started — bootstrap the artifact"}]`; a terminal status omits `next`.
- stderr: `error: …` preceding every non-zero exit; a `.booping.log` append when a vault resolves from the workdir.
- Exit codes: `0` on a report. `1` for `workdir not found`, `playbook not found` (stderr lists the known names), a playbook declaring no `states:`, and a machine with no declared `artifact:` invoked without `--target`.

**`booping session-stats`**

- Arguments / flags: `booping session-stats <path> [--mask GLOB] [--force] [--dry-run] [--projects-root PATH]`. `<path>` is an artifact file, or a directory walked by `--mask` (default `index.md`). `--projects-root` defaults to `~/.claude/projects`.
- stdin: not read.
- stdout: exactly one JSON document, `{"artifacts": [...]}`, `indent=2`, printed once at the end. Each entry carries `path`, `written`, and either `skipped` with empty `sessions` / `totals`, or full `sessions` and `totals` keyed by the six `metrics_*` frontmatter names verbatim.
- stderr: `note: no sessions: key in {path}; skipped`; `warning: no transcript found for session {id}`; `warning: skipped {n} malformed line(s) in {path}`; an `error: …` line before every non-zero exit. Warnings and notes are non-fatal.
- Exit codes: `0` on completion, including runs where every artifact skipped or warned. `1` for `path not found`, `no artifact matching {mask} under {root}`, unreadable frontmatter, and a `sessions:` key that is not a list. `2` for a write failure.

**`booping debug-context`**

- Arguments / flags: `booping debug-context`, no flags.
- stdin: not read.
- stdout: the assembled `Context` as YAML, `sort_keys=True`, with `skills` and `agents` reduced to sorted name lists and every `body` in `plans`, `lessons`, `plan_templates` and `review_templates` collapsed to `<N lines>`.
- stderr: empty on success.
- Exit codes: `0` on a successful assembly. Any loader failure propagates as an unhandled exception.

**Deleted surfaces**: `booping build` (rendered `src/files/**/*.j2` to plugin-root destinations, `wrote {n} files` on stderr, exit 2 on a missing root, missing config, render failure or write failure) and `booping debug-template` (printed `not implemented: debug-template` to stderr, exit 1).

## Final Verification

- [ ] `just e2e` green, with `cases/render/`, `cases/playbook-state/`, `cases/session-stats/` and `cases/debug-context/` collected.
- [ ] `just pytest` green with `booping-python/tests/commands/` and `tests/__fixtures__/playbook-transition-home/` both gone.
- [ ] `just ci` green end to end.
- [ ] `bin/booping --help` lists eleven subcommands, with no `build` and no `debug-template`.
- [ ] `rg -n "booping build|src/files|config_files" --glob '!vault/**'` returns nothing outside this plan's own artefacts.
- [ ] `git diff --stat -- skills/ agents/` is empty across the whole sprint — the retirement changes no rendered surface.
- [ ] Every deleted test has a named corpus case, a named surviving unit, or a recorded drop rationale in M10's cross-check table.

## Out of scope

- **Any production behaviour change to a surviving command**, including a flag that would make `debug-context` pinnable.
- `tests/context/**`, `tests/templates/**`, `tests/scripts/**`, `tests/macros_test.py`, `tests/rendering_test.py`, `tests/migrations_test.py`, `tests/utils_test.py`, `tests/query_test.py`, `tests/test_logger.py` — library tier, untouched.
- `tests/fixtures/session_stats/` — kept for the surviving library tests, not trimmed.
- Any change to `pytest-txtar` itself, including the file-mode marker that would retire the `chmod` line and a whole-tree assertion that would retire the `test_report_writes_nothing` unit. Both are filed upstream as follow-ups if the friction recurs, not implemented here.
- Corpus parallelisation (`pytest-xdist`) and any other runtime work.
- Fixing any behaviour a port exposes as wrong.
- The public `documentation/` site, which never mentions `build` or `debug-template`.

## Risk register

- **`debug-context` coverage is deliberately weak.** Exit and stderr only. Accepted: the alternative is a production flag, which this plan's DoD forbids. Recorded in M08's case comments so a later reader does not mistake it for a content contract.
- **The non-hermeticity rule is judgement, not a mechanism.** Nothing enforces "existence, never extent" — a future case can quietly depend on a playbook count. Mitigated by stating the rule in `e2e/README.md` in M10, where a case author will read it.

## CLAUDE.md impact

Substantial, and it is M09's work, not a follow-up:

- The `## Commands` `just build` line is deleted.
- The `## Layout` entries for `src/config_files.yaml` and `src/files/<rel>.j2` are deleted; the `skills/<name>/SKILL.md`, `agents/<name>.md` entry is rewritten from "build artefacts, never hand-edit" to hand-authored thin shells.
- The `bin/booping <subcommand>` list drops `build` and `debug-template`.
- `## Rendering pipelines` collapses from two numbered stages to one runtime stage.
- The `## Editing conventions` first bullet loses its `src/files/**` clause and its `git diff -- skills/ agents/` drift signal.
- The `## Principles` closing bullet's reference to `src/files/skills/playbook/SKILL.md.j2` is repointed at the surviving `skills/playbook/SKILL.md`.

Also in M09: `docs/plan_templates/claude_skill.md`'s `just build` checklist item, and `vault/docs/_specs/targets.md`'s two build-artefact lines.
