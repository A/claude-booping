---
title: Log project-facing `booping` CLI invocations to `.booping.log`
type: feature
status: done
sp: 4
split_from: null
created: 2026-05-20 00:00
planned: 2026-05-20 10:00
started: 20260520 12:00
commit: 1d22c7a8d188db131ab486079c6f3b6cb71049c1
completed: 2026-06-10 12:14
retro: retrospectives/20260610-cli-logging-and-agent-namespacing.md
goal: success
summary: "Shared log_invocation helper logs render, render-sprints and run-agent calls to vault _booping/.booping.log"
---

# Log project-facing `booping` CLI invocations to `.booping.log`

## Context

**Current state.** Only `booping run-agent` writes to `<vault>/_booping/.booping.log`. `log_invocation` lives at `booping-python/src/booping/commands/run_agent.py:118-131` and emits `<iso8601-utc>: [run-agent] <id>: \`<command-template>\``. The other project-facing subcommands (`render`, `render-sprints`) run silently — skill-load template renders and sprint refreshes leave no trace.

**Motivation.** User wants one auditable file per project listing every `booping` call that touched the vault. Raw argv is noisy and sometimes meaningless (e.g. `run-agent` argv contains briefing file paths, not the actual command template the CLI dispatched). Logging needs a **semantic per-subcommand line**, not a generic argv dump.

**Scope.**
- IN: `render`, `render-sprints`, `run-agent` — the three subcommands that act against the project vault.
- IN: shared logger module; semantic per-command detail strings (template path, resolved output, agent id + command template).
- IN: no double-write when `run-agent` swaps to the shared helper. `run-agent` writes **two** lines per call (invocation pre-exec + completion post-exec, introduced in `6a450cb`); `render` / `render-sprints` write **one** line each.
- OUT: `build`, `debug-context`, `debug-template` — developer tools; do not touch the vault meaningfully and are not invoked by skills against a project.
- OUT: `bin/booping-create-project`, `bin/booping-external-llm-call` — standalone `uv` inline scripts, not subcommands of the `booping` CLI.
- OUT: log rotation, size cap, JSON format. Append-only plain text.

## Decisions

- **Per-command logging, shared helper** — each project-facing subcommand calls `logging.log_invocation(vault, subcommand, detail)` with a subcommand-specific `detail` string. Justification: raw argv hides semantic content (`run-agent`'s rendered command template, `render-sprints`'s resolved default output path) and leaks irrelevant content (briefing file paths). The helper itself is one source of truth (lesson 0004); per-command call sites are unavoidable because the *detail* differs.
- **Resolve project via `Project.load_cwd()` standalone, not `Context.assemble()`** — `render-sprints` and `run-agent` already assemble Context; reuse `ctx.project`. `render` also assembles Context. So `ctx.project` is free at every logging call site. Justification: no second filesystem walk.
- **Silent no-op when no project resolves** — matches current `run-agent` behavior.
- **Preserve `run-agent` line formats verbatim** — invocation line `<iso8601-utc>: [run-agent] <id>: \`<command-template>\`` and completion line `<iso8601-utc>: [run-agent] <id>: exit=<code> elapsed=<s>s stdout[0:100]=<repr> stderr=<repr>` (added in `6a450cb`). Both migrate to the shared helper by passing the relevant `detail` string; output shape unchanged. Existing tests keep passing.
- **Skip `build` / `debug-*`** — `build` writes to the plugin repo, not the vault; `debug-*` is read-only inspection. Neither belongs in the project audit trail. Justification: keep the log focused on calls that affect or read the vault.
- **Log before the work runs, not after** — a failed render is more interesting to audit than a successful one. `build`'s "N files written" doesn't apply here since `build` is out-of-scope.

## Architecture

```
booping render <path> [--output O]
  ──▶ render._run()
       ctx = Context.assemble()
       detail = "<path>"   (or "<path> → <O>" when --output set)
       logging.log_invocation(ctx.project.directory, "render", detail)
       ... do render ...

booping render-sprints [--output O]
  ──▶ render_sprints._run()
       ctx = Context.assemble()    # already required for plans
       resolved = "-" if --output - else (O if --output else <vault>/sprints.md)
       detail = f"→ {resolved}"
       logging.log_invocation(ctx.project.directory, "render-sprints", detail)
       ... do render ...

booping run-agent <id>
  ──▶ run_agent.run_with_context()
       ... resolve agent, validate ...
       detail = f"{agent_id}: `{command_template}`"
       logging.log_invocation(vault_dir, "run-agent", detail)
       ... exec ...
```

