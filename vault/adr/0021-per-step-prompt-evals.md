---
type: adr
title: Prompt behaviour is checked by per-step eval suites, advisory and outside CI
summary: Each playbook step can carry a promptfoo suite with a deterministic smoke tier and a judged regress tier; runs are proposed, not launched by steps, and post an advisory PR comment.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
values: [value/0010, value/0012]
sources: [playbooks/playbook-authoring/_specs/DECISIONS.md, CLAUDE.md]
# also distilled from the owner's local, unpublished notes (vault/notes/ is gitignored): vault/notes/20260709-prompt-hacks-split.md
---

## Context

Two sprints (35 + 36 SP) built a score-based benchmark harness. The 2026-07-22
retro found it unused: the actual need was regression safety per prompt
instruction, for which "unit test"-style evals with decomposed assertions
(promptfoo/DeepEval pattern) fit better; groom had never challenged the goal. The
prompt-hacks audit also wanted a way to prove an instruction can be removed safely.
The benchmark harness now lives in a separate repo, driven by a vault playbook.

## Decision

An eval suite sits beside its step (`tests.yaml`, `promptfooconfig.yaml`,
`_fixtures/`), with two tiers per fixture: `smoke`, deterministic script asserts,
and `regress`, llm-rubric judges. A step's `test-plan.md` covers both tiers; the
tier column decides the implementation. Shared asserts, graders and rubric prompts
live in `playbooks/_lib/`. Suites run through `just eval|smoke|regress` on
subscription auth (`claude -p`), never in CI; each run posts a sticky, advisory PR
comment — no commit status, no merge gate. Playbook-authoring's optimizer steps
never run evals themselves: a step diagnoses a given report, edits, and returns the
next command; the harness runs the tier and owns the loop and its bounds.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [Per-step suites, advisory](#per-step-suites-advisory) | accepted | medium | high | Regression check per instruction |
| [Score-based benchmark harness](#score-based-benchmark-harness) | rejected | high | high | Built, then unused for this need |
| [Evals as a CI gate](#evals-as-a-ci-gate) | rejected | medium | high | Not run in CI |

### Per-step suites, advisory

Small suites pinned to one step's contract.

- **Pros:** a failing check names the instruction that regressed; the cheap smoke
  tier runs without judge calls.
- **Cons:** suites must be written per step; most authoring runs skipped them, so
  several core playbooks ship without suites.
- **Complexity:** medium.
- **Reversibility:** high.

### Score-based benchmark harness

Whole-run scoring across cases and models.

- **Pros:** compares models and whole runs.
- **Cons:** did not answer whether a given instruction still holds; 71 SP sat idle.
- **Complexity:** high.
- **Reversibility:** high.

### Evals as a CI gate

Suites run on every push and block the merge on failure.

- **Pros:** a regression cannot merge unnoticed.
- **Cons:** evals are expensive — too expensive to run on every CI run. A playbook is
  built first and its prompts optimised against the evals afterwards; the evals are an
  optimisation tool, not a merge gate (owner, 2026-10-14).
- **Complexity:** medium.
- **Reversibility:** high.

## Consequences

- Suites exist for learn, playbook-authoring and the shared return contract;
  code-review, develop, migrate, retro and setup were authored with evals out of
  scope.
- The benchmark harness lives in the separate booping-benchmarks repo.
