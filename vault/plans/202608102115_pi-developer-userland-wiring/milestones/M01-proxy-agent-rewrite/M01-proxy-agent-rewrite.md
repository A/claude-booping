---
id: "01"
title: "Rewrite the pi-developer proxy agent"
sp: 3
status: done
plan: "vault/plans/202608102115_pi-developer-userland-wiring/index.md"
---

# M01: Rewrite the pi-developer proxy agent

**Goal**: `~/.claude/agents/pi-developer.md` becomes a compact proxy that drives `~/.bin/pi-developer` — composes the pi worker's prompt from the rendered booping developer body plus the briefing's paths, runs the pinned invocation, validates, retries once, reports in milestone format.

**Scope**: only `~/.claude/agents/pi-developer.md` (full rewrite, replacing the retired `pi-agent --provider ollama-cloud` body). The script `~/.bin/pi-developer` and all claude-booping repo files are read-only reference. This file lives **outside any git repository** — the report's commit line is `Commit: none (file outside repository)`, and no repo commit is expected for this milestone.

**Tests**: none automatable at this surface — verification is the two command receipts in `## Verify` (render output non-empty, script round-trip answers).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Rewrite the agent: frontmatter (`name: pi-developer`, description per the plan's `good_for` wording — "use for all development tasks instead of booping-developer", `tools: Read, Bash`, `model: haiku`, `effort: low` — the proxy only shells out and validates) and a compact body: (1) the briefing **is the agent's task prompt** — develop-loop's standard path-based briefing block (`## Task` / `## Inputs` / `## Return` with workdir and instance), no other channel; the body states this explicitly; (2) render the worker body `cd /home/anton/Dev/@A/claude-booping && bin/booping render src/templates/agents/booping-developer.md.j2 > "$(mktemp)"` — the template takes no per-milestone variables, only project context; it renders clean from the repo root (verified); (3) append the briefing's `## Inputs` block with absolute paths and the run-time context (workdir, instance) to that prompt file; (4) run `~/.bin/pi-developer -f {prompt-file} -m Qwen3-Coder-Next -C {workdir}` capturing stdout; (5) validate — **shortfall** is defined as any of: a file the contract's DoD names absent from `git status --porcelain`/`git log -1 --stat`; a changed file outside the contract's Files set; stdout not claiming completion, or flagging an error, refusal, or red Verify; no commit where the contract expects one; (6) on shortfall, write one corrective follow-up naming the failed check(s) to a fresh file and re-run once with `-f {file2} -m Qwen3-Coder-Next -C {workdir} --continue` (continues the same pi session, prior edits preserved) — never a second retry; (7) report in the exact milestone format the rendered developer body defines. Script/network/timeout failure (box unreachable, model unavailable, non-zero script exit): no retry — report the failure honestly in the milestone format. Hard rules carried over: invocation pinned, never edit code itself, call out files touched outside the contract's set. | `~/.claude/agents/pi-developer.md` | 3 | done |

## Definition of Done

### Task 1.1

- [x] Frontmatter: `tools: Read, Bash` only; description states it replaces booping-developer for all development tasks.
- [x] The body pins exactly one invocation shape — `~/.bin/pi-developer -f {file} -m Qwen3-Coder-Next -C {workdir}` — and forbids changing provider, model, endpoint or env.
- [x] The worker prompt is composed as rendered-developer-body + briefing paths block; no worker instruction text is hand-restated in the proxy body.
- [x] Validation defines shortfall as the explicit check list from task 1.1 (missing DoD file, out-of-contract file, stdout error/refusal/red-Verify, missing expected commit) — the same things the runner will check.
- [x] Retry is bounded to exactly one `--continue` re-run; infrastructure failures (unreachable box, non-zero script exit) skip retry and are reported as failure.
- [x] The report format is the rendered developer body's per-milestone block, stated by reference, not re-invented.
- [x] No angle-bracket placeholders anywhere in the file (`{name}` style only).

## Verify

- `cd /home/anton/Dev/@A/claude-booping && bin/booping render src/templates/agents/booping-developer.md.j2 | head -5` — renders non-empty (the command the agent body pins works from a clean shell).
- `printf 'Reply with exactly: OK' | ~/.bin/pi-developer -f - -m Qwen3-Coder-Next` — the box answers through the script with the pinned model.
- Read `~/.claude/agents/pi-developer.md` back against the DoD checklist.
