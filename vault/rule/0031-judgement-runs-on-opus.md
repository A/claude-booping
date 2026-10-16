---
type: rule
title: Judgement runs on Opus; cheaper models only for routine with a known output
summary: Any step, agent or fallback that decides — drafts, reviews, folds findings in, verifies a DoD, researches, writes tests — runs on Opus; Sonnet and Haiku only for mechanical steps with a known output.
created_by: claude
created_at: 2026-10-17
updated_at: 2026-10-17
status: accepted
targets: [playbook-authoring]
brief: A step that needs judgement is detached to Opus; Sonnet or Haiku only for a mechanical step whose expected output is known (classification, extraction, a one-line record).
---

## Rule

A step, an internal agent, a fallback or an eval config whose work needs judgement — drafting,
reviewing, folding findings in, verifying a Definition of Done, researching, consulting the specs,
writing a manifest or a test suite — runs on Opus. Sonnet and Haiku are used only for a mechanical step
whose expected output is known in advance: classifying against a fixed list, extracting fields,
writing a one-line record. A cheaper model is not benchmarked as a candidate for judgement work.

## Follows from

- [Quality at a rational cost](../value/0012-quality-at-a-rational-cost.md) — booping is a professional
  tool and runs on a subscription; a lazy result costs more time than the model saves (owner,
  2026-10-17: Sonnet chose to do almost nothing in the owner's own agent game, Opus performs well).
- [Proven to work](../value/0010-proven-to-work.md) — the playbooks are measured on Opus; a step on
  another model is unmeasured.

## Exceptions

- A user's own config may pick any model for any step.
