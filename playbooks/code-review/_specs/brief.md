---
reviewed_at: 20260804 11:07
---

# code-review — Brief

## Goal

Turn booping's stateless `/code-review` skill into a playbook that runs comfortably in the same
session as `develop`, so the user can trigger a review right where the work just landed. The run
first settles **what** to review — offering the plan `develop` just delivered when one is in
hand, otherwise reading `git log --oneline` and proposing the latest coherent piece of work
(the latest plan delivery on the branch, a feature's worth of commits, whatever the commits
actually suggest), asked through `AskUserQuestion` with a free-text option so the user can name
an arbitrary scope outright. It then hands the review itself to a sub-agent that performs the
existing skill's craft — stack discovery, checklist selection, blast-radius mapping, the static
checklists and the plan- and lesson-aware dynamic checks — and returns findings classified by
severity. Those findings are finally presented through Plannotator for an in-browser human
review of code and AI comments together. The port stays close to the existing skill: small
changes plus dropping what the playbook shape makes redundant, not a rewrite.

## Success result

A run ends with the user having reviewed a scope they explicitly confirmed, in Plannotator, with
the sub-agent's severity-classified findings seeded as annotations, and their feedback returned
to the runner to act on (trivial nits applied inline, non-trivial fixes delegated, nothing
committed or pushed). When the Plannotator surface is unavailable the run degrades to chat-only
presentation instead of failing. No review artefact is left behind, no plan status moves, and
the stateless `/code-review` skill continues to work unchanged alongside the playbook.

## Artifact home

None — the run is ephemeral; findings live in the conversation and in Plannotator's own
transient batch, never in the vault or the repo.

## Wishes

- Designed to be run inside a `develop` session: when a plan was just delivered, offer it as the
  default review scope rather than re-deriving it.
- Scope selection is model judgement over `git log --oneline`, kept abstract — "the latest plan
  delivery on this branch, or a feature's worth of commits" — not a hardcoded commit rule.
- Ask scope with `AskUserQuestion`, always including a free-text option so the user can state an
  arbitrary target explicitly.
- The review proper runs in a detached sub-agent and returns issues with severity
  (`BLOCKER` / `SUGGESTION` / `NIT`), keeping the runner's context clean.
- Presentation goes through Plannotator (the `plannotator-reviewer` agent), with the chat-only
  fallback that agent already signals.
- Follow the existing `/code-review` skill closely — carry over its craft phases, its hard rules
  (no commits, linter-handled style filtered out, lesson violation is always a `BLOCKER`, no
  persistent report) and the review-template surface; drop only what the playbook shape makes
  redundant.
- Leave the stateless `/code-review` skill in place; the playbook is standalone, not a step
  inside `develop`.
