# Request

> check what's left to migrate to e2e tests
>
> groom next migration. I think, all can be there?

## Task type

`refactoring` — the work moves existing CLI-boundary coverage from Python unit tests to txtar contract cases and adds cases for two commands that have none. No production code changes, no user-visible behaviour change.

- Not `feature`: nothing new reaches a user; every command already exists and keeps its exact surface.
- Not `bug`: no observed divergence between actual and expected behaviour is being fixed. Per the prior migration's rule, a defect exposed while porting is recorded, not fixed.

## Problem

Seven of booping's thirteen subcommands are pinned by the txtar contract corpus (`scaffold`, `frontmatter-update`, `config-get`, `marker-set`, `query`, `render-playbook`, `playbook-transition`), and each migration deleted its CLI-shaped unit file as it closed. Six commands are still outside the corpus:

| Command | Unit file | Lines | Disposition |
| --- | --- | --- | --- |
| `session-stats` | `tests/test_session_stats.py` | 372 | migrate |
| `playbook-state` | `tests/commands/playbook_state_test.py` | 328 | migrate |
| `render` | `tests/commands/render_test.py` | 180 | migrate |
| `build` | `tests/commands/build_test.py` | 89 | retire the command |
| `debug-context` | — | none | new coverage |
| `debug-template` | — | none | retire the command |

Plus `tests/commands/playbook_run_integration_test.py` (94 lines), which already drives `bin/booping` as a subprocess across `playbook-transition` + `playbook-state` and is the natural multi-`cmd`-line txtar case.

The consequence today: the contract surface is split in two. Half the CLI is pinned at argv-in/stdout-out, half reaches its command through Python imports, and two commands are pinned by nothing at all. Contributors have no single place to read what a command promises.

## Goal after this lands

`pytest-txtar` is booping's single CLI contract surface — every surviving subcommand has cases, and `booping-python/tests/` holds only library-tier tests (`tests/context/**`, `tests/templates/**`, `tests/scripts/**`, `macros_test.py`, `rendering_test.py`, `migrations_test.py`, `utils_test.py`, `query_test.py`, `test_logger.py`). `tests/commands/` is gone entirely, and reading a command's contract means reading one directory of txtar files.

## Clarifications and Decisions

- Scope is every remaining command, in one plan — the user's call, against the prior plan's "each is its own later run".
- **`build` is retired, not migrated.** It takes no path arguments and ignores `HOME` / `XDG_CONFIG_HOME` / cwd, resolving the plugin root from the installed module path, so a corpus case would render the real `src/files/` and overwrite the repo's committed `skills/` and `agents/` mid-run. Each of its three templates carries exactly one Jinja expression — an `effort:` frontmatter value — and the rendered destinations already hold the inlined value, so `src/files/`, `src/config_files.yaml`, the `build` subcommand and the `build` / `dev` justfile recipes all delete with no content change to `skills/playbook/SKILL.md` or `agents/*.md`; they simply become hand-authored source.
- **`debug-template` is retired.** It has been a `not implemented` stub printing to stderr at exit 1 since the original CLI plan, and `render` covers the job.
- **`debug-context` stays and gains coverage.** It is not a `config-get` alias: `config-get` resolves one dotted path inside `ctx.config` and requires a key, while `debug-context` dumps the whole assembled `Context` — config plus `project`, `skills`, `agents`, `plans`, `lessons`, `plan_templates`, `review_templates`, `playbooks` — with bodies collapsed to `<N lines>`. It is documented publicly as the way to inspect assembled context.
- `tests/__fixtures__/playbook-transition-home` is retired with the `playbook-state` and run-integration ports, since those are its last two consumers.
- The library tier stays untouched, exactly as the prior migration bounded it.
- **One iteration even past 35 SP** — the user's call. The prior sprint's 37 SP covered two large commands; these are smaller surfaces and the produced artefacts are almost entirely txtar cases, which carry a low review burden.

## Open design risk

`debug-context` dumps the real plugin root's playbook, skill and agent lists, so a case pinning the full YAML breaks whenever a core playbook is added — the exact fragility the prior plan's non-hermeticity rule forbids. The plan must settle how the case asserts (wildcards over the volatile lists, or vault-derived subtrees only).
