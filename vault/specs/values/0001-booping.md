---
type: values
title: Booping
summary: Why booping exists and what it is like — a work tool for technical professionals that runs plans to the end, keeps the human in control cheaply and learns only through the human.
created_by: owner
created_at: 2026-10-14
updated_at: 2026-10-14
---

## Values

### Curated self-learning

The system gets better from its own runs, but only through the user and when the
user wants it: a lesson becomes a rule after the user takes it, not after every run.

- **In practice:** retro and learn run when the user asks; what they propose
  becomes a rule only with the user's consent.
- **Trade-off:** Mistakes may repeat until the user runs a
  retro.

### Minimal effective context

A step gets only what it needs. What the model already knows does not clutter the
context; skills and steps carry only the information that matters — ten lines, not
two hundred, when ten work.

- **In practice:** detail is linked and read on demand, never inlined in case
  it helps; a rule reaches a step as a short brief with a link.
- **Trade-off:** More files and indirection; a step may miss
  something it was not handed.

### Single source

Each fact, decision and piece of structured data lives in one place and is
referenced or rendered from there; a decision is kept together with its reason.

- **In practice:** config and records are the source; prose never restates
  them.
- **Trade-off:** A render pipeline and tooling to maintain.

### Analysable history

Plans, runs and their outcomes are kept across every project, so the history can be
analysed: practices taken over from one project to another, benchmarks, quality
comparison, problem analysis.

- **In practice:** plans, retros and reviews stay in the vault after they close;
  their shape stays stable enough to compare across projects and time.
- **Trade-off:** Storage and a stable artefact shape that
  is harder to change.

### Stack-agnostic core

The core knows nothing about a stack or a project; specifics live in the global and
the project tiers.

- **In practice:** skills, playbooks and the specs skeleton stay generic and
  leave enough room to extend booping in userland: the global and the project
  tiers add and override — their own plan templates, playbooks, rules.
- **Trade-off:** [clarify] proposed: the core ships no stack-specific defaults;
  whoever wants them writes them in their own tier.

### A constructor, not a fixed solution

Booping is a constructor — a framework for playbooks with a set of core mechanics —
not a ready solution fixed to one task.

- **In practice:** a project's config extends booping's logic: user playbooks,
  scripts and templates read their own config keys, and the core mechanics (state
  machines, hooks, queries, scaffolds, tiers) carry them.
- **Trade-off:** no schema gate on config: a mistyped key is not caught at load.

### Plans run to the end

The agent carries a plan through to the end on its own unless force majeure stops it.
Problems are found while planning, discussed with the user in that session, and not
solved ad hoc during the run.

- **In practice:** grooming hunts for open questions and settles them with the
  user before `ready-for-dev`; develop does not stop to ask what grooming should
  have asked.
- **Trade-off:** Longer planning sessions.

### Effective human review

Every step where a human takes part is convenient and effective for that human. The
cheap, compact artefact comes first and is checked before the expensive detail is
built on it, so a review never has to go several steps back because the first lines
already show the wrong thing was made.

- **In practice:** user stories start from a feature index — a compact table
  with capacity and breakdown the human can read, reorder, fix and decompose —
  and only then a story per feature; grooming and planning work the same way.
- **Trade-off:** More review checkpoints in a run.

### Adjustable control

The human can review the system deeply, or give the agent more freedom to act inside
the values and boundaries. Either way the human can take control back easily and
review the values and boundaries when things go the wrong way.

- **In practice:** what the agent did without review stays visible
  (`reviewed_at` or its equivalent), so the human can find it and analyse it
  later.
- **Trade-off:** The agent marks and records instead of
  silently deciding, which costs it time.

### Proven to work

We know the system works as it should and can guarantee it high
enough to call it reliable. Tests, snapshots, evals and checks are the tools, not the
value.

- **In practice:** a behaviour that matters is held by a check that would fail
  if it broke.
- **Trade-off:** The cost of building and keeping the test
  infrastructure.

### Everything in one place

Everything is plain files, easy to look at from one place — for example Obsidian;
symlinks back to the project repos keep it together.

- **In practice:** markdown and YAML in git; project specs are reachable from
  the user's home through symlinks.
- **Trade-off:** No database queries and no concurrent
  writes.

### Quality at a rational cost

Booping is a work tool for professionals, so the quality of the result matters. It
spends tokens rationally, without token-maxing, and keeps a balance between
simplicity and the quality of the result.

- **In practice:** step prompts are evaluated and narrowed while the evals show the
  result still holds; a step's prompt is tuned to a specific model and copied and
  re-tuned for another, with evals working as unit tests for the steps; what a
  sub-agent already knows when asked about a prompt detail does not belong in the
  prompt; lessons are written as compact rules with examples, not as a raw retro.
- **Trade-off:** A run sometimes costs more than the
  cheapest one that would pass.

### Guides to the goal

The system is clear to the user and leads them to the goal by the hand, while letting
a professional step aside and get there their own way.

- **In practice:** after a chat about a task and a grooming run, the system
  says how to call develop; given an under-groomed plan, it says so and what to
  do next.
- **Trade-off:** Hints the user may not need.

## Not valued

### Comfort for non-technical users

Booping is a work tool for professionals with a strong technical background. How
comfortable it is for people without that background is not what we optimise for —
they are not our audience.

- **In practice:** "Guides to the goal" guides a professional; it does not
  explain the basics of git, the terminal, tests or planning.
