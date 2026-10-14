---
type: story
title: Eval suites
summary: Promptfoo suites beside each step guard its contract in a deterministic and an llm-rubric tier.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: done
sources: [vault/docs/_specs/features.md]
---

As **a contributor**, I want an eval suite beside each step, so that a prompt change
that breaks the step's contract is caught.

## Criteria

- A suite's deterministic tier runs with `just smoke` and its llm-rubric tier with
  `just regress`.
- `just suites` lists every suite beside its step.
- Each run posts a sticky, advisory PR comment; there is no commit status and no merge
  gate, and the suites never run in CI.
