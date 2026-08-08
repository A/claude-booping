---
title: Booping Global Config + home_dir
type: feature
status: done
sp: 11
split_from: plans/20260722-playbooks-framework-pilot.md
created: 2026-07-22 23:38
planned: 20260722 11:24
started: 20260722 11:41
completed: 2026-07-22 12:02
retro: retrospectives/20260722-seven-plan-retro.md
goal: success|partial|fail
summary: "Global config tier at ~/.config/booping/config.yaml with home_dir key; vault
  resolution moves off hardcoded ~/Claude"
commit: 1cfd8641275c0c6d34ced8c552815097cc6cb73d
sessions:
- edc8db2c-f522-4311-9cc5-c43fc0399d15
- 3515f801-989d-4aa5-a36f-f9d1acebde90
metrics_active_minutes: 39
metrics_models:
- claude-fable-5
metrics_tokens_input: 89724
metrics_tokens_output: 159179
metrics_tokens_cache_creation: 646357
metrics_tokens_cache_read: 13675249
---

# Booping Global Config + home_dir

Split from the playbooks plan (combined SP exceeded the 35 split threshold; this work is independent).

## Context

Vault home is hardcoded to `~/Claude/` in two code sites — `booping-python/src/booping/context/project.py::_resolve_vault_dir` (`Path.home() / "Claude"`) and `bin/booping-create-project` (`$HOME/Claude/$PROJECT`). `Config.load()` already accepts an ordered override-paths list; CLAUDE.md reserves the global-tier slot.

After this plan: a full global config tier at `${XDG_CONFIG_HOME:-~/.config}/booping/config.yaml` deep-merges between core and project tiers (core → global → project); a `home_dir` key (default `~/Claude/`) drives vault resolution in both code sites; a new `booping config-get` subcommand exposes resolved config values to shell callers; `booping-create-project` seeds the global config interactively on first run when neither config nor `~/Claude` exists. **Config mechanism only — no vault content migration and no prose sweep of templates/docs** (user moves `~/Claude` to `~/Dev/@A/notes/projects/` manually and verifies in the final milestone; existing `~/Claude` doc mentions stay true as the default).

**Resolution-order constraint (chicken-egg)**: today `Context.assemble` resolves the vault first, then loads project config from it. `home_dir` lives in config but determines the vault location. New order: load core + global tiers → read `home_dir` → resolve vault (`.booping` `vault_path:` still wins) → re-merge with project tier `<vault>/config.yaml`.

## Decisions

- **Global config path**: `${XDG_CONFIG_HOME:-~/.config}/booping/config.yaml` — XDG-correct, avoids home_dir-inside-home_dir circularity (user-confirmed).
- **Tier scope**: full config tier, not home_dir-only — deep-merges like the project tier, same `shallow_merge_keys=["agents"]` semantics. Merge order `core → global → project` (user-confirmed).
- **`home_dir` key**: top-level `home_dir: ~/Claude/` default added to `src/config.yaml`. Vault default = `home_dir / project_name`. Precedence: `.booping` `vault_path:` > global `home_dir` > core default. A `home_dir` set in the *project* tier has no effect (vault is already resolved by then) — documented, not an error.
- **Path expansion boundary**: `_resolve_vault_dir` owns normalization — it receives the raw `home_dir` string from config and applies `expanduser` itself (single site). The config dict keeps the raw value (e.g. `~/Claude/`) so `config-get` and templates display what the user wrote.
- **Shell access**: new `booping config-get <dotted.key>` subcommand — `bin/booping-create-project` calls the sibling `bin/booping` (resolved via `dirname "$0"`, not PATH) (user-confirmed).
- **First-run seeding (deterministic, no silent fallback)**: `create-project` resolution ladder — (1) `config-get home_dir` succeeds → use it; (2) it fails but `~/Claude` exists → use default, no prompt; (3) it fails and `~/Claude` absent → interactive prompt: confirm default or enter a dir, then **seed the answer into `${XDG_CONFIG_HOME:-~/.config}/booping/config.yaml`** so subsequent runs hit case 1 (user-confirmed).
- **No project required for config-get**: `config-get` merges core + global (+ project when a `.booping` resolves) — must work outside any project so `create-project` can call it pre-attach.
- **Pytest isolation** (code tests only — no evals in this repo): the global-path helper reads `XDG_CONFIG_HOME` at call time; a new `booping-python/tests/conftest.py` carries an `autouse=True` fixture pointing `XDG_CONFIG_HOME` at a tmp dir, so the developer machine's real global config never leaks into unit tests.

