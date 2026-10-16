---
type: rule
title: A prompt rule earns its place by a measured miss
summary: An instruction enters a prompt or a targeted rule only after a minimal probe shows the model missing it; evals and benchmarks run only when the owner agrees.
created_by: claude
created_at: 2026-10-16
updated_at: 2026-10-16
status: accepted
targets: [playbook-authoring, learn]
brief: Add an instruction only after a minimal probe — one input, the prompt, one model call — shows the miss; ask the owner before any eval suite or benchmark; a rule the model ignores even when told becomes a check.
sources: [vault/reference/0007-groom-benchmark-2026-10.md]
---

## Rule

An instruction goes into a playbook prompt, a partial or a targeted rule only when the model is
shown getting that thing wrong without it. The evidence is the smallest that settles it, like a unit
test: one input, the prompt, one model call, and a look at the answer — or a correction already
recorded. A larger eval suite or a benchmark costs hours and money and runs only when the owner
agrees to it; propose it with its cost and what it would settle (owner, 2026-10-16).
What the model does unprompted stays out of the prompt. An instruction the model misses even when told
moves out of prose into a deterministic check or a structural step. Removing instructions is checked the same
way, smallest evidence first.

## Follows from

- [Minimal effective context](../value/0002-minimal-effective-context.md) — 16 of 45 groom rules were
  instructions the model follows anyway.
- [Quality at a rational cost](../value/0012-quality-at-a-rational-cost.md) — five extra rules made
  the groom variant cheaper and worse (reference/0007).
- [Proven to work](../value/0010-proven-to-work.md) — an instruction is kept for a measured reason, not
  for how plausible it sounds.

## Exceptions

- Owner decisions and safety constraints (secrets, irreversible actions) are stated without waiting
  for a miss.
