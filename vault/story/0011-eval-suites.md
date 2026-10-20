---
type: story
title: Eval suites
summary: Promptfoo suites beside each step guard its contract in a deterministic and an llm-rubric tier.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-20
status: done
priority: P2
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

As **a contributor**, I want an eval suite beside each step, so that a prompt change
that breaks the step's contract is caught.

## Scenarios

1. A contributor changes a step's prompt.
2. The contributor runs the step's deterministic tier with `just smoke <playbook>/<step>`,
   then its llm-rubric tier with `just regress <playbook>/<step>`, on subscription auth.
3. The run posts a sticky, advisory comment on the pull request with the result.
4. `just suites` lists the suites when the contributor looks for the one beside a step.

## Edge cases

- A failing suite blocks nothing: there is no commit status and no merge gate.
- The contributor does not want a PR comment: `EVAL_PR=0` opts out.

## Out of scope

- Running the suites in CI.

## Criteria

- A suite's deterministic tier runs with `just smoke` and its llm-rubric tier with
  `just regress`.
- `just suites` lists every suite beside its step.
- Each run posts a sticky, advisory PR comment; there is no commit status and no merge
  gate, and the suites never run in CI.
