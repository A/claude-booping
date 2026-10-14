---
type: idea
title: Groom scales its depth to the task
summary: Groom runs the full research and review chain only when the task needs it; a simple task or bug gets a lighter pass unless the user asks for depth.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: open
sources: [vault/notes/Notes.md, vault/notes/evals groom.md]
---

## Idea

Groom picks how much of its chain to run from the task's complexity: a simple task or a
bug gets a minimal pass, and the deeper roles run when the task is complex or when the
user asks for it — directly ("plan tests") or indirectly ("do deep research for this
task"). The source wrote this for the old role agents (techlead, PM, QA); in the playbook
those roles are gone, and the graph runs `intake`, `research-codebase`, `research-web`,
`draft-plan`, `cross-review` and `present` for every request.

A measurement ([reference/0006](../reference/0006-groom-playbook-vs-skill-cost.md)) puts the playbook groom at 2.4× the wall
time, 5.2× the main-thread API calls and 3.0× the output tokens of the old `/groom`
skill. The measurement does not say which steps the extra cost came from.

## How to check

- [clarify] The source names no check. Proposed: groom one small bug twice on the same
  commit — the full graph and the graph without `research-web` and `cross-review` — and
  compare the plans and their cost with `booping session-stats`; equal plans at a clearly
  lower cost say the idea pays.