## Architecture

- `booping-python/src/booping/context/config.py` — gains `global_config_path()` helper; `load()` unchanged (already takes ordered `override_paths`).
- `booping-python/src/booping/context/__init__.py::Context.assemble` — new order: `Project.load_cwd` parses the marker but defers vault resolution; core+global merge yields `home_dir`; vault resolves; final merge appends `<vault>/config.yaml`. No-project branch loads core+global (today it loads core only).
- `booping-python/src/booping/context/project.py` — `_resolve_vault_dir` takes `home_dir` instead of hardcoding `Path.home() / "Claude"`.
- `booping-python/src/booping/commands/config_get.py` — new subcommand, registered in `cli.py` alongside the existing seven.
- `bin/booping-create-project` — default root from the seeding ladder above.
- Consumers unchanged: `render`, `render-sprints`, `transition`, `vault-commit` all go through `Context.assemble` / `Project` and inherit the new resolution.
- Jinja context: `config.home_dir` is automatically available to runtime templates once the key exists (config dict is passed whole). No template edits in this plan.

## Milestones

### M1: Global config tier + home_dir resolution — 5 SP | done

**Goal**: `~/.config/booping/config.yaml` deep-merges between core and project tiers, and its `home_dir` drives vault resolution end-to-end.

**Verify**: `XDG_CONFIG_HOME=$(mktemp -d) sh -c 'mkdir -p $XDG_CONFIG_HOME/booping && echo "home_dir: /tmp/vaults" > $XDG_CONFIG_HOME/booping/config.yaml && bin/booping debug-context | grep "directory: /tmp/vaults"'` from an attached repo without `vault_path:`; `just test` green.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Global tier: `global_config_path()` helper (`${XDG_CONFIG_HOME:-~/.config}/booping/config.yaml`, env read at call time); `Context.assemble` prepends it to override paths in both branches (with-project and no-project); `home_dir: ~/Claude/` default added to `src/config.yaml`; new `booping-python/tests/conftest.py` with an `autouse=True` fixture setting `XDG_CONFIG_HOME` to a tmp dir (no per-file opt-in) | `booping-python/src/booping/context/config.py`, `booping-python/src/booping/context/__init__.py`, `src/config.yaml`, `booping-python/tests/context/config_test.py`, `booping-python/tests/conftest.py` | 2 | done |
| 1.2 | Resolution reorder: `_resolve_vault_dir` takes raw `home_dir: str` param (replaces `Path.home() / "Claude"`) and applies `expanduser` itself — the single normalization site; config dict keeps the raw value; `Context.assemble` loads core+global → resolves vault → merges project tier; precedence `vault_path:` > `home_dir` preserved | `booping-python/src/booping/context/project.py`, `booping-python/src/booping/context/__init__.py`, `booping-python/tests/context/project_test.py`, `booping-python/tests/context/assemble_test.py` | 3 | done |

#### Task 1.1 DoD

