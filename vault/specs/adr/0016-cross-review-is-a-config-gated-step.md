---
type: adr
title: Groom's cross-review is a detached step gated by one config key
summary: A second model reviews the drafted plan once, in its own detached step, only when core.groom_playbook.cross_review_agent names an agent; null skips the step.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
values: [value/0012, value/0005]
sources: [playbooks/groom/_specs/DECISIONS.md, vault/retrospectives/20260423-skill-refactors-chat-develop-retro.md, CHANGELOG.md]
---

## Context

The groom skill cross-validated plans through an external Gemini call
(`docs/cross_validation.md`, `booping-external-llm-call`). During skill-era grooms
the user twice had to stop repeated re-runs — "it's not a tool to run after every
change" — and a one-shot rule was written into the cross-validation partial. The
groom playbook needed the same review without framework code for one vendor.

## Decision

`cross-review` is a standalone step between `draft-plan` and `present`, run once.
It is detached to the agent named by `core.groom_playbook.cross_review_agent`, which
`src/config.yaml` declares `null`; the step's summary, `detached:` and body all gate
on that key's truthiness, and `null` skips the step. Its return is findings-only:
`- CRITICAL|RISK|NOTE: {finding} — {plan section}` lines, or `no findings`. The rules
for disposing of findings sit in the step's summary, because a detached step's body
goes to the agent and the runner never reads it.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [Config-gated detached step](#config-gated-detached-step) | accepted | low | high | One pass, any agent, zero framework code |
| [External Gemini call](#external-gemini-call) | rejected | medium | high | Vendor path in core; replaced for playbook runs |
| [A block inside draft-plan](#a-block-inside-draft-plan) | rejected | low | high | First playbook shape; became its own step |
| [A presence check on a project-only key](#a-presence-check-on-a-project-only-key) | rejected | low | high | A bare null renders as None |

### Config-gated detached step

A step that exists only when an agent is configured.

- **Pros:** any agent (for example codex) plugs in through config; one pass by
  construction; the plan's author and reviewer are different models.
- **Cons:** the runner sees only the summary, so the disposal rules must live
  there.
- **Complexity:** low.
- **Reversibility:** high.

### External Gemini call

The skill's path: a helper calls another vendor's model on the plan.

- **Pros:** not named in the source.
- **Cons:** vendor-specific code in core; re-runs had to be stopped by a rule.
- **Complexity:** medium.
- **Reversibility:** high.

### A block inside draft-plan

A Jinja block at the end of drafting spawns the reviewer when the key is set.

- **Pros:** no extra step.
- **Cons:** not named in the source beyond its replacement by a standalone step when
  the graph was reworked.
- **Complexity:** low.
- **Reversibility:** high.

### A presence check on a project-only key

`config.get('cross_review')`, a key with no core default.

- **Pros:** nothing in core config.
- **Cons:** a key with no default, schema or owner; rendering a bare `null` into
  `detached:` gives `None`, read as an agent id.
- **Complexity:** low.
- **Reversibility:** high.

## Consequences

- With no agent configured, the step is skipped entirely and groom runs without a
  second-model review.
