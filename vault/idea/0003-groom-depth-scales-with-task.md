---
type: idea
title: A faster groom without losing quality
summary: Try several groom playbook variants and keep the one that runs faster with no loss in plan quality; depth scaled to the task is one of the variants.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-16
status: validating
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

- Experiment (owner, 2026-10-16; protocol in booping-benchmarks `groom/`): a corpus of past
  requests from hermes-pet and shatterlings (2 small, 2 medium, 2 complex), each in an isolated
  worktree at the commit before its plan with a vault stripped of plans, retros, notes and
  reviews; variants V0 the current groom, V1 a bare "write a plan", V2 bare + plan template,
  V3 template + stages, V4 V3 + cross-review (codex, fable, three OpenRouter models via
  pi-developer); metrics wall time, tokens and calls from `booping session-stats`, plan
  quality by a blind rubric judge against the historical plan, and for the best two a develop
  run scored by `bench-score`; each groom prompt paragraph probed against an empty-context
  agent to cut what the model already knows. Results land in a reference record, the chosen
  shape in an ADR.
- Added 2026-10-16 (owner): D1 — the whole development as one `claude -p` run with no groom
  or develop playbooks, compared on time and outcome with the historical pipeline; every
  variant runs in two isolation modes — a clean vault, and a vault with the project's plans,
  retros and reviews dated before the task (realistic: past plans may guide the model);
  historical reference plans came from older booping versions, so fresh references are made
  with the current booping at the end and the judge checks against both. Corpus: 6 done
  tasks, mostly web/client work (booping-benchmarks `groom/corpus/`).
- Owner's targets: small tasks (10-15 SP) reach develop with little or no grooming; complex
  ones keep research quality and also get faster; tokens about the same or lower.
- Run each variant on the same set of requests on the same commit, and compare plan
  quality (the groom evals' rubric, the plan's later develop outcome: rework, failed
  attempts) and cost (`booping session-stats`: wall time, tokens, API calls); a variant
  wins when its cost is clearly lower and quality holds. booping-benchmarks holds the
  harness for such runs.
- [clarify] The source names no check. Proposed: groom one small bug twice on the same
  commit — the full graph and the graph without `research-web` and `cross-review` — and
  compare the plans and their cost with `booping session-stats`; equal plans at a clearly
  lower cost say the idea pays.