- [x] With `XDG_CONFIG_HOME` pointing at a fixture, a global-config key (e.g. `sprint.default_threshold_sp`) overrides core and is itself overridden by project config — merge order test proves `core → global → project`.
- [x] `agents` blocks shallow-merge across all three tiers (existing `shallow_merge_keys` behavior holds).
- [x] Missing global file is silently skipped (existing `path.exists()` guard covers it).
- [x] No-project branch (`Context.assemble` outside any `.booping`) also merges the global tier.
- [x] `src/config.yaml` carries `home_dir: ~/Claude/`; `bin/booping debug-context` shows it.
- [x] `conftest.py` fixture is `autouse=True` — a deliberately-added canary test reading `global_config_path()` sees the tmp dir without any explicit fixture request.
- [x] All existing tests pass unmodified under the new conftest.

#### Task 1.2 DoD

- [x] Global `home_dir: /tmp/x` + no `vault_path:` → `Project.directory == /tmp/x/<project_name>`.
- [x] `.booping` `vault_path:` set → `home_dir` ignored (precedence test).
- [x] No global config → default `~/Claude/<project_name>` unchanged (regression test).
- [x] `home_dir: ~/somewhere` expands `~` inside `_resolve_vault_dir`; the config dict retains the raw `~/somewhere` string.
- [x] `home_dir` in project-tier config has no effect on vault resolution (test documents the non-behavior).
- [x] `is_local_vault` still correct for both vault kinds.

---

### M2: `config-get` subcommand + create-project seeding — 5 SP | done

**Goal**: shell callers read any resolved config value; `booping-create-project` resolves its root deterministically and seeds the global config on true first run.

**Verify**: `bin/booping config-get home_dir` prints the resolved value, exit 0; `bin/booping config-get no.such.key` → stderr + exit 1; with `XDG_CONFIG_HOME=<empty tmp>` and `HOME=<tmp without Claude/>`, `bin/booping-create-project t </dev/null` prompts (or aborts non-interactively with a clear message) instead of silently scaffolding.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | `booping config-get <dotted.key>`: resolves through the same merged config as `Context.assemble` (core + global + project-when-attached); scalar → raw text on stdout; mapping/list → YAML dump; missing key → stderr message, exit 1; registered in `cli.py` | `booping-python/src/booping/commands/config_get.py`, `booping-python/src/booping/cli.py`, `booping-python/tests/commands/config_get_test.py` | 2 | done |
| 2.2 | `create-project` resolution ladder: `BOOPING="$(dirname "$0")/booping"`; (1) `HOME_DIR="$("$BOOPING" config-get home_dir)"` on success; (2) on failure, if `$HOME/Claude` exists → `HOME_DIR="$HOME/Claude"`; (3) else interactive prompt "Vault home dir [~/Claude]: " → write `home_dir: <answer>` to `${XDG_CONFIG_HOME:-$HOME/.config}/booping/config.yaml` (create dirs; refuse to clobber an existing file) and use it. Non-interactive stdin in case 3 → abort with clear stderr message, exit 1. Expand leading `~` before use. `--local` and absolute-path modes untouched; usage text updated | `bin/booping-create-project` | 2 | done |
| 2.3 | Docs for the feature (not a sweep): `documentation/project_config.md` gains the global-tier section (path with XDG note, merge order core → global → project, `home_dir` semantics + precedence vs `vault_path:`, project-tier no-op, first-run seeding); CLAUDE.md `## CLI` gains `config-get`, config-schema/status lines updated ("one-line change" sentence retired) | `documentation/project_config.md`, `CLAUDE.md` | 1 | done |

#### Task 2.1 DoD

- [x] `config-get home_dir` prints one line, no quoting, trailing newline only.
- [x] `config-get sprint.default_threshold_sp` prints the scalar (dotted-path traversal works).
- [x] `config-get plan.statuses` prints YAML for the mapping.
- [x] Missing key → exit 1, message on stderr, nothing on stdout.
- [x] Works outside any project (core+global only) — no crash on `project is None`.
- [x] `--help` lists the new subcommand.

#### Task 2.2 DoD

