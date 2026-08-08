---
title: Run every prompt artefact through the four-check information architecture pass
targets:
  - groom
retro: retrospectives/20260423-skill-refactors-chat-develop-retro.md
---

**Rule**: Before saving any prompt-bearing artefact (skill, agent, partial, template, briefing), every block must pass four checks:
- **Scoping** — does this component need this information to do its job? If it belongs to a higher-level orchestrator, move it up; if it's residue from a past correction ("never read any lessons") with no positive rule attached, delete it.
- **Duplication** — does the same block live in other components? Extract to a partial; a single source prevents drift.
- **Configurability** — is this behaviour a user might want to tweak? Partial it so the main flow stays readable and the knob is in one place.
- **Hierarchy** — does every block sit at the right level of detail? Top-level docs describe *what* and *when*; deeper docs describe *how*. A block whose detail doesn't match its level belongs one layer up or down.

**Example**: A skill body contained the full roster of sub-components inline (hierarchy — belongs in a referenced doc), the same roster appeared verbatim in two sibling skills (duplication — extract), one entry was a negative rule with no positive counterpart (scoping — delete), and a threshold the user tunes was hard-coded in prose (configurability — move to config). Four-check pass caught all four in one sweep.