Integration points:
- `booping-python/src/booping/logging.py` *(new)* — shared `log_invocation(vault, subcommand, detail)`.
- `booping-python/src/booping/commands/render.py` — add one call.
- `booping-python/src/booping/commands/render_sprints.py` — add one call.
- `booping-python/src/booping/commands/run_agent.py` — delete local `log_invocation` and `log_completion`; switch both call sites to the shared helper with the same output formats (invocation + completion details preserved).
- `booping-python/tests/test_logging.py` *(new)* — unit tests for the shared helper.
- `booping-python/tests/commands/run_agent_test.py` — existing log tests stay (merged invocation+completion test + two `log_invocation` helper tests); update imports/signatures only, keep both format regexes (invocation + completion).
- `CLAUDE.md` — one-line bullet under "Project vault layout" for `_booping/.booping.log`.

## Milestones

### M1: Shared logger + wire into `render` and `render-sprints` — 2 SP | done

**Goal**: invoking `booping render <template>` or `booping render-sprints` under a project appends one semantic line to `<vault>/_booping/.booping.log`.

**Verify**:
```bash
cd /home/anton/Dev/@A/claude-booping
rm -f /home/anton/Claude/claude-booping/_booping/.booping.log
booping render src/templates/skills/chat.md.j2 > /dev/null
booping render-sprints
tail -2 /home/anton/Claude/claude-booping/_booping/.booping.log
# Expect:
# <ts>: [render] src/templates/skills/chat.md.j2
# <ts>: [render-sprints] → /home/anton/Claude/claude-booping/sprints.md
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Create `booping/logging.py` with `log_invocation(vault: Path \| None, subcommand: str, detail: str) -> None`. No-op when `vault is None`. Append `<iso8601-utc>: [<subcommand>] <detail>\n` (or `<iso8601-utc>: [<subcommand>]\n` when `detail == ""`). Create `<vault>/_booping/` if missing. | `booping-python/src/booping/logging.py` | 0.5 | done |
| 1.2 | Hook `render._run()`: compute `detail = str(template_path_relative_or_absolute)` plus ` → {output}` when `args.output is not None`. Call `logging.log_invocation(ctx.project.directory if ctx.project else None, "render", detail)` after `Context.assemble()`, before rendering. Use the **original** argument as displayed (relative if user passed relative), not the resolved absolute path — keeps the log readable. | `booping-python/src/booping/commands/render.py` | 0.5 | done |
| 1.3 | Hook `render_sprints._run()`: compute `resolved` per existing branch logic (`"-"` for stdout, `args.output` when set, else `<vault>/sprints.md`). `detail = f"→ {resolved}"`. Call the helper after `Context.assemble()`, before rendering. | `booping-python/src/booping/commands/render_sprints.py` | 0.5 | done |
| 1.4 | Unit tests for `log_invocation`: (a) `vault=None` is a no-op (no file created); (b) appends one line with documented format; (c) multiple calls append, never overwrite; (d) empty `detail` produces line without trailing space; (e) `_booping/` parent dir is auto-created. | `booping-python/tests/test_logging.py` *(new)* | 0.5 | done |

#### Task 1.1 DoD

- [x] `booping/logging.py` exports `log_invocation` with `(vault: Path | None, subcommand: str, detail: str) -> None`.
- [x] No-op path verified by test (file does not appear in tmp_path).
- [x] UTC iso8601 stamp `YYYY-MM-DDTHH:MM:SSZ`.
- [x] `just typecheck` clean on the new module.

#### Task 1.2 DoD

- [x] `booping render <path>` from inside the project appends one `[render] <path>` line.
- [x] `booping render <path> --output /tmp/x.md` appends `[render] <path> → /tmp/x.md`.
- [x] `booping render <path>` from outside any `.booping` project does **not** create a log file (verified manually under `/tmp`).
- [x] Logger call happens before `render()` — confirmed by reading the diff.

#### Task 1.3 DoD

- [x] `booping render-sprints` appends `[render-sprints] → /home/anton/Claude/claude-booping/sprints.md`.
- [x] `booping render-sprints --output -` appends `[render-sprints] → -`.
- [x] `booping render-sprints --output /tmp/s.md` appends `[render-sprints] → /tmp/s.md`.
- [x] The existing error path (`ctx.project is None`) still prints to stderr and exits 2; no log line is written.

#### Task 1.4 DoD

- [x] Five test cases pass.
- [x] Tests use `tmp_path`; no test touches the real vault log.
- [x] `just test` passes — no regressions.

#### Task 1.1 Code sketch

```python
# booping-python/src/booping/logging.py
from datetime import UTC, datetime
from pathlib import Path


def log_invocation(vault: Path | None, subcommand: str, detail: str) -> None:
    if vault is None:
        return
    log_dir = vault / "_booping"
    log_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"{ts}: [{subcommand}] {detail}\n" if detail else f"{ts}: [{subcommand}]\n"
    with (log_dir / ".booping.log").open("a", encoding="utf-8") as f:
        ...  # write line
