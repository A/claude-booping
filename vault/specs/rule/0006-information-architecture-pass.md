---
type: rule
title: Every prompt artefact passes the information-architecture check
summary: Before a prompt-bearing artefact is saved, every block passes four checks — scoping, duplication, configurability, hierarchy — and prose that only restates or motivates is cut.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
targets: [groom]
brief: "Before saving a skill, agent, partial, template or briefing, check every block for scoping, duplication, configurability and hierarchy; cut motivation, restated context and preambles."
sources: [CLAUDE.md, vault/retrospectives/20260423-skill-refactors-chat-develop-retro.md]
---

## Rule

Before a prompt-bearing artefact (skill, agent, partial, template, briefing) is
saved, every block in it passes four checks:

- **Scoping** — the component needs this to do its job; what belongs to a
  higher-level orchestrator moves up, and a residue of a past correction with no
  positive rule attached is deleted.
- **Duplication** — the block lives nowhere else; a block shared by several
  components is extracted to a partial.
- **Configurability** — a behaviour the user may want to tune sits in a partial or
  in config, not hard-coded in prose.
- **Hierarchy** — top-level docs say what and when, deeper docs say how; a block
  whose detail does not match its level moves a layer up or down, and
  route-specific detail is linked from `docs/` rather than inlined.

Motivation, restated context and preambles are cut: prose decays, the schema does
not.

## Follows from

- [Minimal effective context](../value/0002-minimal-effective-context.md) — a body carries only
  what its step needs.
- [Single source](../value/0003-single-source.md) — a duplicated block drifts.
- [Retro: skill refactors, chat, develop](../../retrospectives/20260423-skill-refactors-chat-develop-retro.md)
  — one pass caught an inlined roster, its verbatim copy in a sibling skill, a
  negative rule without a positive one and a hard-coded threshold.
