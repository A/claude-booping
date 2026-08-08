---
plans:
  - plans/20260520-log-all-booping-cli-calls.md
  - plans/20260530-namespace-internal-agents-prefix.md
date: 2026-06-10
goal_summary: Both plans shipped clean (success) — semantic CLI invocation logging and first-try agent delegation; friction was concentrated in the cli-agent delegation model and in output-contract details settled mid-develop rather than at groom.
goal_verdicts:
  plans/20260520-log-all-booping-cli-calls.md: success
  plans/20260530-namespace-internal-agents-prefix.md: success
---

# Retro — CLI invocation logging + agent namespacing

Two plans on one branch (`feat/log-booping-cli-calls`): a logging feature (4 SP) and a delegation bug fix (2 SP). 4 commits: `c1d6900` (logging M1), `e72b180` (logging M2, built by the pi cli-agent), `c13e09c` (polish), `d37ea90` (namespace fix). Milestone DoD and Final Verification 100% on both. Both goals reached.

## What went well

- Shared `log_invocation(vault, subcommand, detail)` helper — one source of truth, semantic per-command detail instead of a raw argv dump (lesson 0004 honoured).
- `run-agent` migrated to the shared helper with byte-identical output formats; existing log tests kept passing with import/signature-only changes.
- CLAUDE.md vault-layout bullet for `.booping.log` landed inside the sprint (M2.4), not deferred (lesson 0005 honoured).
- Namespace bug cleanly diagnosed — bare `subagent_type` vs the harness's `booping:` plugin registration — and fixed in one macro branch plus a regression test that codified the correct names.
- Plannotator chosen for the code review (over revdiff); the browser review worked well.

## What went wrong

#### Delegation-model confusion

**What happened**: During develop, the orchestrator tried to re-invoke the pi cli-agent and was unsure it had run ("why re-invoke? pi-agent is cli agent. Check your prompt").

**Root cause**: cli-agent invocation diverged from the native-agent path — a non-homogeneous fork in delegation logic with no single mental model the orchestrator could rely on.

**Impact**: A burned develop cycle; the divergence is being generalized away by the in-progress native-wrapper work.

#### Log format churned mid-develop

**What happened**: The completion line, the changed-files trailer, and process-synchronicity semantics all surfaced during develop, not in the plan.

**Root cause**: The plan specified the log *line format* in prose but never locked its *content* with the user at groom.

**Impact**: The output contract was iterated live instead of decided up front.

#### Error output truncated

**What happened**: The first logging implementation capped stderr the same way as stdout; the user asked "can you not crop the error, please?".

**Root cause**: A single truncation rule applied to both channels, treating the error channel as verbose success output.

**Impact**: Debug information was hidden until the crop was removed (now `stdout[0:100]`, `stderr` full via `err_full = repr(child.stderr)`).

#### Agent return contract too loose

**What happened**: Mid-sprint the user had to constrain the agent: "agent just need to return list of changed files, nothing else."

**Root cause**: The briefing did not bound the agent's return shape, so the agent emitted extra prose.

**Impact**: Surplus agent output rots orchestrator context; corrected by codifying `OUTPUT_GUIDE` ("final reply MUST contain ONLY the list of files changed").

#### Release notes / docs overshare internals

**What happened**: Generated release notes listed `booping` CLI updates that users never interact with directly.

**Root cause**: Content generation is not audience-scoped — internal CLI changes leak into user-facing output.

**Impact**: Users see irrelevant internal churn; noise dilutes signal. Recurrence — the same oversharing pattern hit the May-21 cli-agent docs review ("no oversharing in docs … internal details of booping cli").

## Lesson gaps

No loaded lesson covered these issues — lessons `0004` (information-architecture four-check) and `0005` (stale-reference cleanup in sprint) were both honoured this sprint. The five issues above are new territory; the audience-awareness and homogeneous-delegation patterns are candidates for `/learn` to capture.

## Action items & takeaways

| # | Type | Item | Owner | Status |
|---|------|------|-------|--------|
| 1 | Task | Finish homogeneous external-agent encapsulation (native wrapper for cli agents) on `feat/cli-agent-native-wrapper` | Claude/User | Planned (in progress) |
| 2 | Heuristic | Groom presents output/log-format options (or asks the user) when a plan defines a user-facing output format — lock content at groom, not develop | standing | Planned |
| 3 | Task | Keep the error channel untruncated in audit logs; cap only verbose success output | Claude | Done |
| 4 | Heuristic | Agent briefings specify a minimal return contract — only harness-needed info, nothing else | standing | Done |
| 5 | Heuristic | Audience-aware content generation — release notes / user docs exclude internal-only changes (CLI internals); scope content to its audience | standing | Planned |

**Takeaways**

- Prefer one homogeneous delegation interface over native/cli special-case forks — divergent logic in a shared fork breeds orchestrator confusion.
- When a plan defines a user-facing output format, lock its content with the user at groom, not mid-develop.
- Delegation is lossy: an agent returns only what the harness needs; everything else rots context.
- Audience-targeted content must filter by audience — internal/CLI-internal changes don't belong in user-facing output (recurring; flag for `/learn`).

## Self-review checklist

- [x] Each "what went wrong" item has a named root cause (a pattern, not a restatement).
- [x] Lesson gaps cite existing lessons by path and explain the gap.
- [x] Items are specific with an owner (or "standing" for heuristics) and a clear next step.
- [x] Heuristics are concrete enough to apply next sprint.
- [x] "What went well" is honest, not inflated.
- [x] No blame language — focus on decisions and processes.
