---
type: rule
title: A prompt rule earns its place by a measured miss
summary: An instruction enters a playbook prompt or a targeted rule only when a run shows the model getting it wrong without it; what the model does unprompted stays out.
created_by: claude
created_at: 2026-10-16
updated_at: 2026-10-16
status: accepted
targets: [playbook-authoring, learn]
brief: Add an instruction to a prompt or a targeted rule only for a miss a run showed; what the model does without being told stays out, and a rule the model ignores even when told moves into a check instead.
sources: [vault/reference/0007-groom-benchmark-2026-10.md]
---

## Rule

An instruction goes into a playbook prompt, a partial or a targeted rule only when a run — a
benchmark, an eval or a recorded correction — shows the model getting that thing wrong without it.
What the model does unprompted stays out of the prompt. An instruction the model misses even when told
moves out of prose into a deterministic check or a structural step. Removing instructions is measured
the same way: a batch is dropped when an ablation shows no loss.

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
