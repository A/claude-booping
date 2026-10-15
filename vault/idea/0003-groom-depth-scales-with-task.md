---
type: idea
title: A faster groom without losing quality
summary: Try several groom playbook variants and keep the one that runs faster with no loss in plan quality; depth scaled to the task is one of the variants.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-15
status: open
# also distilled from the owner's local, unpublished notes (vault/notes/ is gitignored): vault/notes/Notes.md, vault/notes/evals groom.md
---

## Idea

The owner wants to try different variants of the groom playbook, with one goal: find a
groom that runs faster without losing quality (owner, 2026-10-15). Today a plan of 12-29
SP spends 6-12 minutes in groom on top of 17-43 minutes of develop, and small plans pay
the same fixed groom cost as large ones. Variants to compare include skipping groom for
small mechanical plans (straight to develop with a short brief), a lighter graph, and the
depth-by-task variant below.

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

- Run each variant on the same set of requests on the same commit, and compare plan
  quality (the groom evals' rubric, the plan's later develop outcome: rework, failed
  attempts) and cost (`booping session-stats`: wall time, tokens, API calls); a variant
  wins when its cost is clearly lower and quality holds. booping-benchmarks holds the
  harness for such runs.
- [clarify] The source names no check. Proposed: groom one small bug twice on the same
  commit — the full graph and the graph without `research-web` and `cross-review` — and
  compare the plans and their cost with `booping session-stats`; equal plans at a clearly
  lower cost say the idea pays.
