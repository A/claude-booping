---
reviewed_at: 2026-08-08 13:01
---

# docs — Brief

## Goal

A project-level playbook for claude-booping that writes and maintains the project's
documentation. It first establishes a stable spec set the whole procedure reads from — a short
project briefing that shapes what booping is and where it is going, the target audiences who
read its documentation, and the documentation surfaces that exist (README, docs site,
CHANGELOG, plugin-internal `docs/`, code comments, module headers) — then builds a feature
index of features, their capabilities and their groups, which doubles as the documentation
structure. From there each run detects what has been developed since the last run, researches
those changes against the spec set, decides per role and per surface what must be written, and
writes it. A reviewer pass guards the output against AI-slop prose, oversharing for the wrong
audience, and legacy narration that hides the current state.

## Success result

A run ends with the project's documentation surfaces updated to match the current state of the
repo: the spec set exists and is current, the feature index reflects the features and
capabilities that actually ship, a reviewed per-run update record lists what changed and where
each change landed, and every affected surface has been written in the tone and depth its
audience needs. Steps that were already satisfied are skipped rather than redone, and the
runner ends holding the file paths and the changed set — never the raw reading that produced
them.

## Artifact home

`{vault}/docs/`

## Wishes

- Stable spec set, established once and reused: project briefing (`_specs/index.md`), roles
  (`_specs/roles.md`), targets/surfaces (`_specs/targets.md`). The briefing is the shaping
  layer that catches vision migration (e.g. booping moving from a self-learning skillset into
  a Jinja/context-model playbook framework).
- Roles and targets are discovered by sub-agents reading the project, each written to its file
  by the agent, then confirmed by the runner at a review gate — the agent-writes-then-runner-
  gates pattern. The two are independent and should run in parallel. If both files already
  exist, present them compactly in chat and ask whether to refine or proceed.
- Feature index step modelled on the home-dir user-stories step, but a private copy that
  mutates independently. Produces features, their capabilities, and feature groups (epics) —
  the future documentation structure. Reference shape:
  `~/Dev/@A/notes/projects/{pasha_cars,maria-logistic,north-py}` feature index files.
  Priorities probably unnecessary for documentation. Skipped when the index is already a valid,
  fully-created file — smoke-checked by a cheap haiku sub-agent first.
- Change detection between runs: record what has already been documented (last developed plan,
  commit hash, or a cached plan→status mapping diffed against the current one) so the step
  surfaces only the difference and never re-reads the whole plan history. Must tolerate an old
  postponed plan being developed late.
- Research pass reads the newly delivered plans in sub-agents and returns change summaries tied
  to the spec set: effect on targets, on roles, on the feature index (new/changed/dropped
  capabilities, refactorings, reorganisation), and on the project briefing when the vision
  shifted.
- Change review is a compact typed table (vision shift | new feature | refactoring | feature
  drop | chore | …) that the user extends, refines or confirms in chat.
- Targeting step decides, per change, which role × surface combinations must be written and
  what each one says. Saved as a reviewable per-run file (`YYYYMMDDHHmm-{title}.md`) before
  anything is written. Its review gate sits at the default severity level so a
  high-severity-only setting skips it. Writing is delegated to a sub-agent after confirmation.
  CHANGELOG entries may deserve their own step.
- Reviewer pass covers three failure modes plus fact-checking: AI-slop text quality (split the
  document by sections, run a radical-compaction and a gentle-compaction pass per section, then
  merge — encapsulated in a sub-agent or a detached step so the runner's context stays clean);
  oversharing for the wrong role (business readers such as CPO/CTO must not get implementation
  detail — roles drive tone and focus in research and writing too); oversharing of legacy (no
  "it used to be like this" narration — documentation is a readable snapshot of the current
  state). Validate the result against facts: code, roles, targets.
- Runner owns state: every step reports its findings back to the runner — file paths to hand to
  later steps, the changed/updated set, detail level. Define explicitly what the runner must
  hold to do its job.
- Keep context clean: anything requiring deep codebase reading goes to a sub-agent that reads,
  summarises, and returns only the valuable part.
- Use loop patterns where they fit (e.g. writing updates end-to-end per feature) and design an
  efficient graph rather than a long chain.
- Keep steps small: ~50 lines of body as the aim, 100 lines as the soft cap, 400 lines for a
  whole step as the hard cap. Secondary to actual step complexity.
- Evals are out of scope for this authoring run — review covers the brief, the decomposition
  and the prompts only.