```

#### Task 1.2 Code sketch

```python
# booping-python/src/booping/commands/render.py
def _run(args: argparse.Namespace) -> None:
    ctx = Context.assemble()
    template_path: Path = args.path
    detail = str(args.path)  # user's original argument, pre-resolution
    if args.output is not None:
        detail = f"{detail} → {args.output}"
    vault = ctx.project.directory if ctx.project is not None else None
    booping_logging.log_invocation(vault, "render", detail)
    if not template_path.is_absolute():
        template_path = get_plugin_root() / template_path
    ...  # existing render
```

#### Task 1.3 Code sketch

```python
# booping-python/src/booping/commands/render_sprints.py
def _run(args: argparse.Namespace) -> None:
    ctx = Context.assemble()
    if ctx.project is None:
        print("error: no project resolved …", file=sys.stderr)
        sys.exit(2)

    output_str: str | None = args.output
    if output_str == "-":
        resolved = "-"
    elif output_str is not None:
        resolved = output_str
    else:
        resolved = str(ctx.project.directory / "sprints.md")
    booping_logging.log_invocation(ctx.project.directory, "render-sprints", f"→ {resolved}")

    ...  # existing render + write
```

---

### M2: Migrate `run-agent` to shared helper + docs — 2.25 SP | done

**Goal**: `run-agent` writes both its invocation and completion lines via the shared helper (same formats as today — 2 lines per call), the legacy `log_invocation` + `log_completion` in `run_agent.py` are deleted, and CLAUDE.md mentions the log file.

**Verify**:
```bash
cd /home/anton/Dev/@A/claude-booping
rm -f /home/anton/Claude/claude-booping/_booping/.booping.log
echo "BRIEFING" | booping run-agent <a-cli-agent-id> 2>/dev/null || true
wc -l /home/anton/Claude/claude-booping/_booping/.booping.log
# Expect: exactly 2 lines — 1 invocation `[run-agent] <id>: `<cmd-template>``, 1 completion `[run-agent] <id>: exit=<n> elapsed=<s>s stdout[0:100]=<repr> stderr=<repr>`
grep -nE "def (log_invocation|log_completion)" booping-python/src/booping/commands/run_agent.py  # expect no match
grep -n "from booping import logging" booping-python/src/booping/commands/run_agent.py  # expect 1 match
```

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Delete `log_invocation` **and** `log_completion` from `run_agent.py`. Replace the pre-exec call site with `logging.log_invocation(vault_dir, "run-agent", f"{agent_id}: \`{command_template}\`")`. Replace the post-exec call site with `logging.log_invocation(vault_dir, "run-agent", f"{agent_id}: exit={child.returncode} elapsed={elapsed:.2f}s stdout[0:100]={out_snip} stderr={err_full}")` (compute `out_snip = repr(child.stdout[:100])` and `err_full = repr(child.stderr)` inline at the call site, preserving today's format exactly). Adjust imports (drop `from datetime import UTC, datetime` if unused; add `from booping import logging as booping_logging`). Keep `_porcelain_pairs`, `_git_porcelain_code`, `OUTPUT_GUIDE`, and the trailer-emission logic untouched. | `booping-python/src/booping/commands/run_agent.py` | 0.75 | done |
| 2.2 | Update existing log tests in `run_agent_test.py`: switch `ra.log_invocation` → `booping_logging.log_invocation` in the two helper tests; rewrite their call signature from `(vault, id, command)` → `(vault, "run-agent", f"{id}: \`{command}\`")` and update the `"second: \`cmd2\`"` substring assertion to match the new detail shape. Keep `test_log_invocation_appends_line_to_booping_log` asserting `len(lines) == 2` with both `invocation_pattern` and `completion_pattern` regexes — output shape is unchanged. Leave `test_changed_files_trailer_*` tests untouched. | `booping-python/tests/commands/run_agent_test.py` | 0.5 | done |
| 2.3 | Add a subprocess integration test under `tests/test_logging.py`: scaffold a tmp project (`tmp_path/repo/.booping` marker + `tmp_path/Claude/<name>/_booping/`), invoke `bin/booping render src/templates/skills/chat.md.j2` via `subprocess.run` from inside the repo, monkey-patch `HOME` so `Project.load_cwd()` resolves to the tmp Claude tree, and assert the log contains exactly one `[render]` line. | `booping-python/tests/test_logging.py` | 0.5 | done |
| 2.4 | CLAUDE.md: under "Project vault layout (`~/Claude/{project}/`)", add a bullet for `_booping/.booping.log` — one line, naming the format and the three subcommands that write it (`render`, `render-sprints`, `run-agent`). | `/home/anton/Dev/@A/claude-booping/CLAUDE.md` | 0.5 | done |

#### Task 2.1 DoD

- [x] `grep -nE "def (log_invocation|log_completion)" booping-python/src/booping/commands/run_agent.py` shows no match.
- [x] Both call sites in `run_with_context` use `booping_logging.log_invocation(...)`.
- [x] `from datetime import UTC, datetime` removed when no other use remains (ruff F401 flags unused imports — confirm via `just lint`).
- [x] `just lint` and `just typecheck` clean.
- [x] Top-of-file docstring still accurate; no stale claims about local logging.

#### Task 2.2 DoD

- [x] Existing log tests still pass under the new import and call signatures.
- [x] No new test in `run_agent_test.py` — all new logging tests live in `tests/test_logging.py`.
- [x] Invocation regex `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z: \[run-agent\] test-cli: \`printf %s\`$` still matches line 0.
- [x] Completion regex `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z: \[run-agent\] test-cli: exit=0 elapsed=\d+\.\d{2}s stdout\[0:100\]=.+ stderr=.+$` still matches line 1.

