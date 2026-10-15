---
id: "04"
title: "CLAUDE.md and documentation on booping run and core.run"
sp: 2
status: pending
plan: "plans/202610151936_run-registry/index.md"
---

# M04: CLAUDE.md and documentation on booping run and core.run

The plugin's own guide and the public docs name `booping run`, `core.run`, the `runs/` vault directory and the `runs` status section.

**Scope**: `CLAUDE.md` — `## Commands`: add `run` (`groom`, `develop`, `ack`) to the `bin/booping` subcommand list; `## Config`: a `core.run` bullet (launch shape for `booping run` — `command`, `env`, `prompt`, `preamble`, `dir` — shared key, no value env-interpolated); `## Vault`: add `runs/` (run records plus gitignored logs, written only by `booping run`) to the directory list; `## Lifecycle`: one bullet on run records (`running` → `finished` | `failed` written by `booping run`, `lost` computed, `ack` marks seen). `documentation/project_config.md` — a `core.run` entry beside `core.status`. `documentation/quick_start.md` — one example `bin/booping run develop plans/{slug}/index.md --autonomous &` with one sentence on what it records. `documentation/vault.md` — `runs/` in the vault layout. Audience filter (rule/0008): the public pages say only what a user runs, configures and finds in the vault — no module names, no test details.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | CLAUDE.md commands, config, vault and lifecycle entries. | `CLAUDE.md` | 1 | pending |
| 4.2 | Public docs entries. | `documentation/project_config.md`, `documentation/quick_start.md`, `documentation/vault.md` | 1 | pending |

## Definition of Done

### Task 4.1

- [ ] `CLAUDE.md` names `run` in the subcommand list and `core.run` under Config, and `runs/` in the Vault section.

### Task 4.2

- [ ] Each of the three pages carries its entry; none names a Python module, a test or an internal helper.
- [ ] `just docs` builds without a new warning.

Return: the list of changed files, nothing else.

## References

- Commit `368dfd2` — the same four-place docs change for `booping status`.

## Verify

`just docs`
