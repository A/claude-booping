# Input — refine-existing

Write the accepted row below. The project is `taskflow`; the current working directory is its vault root. The vault lives outside the attached repo, which is checked out at `repo/`. The run's retrospective is `retrospectives/202608051640_notification-center.md`; it covers the plan `plans/20260805-notification-center/index.md`. Run date: **2026-08-06**.

This run has no shell, so the `booping` commands the step names were run for you; their outputs:

- `booping specs init --tier project` — last stdout line `specs`: the project tier root, relative to the vault root. Its one existing record is `specs/rule/0002-information-architecture-pass.md`.
- `booping specs check --tier project` — cannot run here; check the edited record against the rule record shape yourself.

The user accepted the review table exactly as presented — the single row below is accepted. Sweep verdict: row 1 is `update existing at rule/0002`.

## Accepted review table

| # | Target | Type | Targets | Brief | Rule | Example |
|---|--------|------|---------|-------|------|---------|
| 1 | `rule/0002` | `rule` | `groom` | Before saving a prompt artefact, pass every block through the scoping, duplication, configurability, hierarchy and compaction checks. | Add a fifth check to the information architecture pass, **Compaction** — does the block say it in the fewest words that keep the substance? | A skill body restated its own config table in three paragraphs of prose. |

## Context files

<file path="retrospectives/202608051640_notification-center.md">
---
plan: plans/20260805-notification-center/index.md
plans:
  - plans/20260805-notification-center/index.md
title: Notification center
created: 2026-08-05 16:40
status: awaiting-learning
---

# Retrospective — notification center

## Finding — the checklist never asks about word count

During the mid-sprint review of the settings skill, the reviewer noticed the skill body spent
three full paragraphs describing, in careful prose, exactly the notification-channel matrix
that the config block directly above it already declared: every channel name, every default,
every override rule, all restated in sentences. The prose had already drifted from the config
once — it still described the retired `digest` channel — and it was pure weight.

The block sailed through the team's information-architecture checklist (rule 0002,
information-architecture-pass): it was scoped correctly, stated once, not a tunable, and at
the right level of detail — all four checks green. What no check ever asked was whether the
block earns its word count. The team's decision: extend that existing checklist with a fifth
check, compaction — does the block say it in the fewest words that keep the substance? This
is a refinement of the existing rule, not a new one; the four current checks and the
rule's example stay exactly as they are.
</file>

<file path="specs/rule/0002-information-architecture-pass.md">
---
type: rule
title: "Run every prompt artefact through the four-check information architecture pass"
summary: "Before saving a prompt-bearing artefact, check every block for scoping, duplication, configurability and hierarchy."
created_by: claude
created_at: 2026-04-23
updated_at: 2026-04-23
status: accepted
targets:
  - groom
brief: "Before saving a prompt artefact, pass every block through the scoping, duplication, configurability and hierarchy checks."
---

## Rule

Before saving any prompt-bearing artefact (skill, agent, partial, template, briefing), every block must pass four checks:

- **Scoping** — does this component need this information to do its job? If not, move it up or delete it.
- **Duplication** — does the same block live in other components? Extract to a partial.
- **Configurability** — is this behaviour a user might want to tweak? Partial it so the knob is in one place.
- **Hierarchy** — does every block sit at the right level of detail? Top-level docs describe *what*; deeper docs describe *how*.

**Example**: A skill body carried an inline sub-component roster (hierarchy), duplicated in two sibling skills (duplication), with one orphaned negative rule (scoping) and a hard-coded tunable threshold (configurability) — one pass caught all four.

## Follows from

- [clarify] Learnt from `retrospectives/202604231512_skill-refactors.md` in the project vault, which a record outside the vault cannot link — see the [tier README](../README.md); link a value or settle the source.
</file>