- [x] Config present → scaffold lands under its `home_dir`; no prompt.
- [x] No config + `$HOME/Claude` exists → scaffold under `$HOME/Claude`; no prompt.
- [x] No config + no `$HOME/Claude` + interactive tty → prompt shown; answer (or empty = default) seeded into the global config file; scaffold lands under it.
- [x] Seeding never overwrites an existing global config file.
- [x] No config + no `$HOME/Claude` + non-interactive stdin → exit 1 with instructive stderr, nothing scaffolded.
- [x] `bin/booping` resolved via `dirname "$0"`, not PATH.
- [x] `--local` and absolute-path second-arg modes behave exactly as before.

#### Task 2.3 DoD

- [x] `project_config.md` covers: global path, merge order, `home_dir` + precedence, project-tier no-op, first-run seeding.
- [x] CLAUDE.md `## CLI` documents `config-get`; config-schema + status sections reflect the three-tier merge.
- [x] No other docs touched (sweep explicitly out of scope).

---

### M3: Live migration verification — 1 SP | done

**Goal**: user migrates the real vault home and confirms end-to-end resolution; plan does not transition out before this passes.

**Verify**: user-driven checklist below, run on the real machine.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Pause-for-user step: /develop halts and hands over. User writes `~/.config/booping/config.yaml` with `home_dir: ~/Dev/@A/notes/projects/`, moves `~/Claude/*` there, then runs the checklist. Agent assists only on request | — (user's machine state) | 1 | done |

#### Task 3.1 DoD

- [x] `bin/booping config-get home_dir` prints `~/Dev/@A/notes/projects/` (raw, per expansion-boundary decision).
- [x] `bin/booping debug-context` from this repo resolves `directory:` under the new home.
- [x] `bin/booping render src/templates/skills/chat.md.j2` renders with correct vault paths.
- [x] `bin/booping render-sprints` writes to the new vault location.
- [x] A repo with `.booping` `vault_path:` (local vault) still resolves locally — precedence intact.
- [x] User explicitly confirms migration success.

---

## I/O contract

`booping config-get <dotted.key>`

- **Arguments**: exactly one positional — dot-separated key path into the merged config (e.g. `home_dir`, `sprint.default_threshold_sp`, `plan.statuses`).
- **stdin**: unused.
- **stdout**: scalar values → raw text, single line, no quotes; mappings/lists → YAML dump. Nothing on failure.
- **stderr**: `error: key not found: <key>` on missing key; loader diagnostics on malformed config.
- **Exit codes**: `0` = value printed; `1` = key not found / user error; `2` = internal error (unreadable config).

`bin/booping-create-project`

- Default-mode root resolution: deterministic ladder (config → existing `~/Claude` → interactive seed). Prompt: `Vault home dir [~/Claude]: `; empty answer accepts default; answer seeded to the global config.
- Non-interactive + unresolvable → exit 1, stderr explains how to set `home_dir`.
- Flags, marker format, `--local`, absolute-path mode: unchanged.

## Final Verification

- [x] `just lint`, `just typecheck`, `just test` green.
- [x] `bin/booping --help` lists `config-get`; its help text accurate.
- [x] Happy path: global-config fixture drives `debug-context` vault resolution (M1 Verify).
- [x] Failure path: `config-get no.such.key` → exit 1 + stderr.
- [x] First-run seeding path exercised (M2 Verify).
- [x] M3 user checklist passed and explicitly confirmed.

## Out of scope

- No vault content migration — user moves directories manually (M3).
- No prose sweep of templates / docs / README for literal `~/Claude` mentions — default is unchanged, so existing mentions remain true. Only the two files in task 2.3 are touched.
- No `home_dir`-driven change to `bin/booping-external-llm-call` (doesn't touch the vault).
- No new config keys beyond `home_dir`; no restructuring of existing config schema.
- No per-project `home_dir` semantics (explicit no-op).

## CLAUDE.md impact

- `## CLI` — add `config-get` entry (task 2.3).
- Config-schema + status sections — three-tier merge order, `home_dir` key, precedence vs `vault_path:`; retire the "one-line change" sentence (task 2.3).