#### Task 2.3 DoD

- [x] Integration test invokes `bin/booping` via `subprocess.run` (not the in-process `cli.main`).
- [x] Assertion: log file has exactly 1 line, matches `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z: \[render\] .+$`.
- [x] Test is hermetic — uses `tmp_path`, never writes to the real `/home/anton/Claude/`.

#### Task 2.4 DoD

- [x] CLAUDE.md "Project vault layout" lists `_booping/.booping.log — append-only invocation log. `render` / `render-sprints` write one line per call; `run-agent` writes two (invocation pre-exec + completion post-exec). Format: `<iso8601-utc>: [<subcommand>] <detail>`.`
- [x] No other CLAUDE.md edits in the diff.

---

## I/O contract

**Logger function** (`booping/logging.py`):
- **Args**: `vault: Path | None`, `subcommand: str`, `detail: str`.
- **Side effect**: creates `<vault>/_booping/` if missing; appends one line to `<vault>/_booping/.booping.log`.
- **Returns**: `None`. No raises under normal filesystem conditions.

**Log line format**:
```
2026-05-20T10:42:01Z: [render] src/templates/skills/groom.md.j2
2026-05-20T10:42:02Z: [render] src/templates/sprints.md.j2 → /tmp/out.md
2026-05-20T10:42:05Z: [render-sprints] → /home/anton/Claude/claude-booping/sprints.md
2026-05-20T10:42:07Z: [render-sprints] → -
2026-05-20T10:42:12Z: [run-agent] test-cli: `printf %s`
2026-05-20T10:42:14Z: [run-agent] test-cli: exit=0 elapsed=1.42s stdout[0:100]='hello\n' stderr=''
```
- Timestamp: ISO 8601 UTC with `Z` suffix, second precision.
- Subcommand: one of `render`, `render-sprints`, `run-agent`.
- Detail: subcommand-specific string per the table above.
- `run-agent` emits two consecutive lines per call (invocation + completion); `render` / `render-sprints` emit one.

**Exit codes**: unchanged. Logger never alters subcommand exit code.

**Excluded subcommands** (no log line emitted): `build`, `debug-context`, `debug-template`.

## Final Verification

- [x] `just test` passes.
- [x] `just lint` clean.
- [x] `just typecheck` clean.
- [x] `booping render src/templates/skills/chat.md.j2 > /dev/null` from this repo appends one `[render]` line.
- [x] `booping render-sprints` appends one `[render-sprints] → <path>` line.
- [x] `echo BRIEFING | booping run-agent <id>` (real cli agent) appends exactly two `[run-agent]` lines: invocation (`<id>: \`<cmd>\``) + completion (`<id>: exit=... elapsed=...s stdout[0:100]=... stderr=...`). No third line, no duplicate of either.
- [x] `booping build`, `booping debug-context` produce **no** log lines (confirmed by line count before/after).
- [x] Running any subcommand from a directory without a `.booping` ancestor produces no log file and no stderr noise.
- [x] `git grep -n "log_invocation"` matches only `booping-python/src/booping/logging.py`, the three call sites in `commands/*.py`, and the test files.

## Out of scope

- `build`, `debug-context`, `debug-template` — developer tools; not project-facing.
- `bin/booping-create-project`, `bin/booping-external-llm-call` — standalone `uv` scripts, not subcommands.
- Log rotation, size cap, pruning.
- Structured (JSON) format.
- Wall-clock duration or exit-code capture.

## CLAUDE.md impact

| Section | Change | Owning task |
|---------|--------|-------------|
| `## Project vault layout (~/Claude/{project}/)` | New bullet for `_booping/.booping.log` — format + list of writing subcommands. | M2.4 |
