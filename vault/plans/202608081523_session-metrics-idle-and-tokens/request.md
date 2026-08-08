# Request framing

## Request

> Can we not count time it waits for user? It looks incorrect. 2. I want to have a script that deterministically,l without LLM extracts active time, models and tokens spent (INPUT, OUTPUT, CACHE) by session id

## Task type

`feature`.

- Not `bug`: `booping session-time` implements its plan's stated algorithm exactly — a turn runs from a real user prompt to the last event before the next one. The 209m and 941m readings are that spec working as written. What changed is the intent, not the conformance, so this is a specification change rather than a defect against spec.
- Not `refactoring`: the numbers a user sees change, and a new CLI surface (metrics by session id, token totals) appears. Both are user-visible behavior changes, which a refactoring is defined to avoid.
- `feature` fits: a new measurement rule plus a new addressable reporting surface, both of which need milestones, DoD and a Verify.

## Problem

Today `booping session-time <plan>` sums turn spans across the plan's stamped sessions. A turn ends at the last event before the next real user prompt, so any stretch where the system is waiting on a human lands inside a turn and is counted as active work. Two mechanisms make this dominant rather than marginal in this project:

1. **Playbook questions and review gates go through `AskUserQuestion` and prose stop-and-wait.** A tool answer is a `tool_result` line, not a real user prompt, so an entire interactive groom — every question answered, every gate the user sat at — collapses into one turn. Measured: session `19353202` reports 209 active minutes, of which a single turn from the `/booping:playbook` invocation to ~3h later accounts for 175.
2. **A session left open across a break.** Session `dd8af31c` reports 929 minutes, of which one turn spans 16:51 → 07:39 the next morning.

Separately, the transcripts carry per-assistant-event `usage` — `input_tokens`, `output_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, and a `cache_creation` split by TTL — which nothing in the project reads today. There is also no way to ask for one session's metrics directly: `session-time` is addressed by plan, so a bare session id has no reporting surface.

## Clarifications and Decisions

- Idle is excluded by subtracting user-blocking tool waits, not by an idle threshold: the interval between a blocking tool call (`AskUserQuestion`, plan approval, permission prompt) and its `tool_result` is wait-on-human and does not count. Evidence: session `dd8af31c`'s 886.5m gap is exactly one `assistant[AskUserQuestion]` → `user[result]` pair, and `19353202`'s 175m turn is the same mechanism, so this rule alone resolves both known outliers.
- Fully deterministic, code only — no LLM in the extraction path at any point, because per-session LLM processing would be too expensive to run across a vault.
- The script reads the `sessions:` list a plan already carries, computes the metrics in code, and writes them back into that plan's frontmatter. Existing values are left alone unless `--force` is passed, which overrides them.
- Metrics land in plan frontmatter and are visible as `sprints.md` columns.
- One surface only: `session-stats`. `session-time` is superseded by it rather than kept alongside — how that retirement lands is a draft-plan call.
- The frontmatter contract is standardised around `sessions:`: run `session-stats` against a directory plus an optional filename mask (`index.md`, `retro.md`, …) and every matching artifact carrying `sessions:` gets the same standardised metric fields written back.
- Cache tokens are reported split — creation and read separately, never as one number.
- Token metrics are `INPUT`, `OUTPUT`, `CACHE` (split as above), per session and totalled.
- No post-implementation prose-shape reshape milestone: the work is Python and CLI, with no rendered prompt surface to re-read after the fact.
