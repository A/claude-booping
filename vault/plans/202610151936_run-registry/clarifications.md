# Clarifications

## C1 — command shape — answered

**Asked:** 2026-10-15 — groom/intake

**Question:** The request names `booping run groom|develop <plan> --autonomous`, but a groom run starts from a request, not a plan. What does each verb take, and how is a finished run marked seen?

**Options:**
- one positional plan for both verbs
- groom takes open item ids or a parked plan, develop takes a plan
- groom takes free text

**Answer:** Default (autonomous run): `booping run groom TARGET... [--autonomous]` — TARGET is one or more open item ids (`OI-NNNN`, adr/0028: every request is an item first) or exactly one plan path (`index.md` or its directory) to resume a parked groom run. `booping run develop PLAN [--autonomous]` — one plan path. `booping run ack ID...` marks finished, failed or lost runs seen. Free text is not accepted: a request is filed with `booping items add` first, so the run always has its item.

## C2 — foreground or detached — answered

**Asked:** 2026-10-15 — groom/intake

**Question:** Does `booping run` detach `claude -p` and return at once, or wait for it?

**Answer:** Default (autonomous run): it waits. It prints the record path as soon as the run is launched, waits for `claude -p`, writes the outcome and exits with the child's exit code. The caller backgrounds it — the Bash tool's background mode notifies the manager session on exit, a timer unit waits on it. No daemon, no detached child, no polling loop in booping (value/0015, the simplest mechanism that works); the fallback check (C4) covers a wrapper that dies.

## C3 — where the registry lives — answered

**Asked:** 2026-10-15 — groom/intake

**Question:** What is the registry, physically?

**Answer:** Default (autonomous run): one record per run, `{vault}/runs/{id}.md`, plain markdown with YAML frontmatter (rule/0028, value/0011), the prompt as its body; the run's combined stdout and stderr in `{vault}/runs/{id}.log` beside it. `booping run` writes `runs/.gitignore` with `*.log` when it creates the directory — records are history worth keeping (value/0004), stream-json logs are large. The directory name is config (`core.run.dir`), like `core.specs.open_items.dir`. `runs/` is not a record type, so `specs check` ignores it (adr/0001).

## C4 — record lifecycle and the fallback check — answered

**Asked:** 2026-10-15 — groom/intake

**Question:** Who writes a record's status, and how is a run that died without writing its outcome noticed?

**Answer:** Default (autonomous run): only `booping run` writes a record. At launch: `status: running` with the child's `pid`. At exit: `finished` (exit 0) or `failed` (non-zero, or a signal → 128+n), `exit_code`, `ended_at`, and `pid` cleared. SIGINT/SIGTERM to the wrapper is forwarded to the child's process group, then the outcome is written. `lost` is never stored by the run: a record still `running` whose pid is not alive is reported `lost` at read time — that is the fallback check. `booping run ack` writes `acked_at` (and stores `lost` for a lost run). No state machine: the record is a CLI-owned log like the corrections and defaults sidecars, not a playbook's run state.

## C5 — launch shape in config — answered

**Asked:** 2026-10-15 — groom/intake

**Question:** Where do the claude argv, env, prompt and autonomy preamble live?

**Answer:** Default (autonomous run): `core.run`, directly under `core` because the CLI and the project-manager (part 4) share it. `command` — argv list, default `[claude, -p, --permission-mode, auto, --output-format, stream-json, --verbose]`; `env` — mapping added to the inherited environment, default `{CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS: "0"}`; `prompt` — `/booping:playbook {playbook} {target}`; `preamble` — the autonomy text appended after a blank line under `--autonomous`; `dir` — `runs`. The launcher appends `--session-id {uuid}` and the prompt as the last two argv items, runs in the repo directory with stdin from `/dev/null`. No value is env-interpolated. A test overrides `command` in a vault config with a fake script — the injection seam, no mock.

## C6 — ids — answered

**Asked:** 2026-10-15 — groom/intake

**Question:** How are the run id and the session id made, and kept reproducible in tests?

**Answer:** Default (autonomous run): run id `{YYYYMMDD-HHMMSS}-{playbook}` from `core.macros.date` (stubbable), with `-2`, `-3` … appended on a clash; session id `uuid5(NAMESPACE_URL, "booping-run:{run id}")`, passed as `--session-id` and stored on the record, so the session's transcript is findable from the record.

## C7 — which items a run records — answered

**Asked:** 2026-10-15 — groom/intake

**Question:** "Every launched run recorded with its item" — which items?

**Answer:** Default (autonomous run): groom with item ids — those ids, each checked to exist; groom or develop with a plan — the items `open_items.planned_for` returns for that plan (possibly none, recorded as `[]`). The plan link stays only on the item (CLAUDE.md, open-items track); the record lists item ids, and its `plan` is the plan path when one was given.

## C8 — status section — answered

**Asked:** 2026-10-15 — groom/intake

**Question:** Where does `runs` sit in `booping status`, and what does it count?

**Answer:** Default (autonomous run): after `plans`, in the request's order (items, ideas, plans, runs, records, marks) — the short report grows to six lines. It counts records not yet acked: running, finished, failed, lost. Acked records are history and are not shown.

## C9 — output content — answered

**Asked:** 2026-10-15 — groom/intake

**Question:** Rule/0010 asks for the exact output content now.

**Answer:** Default (autonomous run): locked in `index.md`'s I/O contract — the record's frontmatter keys and order, the two stdout lines of `booping run`, the `ack` output, the status summary line and detail table.

## C10 — scope boundary — answered

**Asked:** 2026-10-15 — groom/intake

**Question:** What of the project-manager request lands here?

**Answer:** Default (autonomous run): the `booping run` command, its record and log, `core.run`, the status `runs` section, e2e cases and docs entries. Out: budget and window gates, batching, a timer unit, pause/resume and `--resume` of a session (part 4, the project-manager's autonomous mode); the project-manager playbook itself (part 4); project-manager docs and setup linking (part 5). No playbook source changes, so no snapshot drift.
