---
status: done
agents:
  step-prompt: a6365a4f3790e3f8b
  step-spec: a8e3ede70d47aa686
  llm-tests: a5118109e63224e91
reviewed_at: 20260802 09:49
fixtures_reviewed_at: 20260802 09:52
suite_reviewed_at: 20260802 09:58
---

[← index](../../index.md)

# verify

## Contract

- **Needs** —
  - the project's own guardrail tooling and the signals that identify it — the canonical
    commands when the repo's `CLAUDE.md` or the project-local `_booping/skill_develop.md`
    names them (trust them, skip discovery), else the usual signals: `package.json` scripts,
    `pyproject.toml` / `ruff.toml` / pyright config, `Justfile` / `Makefile` targets,
    `.eslintrc`, `tsconfig.json`, `cargo.toml` dev-dependencies. The hook-enforced (pre-commit,
    husky, lefthook, CI gate) vs configured-but-manual split is
    [development_quality_checks.md](${CLAUDE_PLUGIN_ROOT}/docs/development_quality_checks.md)'s
    and holds here — only the manual bucket is run, hook-enforced tools already fired at commit
    time. Its per-milestone framing does not: the suite runs **once**, at sprint end
  - the plan's Final Verification commands — verbatim as authored, run alongside the project's
    own suite
  - the sprint branch as it stands — the finished sprint's working tree in the attached repo,
    every milestone already committed
  - the sprint's completion state as recorded in the plan — every task DoD checkbox and every
    milestone status, read off disk, so completeness is checked against what the loop actually
    wrote rather than what it reported
- **Value** — one guardrail pass over the finished sprint, performed by a fresh agent whose
  context carries none of the loop: what the project itself enforces — tests, lint, typecheck,
  formatter, whatever else — plus the plan's own Final Verification, run once and reported
  pass/fail, plus the plan's own bookkeeping — every DoD checkbox `[x]`, every milestone `done`.
  What it answers is narrow and mechanical: can a PR open from this branch without CI failing,
  and is the plan actually finished. No code-quality judgement, no architectural opinion, no
  fixes applied — a red result is evidence handed back, not work started. One report answers the
  exit edge's gates by itself: a green verdict lets wrap-up close the run, a red one goes back to
  the runner for fixes and a re-run — no user confirmation involved.
- **Output files** —
  - none — the step writes nothing: no fixes, no plan edits, no report file. The report returned
    to the runner is the artifact; disposing of failures (delegating a fix to a worker agent,
    re-running this step, taking the `fail` branch after two attempts on one issue) is the
    runner's, not this step's
- **Harness return** — `## Changed:` stays empty (nothing is written). `## Notes:` carries one
  line per command actually run — the plan's Final Verification commands first, then the
  project's manual guardrails — each `PASS` or `FAIL`; a `FAIL` line carries enough evidence
  (failing test ids, rule codes, `file:line`) for the runner to brief a fix without re-running
  anything. Tools skipped as hook-enforced get their own line so the coverage is auditable.
  Two `plan:` lines close the checks — DoD checkboxes and milestone statuses, each `PASS` or
  `FAIL`, a `FAIL` naming the unticked boxes and the milestones still open. A closing `verdict:`
  line reduces the whole list to green / red: red when any command **or** either plan check
  failed. Nothing else — no summary paragraph, no recommendations, no praise, no proposed fixes.
- **Review gate** —
  - none — the guardrails decide: a green verdict proceeds to wrap-up, a red one goes back to
    the runner (fix delegated, verify re-run); no user confirmation. The guardrails themselves
    must be discoverable — the discovery ladder in the body is the contract, never an ad-hoc
    judgement of what to run
  - the `in-progress` → `awaiting-retro` edge's two conditions are answered by this one report:
    guardrails and Final Verification green, every DoD checkbox `[x]` and every milestone
    `done`. Wrap-up takes the edge; it re-confirms nothing
- **Delegation** — detached: `detached: "sonnet:medium"` — a generic sub-agent fetches this
  step's body itself (`booping render-playbook develop --step verify`) and performs it; the
  runner never reads the instructions and never runs the guardrails in its own conversation.
  The agent needs shell access to run the discovered commands plus reads over the repo; its
  bootstrap carries the attached repo path, the plan path (`plans/{slug}/index.md`, for the
  Final Verification commands) and the sprint branch.

## Example artifact

The step's return for a sprint on `feat/rate-limit-public-api` — no file is written, the block
below is the whole artifact:

```markdown
## Changed:

## Notes:
- `just test` (plan Final Verification) — PASS — pytest, 214 passed, 0 failed
- `curl -s localhost:8000/api/ping -H 'X-Forwarded-For: 1.2.3.4'` (plan Final Verification) —
  PASS — 200 then 429 on the 21st call, `Retry-After: 60` present
- `just lint` — PASS — ruff, 0 issues
- `just typecheck` — FAIL — basedpyright, 2 errors: `api/limiter.py:88` reportOptionalMemberAccess
  (`request.client` may be `None`); `api/limiter.py:141` reportArgumentType (`str` passed to
  `int` parameter `window`)
- skipped: `.pre-commit-config.yaml` (ruff-format, end-of-file-fixer) — hook-enforced, fired at
  commit time
- plan: DoD checkboxes — FAIL — 2 unticked: M2 task 2.3 "429 response logged with client id",
  M3 task 3.1 "burst window documented in CLAUDE.md"
- plan: milestone statuses — PASS — M1, M2, M3 all `done`
- verdict: red — 1 of 4 commands failing, 1 of 2 plan checks failing

## Questions:
```

A clean sprint closes on the same shape:

```markdown
## Changed:

## Notes:
- `just test` (plan Final Verification) — PASS — pytest, 214 passed, 0 failed
- `just lint` — PASS — ruff, 0 issues
- `just typecheck` — PASS — basedpyright, 0 errors
- skipped: `.pre-commit-config.yaml` (ruff-format) — hook-enforced, fired at commit time
- plan: DoD checkboxes — PASS — 14 of 14 `[x]`
- plan: milestone statuses — PASS — M1, M2, M3 all `done`
- verdict: green — 3 of 3 commands passing, 2 of 2 plan checks passing

## Questions:
```

## Return Format

```markdown
## Changed:

## Notes:
- `<command>`[ (plan Final Verification)] — PASS|FAIL — <evidence>
- skipped: <tool or config file> — hook-enforced, fired at commit time
- plan: DoD checkboxes — PASS|FAIL — <n of m [x], else the unticked ones by task>
- plan: milestone statuses — PASS|FAIL — <all done, else the milestones still open>
- verdict: green|red — <n> of <m> commands passing|failing, <n> of 2 plan checks passing|failing

## Questions:
```

`## Changed:` is always empty. One `## Notes:` line per command run, plan Final Verification
commands first, then the project's manual guardrails; one `skipped:` line per hook-enforced tool
left unrun; then the two `plan:` lines, then the `verdict:` line last. `FAIL` evidence names the
failing test ids, rule codes and `file:line`, or the unticked DoD items and open milestones by
name — never a re-run instruction, never a fix. `verdict: red` when any command or either plan
check failed. No prose outside the block.
