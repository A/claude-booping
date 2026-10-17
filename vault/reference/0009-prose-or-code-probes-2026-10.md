---
type: reference
title: Prose or code probes 2026-10
summary: Three cheap probes on 2026-10-18 — which rule wording makes a fresh model pick prose, an existing primitive or a new CLI correctly, and how sibling items should be groomed.
created_by: claude
created_at: 2026-10-18
updated_at: 2026-10-18
status: live
tags: [probe]
---

## Facts

Setup: `claude -p --model claude-opus-5-5 --setting-sources "" --tools ""`, no booping context beyond
a fixed description of the driver, the vault and the CLI's subcommands. Scenarios and their expected
answers were written by the agent after the owner's decisions of the day (adr/0036, adr/0037), so
they are a signal, not a proof; 2–3 repeats a cell.

**Probe 1 — which wording decides prose (A), an extended existing primitive (B) or a new CLI or
config key (C).** Eleven scenarios: autonomy mode (expected A), an agent-decisions log with a
corrections CLI already present (A/B), item questions read by `status` (B), idea capture (A/B), and
controls — transitions, a run registry, plan split, a status report, entry timestamps and session id,
a render-time slice of open entries (B/C), milestone feedback (A).

| Wording | Right | Autonomy | Feedback |
|---|---|---|---|
| none | 14/16 | C C | A A |
| value/0015 + rule/0025 + rule/0030 as of 2026-10-17 | 12/16 | C C | B B |
| "a mechanism earns its place" | 14/16 | C C | A A |
| ladder: prose → extend existing → new | 14/16 | C B | A A |
| old texts + ladder | 14/16 | B B | B B |
| old texts + "fewest mechanisms" value | 13/16 | C C | A B |
| "who reads the result" | 16/16, and 33/33 on all eleven × 3 | A A | A A |
| old texts + "who reads the result" | 15/16 | C C | A A |
| "who reads" + examples + "when unsure, prose" | 31/33 | C A C | A A A |
| the above + "count only readers that exist or are asked for" (rule/0025 now) | 33/33 | A A A | A A A |

- The old wording pushed a prose task into code: "only the findings text needs judgement; capturing,
  persisting and handing over are computable → code" (milestone feedback as a validated transition
  payload).
- Beside the old texts the new wording loses the autonomy case: the old texts must be replaced, not
  joined.
- Adding "a prompt filled in at render time" as a code reader let the model justify a config key by
  the template branch it would itself add — the shape `core.autonomy` had. The "readers that exist
  or are asked for" clause closed it.

**Probe 2 — groom an item with a sibling of the same shape.** Pairs: corrections → agent decisions,
flaky-test register → rejected review findings; control: run registry → per-plan cost.

| Brief | Same-shape pairs (6 runs) | Control (3 runs) |
|---|---|---|
| the item alone | no new CLI: open items with a kind, query at render, `items close` | extends `session-stats` |
| + the sibling's groomed plan (which adds a CLI) | 6/6 generalise the sibling's CLI into one (`ledger`, `register`) | 3/3 reuse, no forced merge |
| + "same batch, similar shape" from the manager | same as above | 2 reuse, 1 separate |

**Probe 3 — both items groomed together in one plan.** Same pairs: 6/6 one mechanism for both, 5/6
with no new CLI (open items with a kind, or a note per entry through `scaffold`, `frontmatter-update`
and a render-time query); control 3/3 one design (cost rolled up from run records), sensible rather
than forced.

- A sibling's plan anchors the next one: it generalises the sibling's new CLI instead of returning to
  an existing primitive. Grooming together sees the shared shape first and does not anchor.
- Parallel grooming without the sibling is how the corrections, defaults and questions CLIs came to
  exist side by side (plans 202610151532 and 202610151609, groomed the same afternoon).

## How to check

- Prompts, variants and raw answers: `~/.tmp/booping-probes-2026-10-18/exp` (probe 1, `run1.sh`,
  `sc/`, `var/`, `out/`) and `exp2` (probes 2 and 3, `run1.sh`, `runT.sh`, `out/`).
- Re-run one cell: `./run1.sh <scenario> <variant> <rep>` from that directory.
