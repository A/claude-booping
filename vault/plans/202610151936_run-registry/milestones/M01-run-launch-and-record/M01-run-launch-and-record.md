---
id: "01"
title: "booping run groom|develop launches and records a run"
sp: 4
status: pending
plan: "plans/202610151936_run-registry/index.md"
---

# M01: booping run groom|develop launches and records a run

`booping run develop PLAN` and `booping run groom TARGET...` launch the configured `claude -p` command in the repo directory with stdin from `/dev/null`, write a run record at `{vault}/runs/{id}.md` before the child starts and its outcome when it ends, stream the child's output to `{vault}/runs/{id}.log`, and exit with the child's code.

**Scope**: add `core.run` to `src/config.yaml`, directly under `core` beside `core.status`, commented like its neighbours: `dir: runs`; `command: [claude, -p, --permission-mode, auto, --output-format, stream-json, --verbose]`; `env: {CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS: "0"}`; `prompt: "/booping:playbook {playbook} {target}"`; `preamble:` the autonomy text locked in `index.md`'s I/O contract, verbatim. Create `booping-python/src/booping/runs.py` — every record read and write, nothing printed: run-id allocation (`{date}-{playbook}` from `macro('core.macros.date', '+%Y%m%d-%H%M%S')` rendered the way `booping/defaults.py` renders its date, `-2`, `-3` … appended while `runs/{id}.md` exists), `session_id` = `str(uuid.uuid5(uuid.NAMESPACE_URL, f"booping-run:{id}"))`, `create(...)` writing the record with the frontmatter keys in the contract's order and the prompt as the body, `finish(...)` setting `status`, `exit_code`, `ended_at`, `pid: null`, and creation of `runs/.gitignore` (one line `*.log`) together with the directory. Create `booping-python/src/booping/commands/run.py`: `add_parser(sub)` builds `run` with sub-verbs `groom` and `develop` (M02 adds `ack`), each with `--autonomous`; target validation, item resolution and launch as the contract states; the child is started with `subprocess.Popen(argv, cwd=repo, env=os.environ | core.run.env, stdin=DEVNULL, stdout=log, stderr=STDOUT, start_new_session=True)` where `argv = core.run.command + ["--session-id", session_id, prompt]`; the record path is printed and flushed right after `create`, the outcome line after `finish`. Target resolution: a `PLAN` that is a directory resolves to its `index.md`; the resolved file must exist inside the vault (else `error: plan not found: {path}`) and is turned vault-relative with `open_items.vault_path` — the form stored on the record and passed to `planned_for` — while the prompt gets its absolute path. An item id resolves with `open_items.item_path(ctx, id)`; the file must exist (else `error: unknown item {id}`), and its `.resolve()`d path goes into the prompt. Items: the given ids for groom, otherwise `open_items.planned_for(ctx, plan)`. A failure to create `runs/`, the record or the log (`OSError`) → `error: cannot write run record: {reason}`, exit 1, no child launched. Errors through `_fail` from `commands/specs.py`. Log once per run: `logger.log(vault=ctx.vault, subcommand="run", message=f"{playbook} {id} {status}")`. Register in `booping-python/src/booping/cli.py` beside `status_cmd`.

Tests (integration tier, e2e corpus `booping-python/e2e/cases/run/`, expectations hand-derived; the vault config overrides `core.run.command` with a `sh -c` script that prints its argv, `$CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS` and whether stdin is empty, then exits with a fixed code — the injection seam, no mock; `core.macros.date` stubbed): develop over a plan directory (not its `index.md`) with one planned item → record `finished`, log holds the session id, the absolute plan path in the prompt and env `0`; `--autonomous` → the preamble after a blank line in the prompt and on the record body, `mode: autonomous`; groom with two item ids → `items` lists both, prompt names both with their paths; fake exit 3 → `failed`, `exit_code: 3`, exit 3; a second run in the same stubbed second gets `-2`; unknown item, missing plan, develop with two targets, groom mixing an item and a plan, no project, `runs` existing as a file → exit 1 with the contract's message and no record; a command that does not exist → record `failed`, `exit_code: 127`, exit 127.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | `core.run` config block with comments and the locked preamble. | `src/config.yaml` | 1 | pending |
| 1.2 | `runs.py` record module; `commands/run.py` groom/develop launch; registration. | `booping-python/src/booping/runs.py`, `booping-python/src/booping/commands/run.py`, `booping-python/src/booping/cli.py` | 2 | pending |
| 1.3 | e2e cases for launch, outcome, ids and every user error above. | `booping-python/e2e/cases/run/*.txtar` | 1 | pending |

## Definition of Done

### Task 1.1

- [ ] `bin/booping config-get core.run` prints the five keys with the defaults above; the preamble equals the contract's text.

### Task 1.2

- [ ] `bin/booping run --help` lists `groom` and `develop`; `bin/booping run develop --help` shows `PLAN` and `--autonomous`.
- [ ] A record's frontmatter keys and order equal the I/O contract; a finished record has `pid: null`.
- [ ] `runs.py` holds no status literal outside one tuple of the four statuses, and no argv, env or prompt literal — those come from `core.run`.

### Task 1.3

- [ ] `booping-python/e2e/cases/run/` holds the cases above, all passing.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/src/booping/commands/items.py` — command module shape, sub-verbs, `_fail`, logging; `booping-python/src/booping/defaults.py` — the date macro render and a sidecar writer.
- `booping-python/e2e/cases/items/add-request-with-a-title-and-argv-text.txtar` — case shape, macro stub, expected vault files.
- `booping-python/e2e/README.md` — the case format.

## Verify

`cd booping-python && uv run pytest e2e/cases/run -q`
