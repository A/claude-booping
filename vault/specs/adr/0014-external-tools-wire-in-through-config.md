---
type: adr
title: External agents and surfaces wire in through config; core names no external tool
summary: An external worker or review surface is a plain agent registered in config and steered by a targeted rule; core ships no wrapper for it and no playbook names it.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-15
status: accepted
values: [value/0005, value/0009]
sources: [playbooks/code-review/_specs/DECISIONS.md, vault/retrospectives/20260610-cli-logging-and-agent-namespacing.md, vault/retrospectives/20260610-plannotator-code-review-surface.md, vault/retrospectives/20260722-seven-plan-retro.md, CLAUDE.md]
---

## Context

Booping once generated native wrapper agents for external CLI workers through a
compile step, beside the path for native agents. The 2026-06-10 retro found the
orchestrator confused by that fork — re-invoking a CLI agent it was unsure had run —
and drew the takeaway to prefer one homogeneous delegation interface. The same day's
Plannotator retro found that a browser review surface attached through existing
config extension points with no core change, but that a blanket "never touch the
repo" invariant forced a contradiction; the narrower intent was "no
Plannotator-specific code in the repo". When the code-review playbook was authored,
an early design gave it a `review_surface` config key, a named surface agent, its
briefing grammar and its fallback exit codes; the user corrected that the playbook
knows nothing about Plannotator.

## Decision

An external worker or surface is a self-contained Claude Code agent (global at
`~/.claude/agents/` or the user's own), registered under
`core.{name}_playbook.agents.<id>` with `good_for`/`bad_for` bullets and steered by a
targeted rule on the step that delegates. Core ships no wrapper, compile step or
transport for it, and no playbook body names a specific external tool. Code review's
`present` step shows the findings in chat and collects the verdict; a browser round
is the configured agent's own business, and with no agent configured the chat
presentation is the whole review, not a fallback.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [Config-registered agents](#config-registered-agents) | accepted | low | high | One delegation path for every worker |
| [Generated CLI-agent wrappers](#generated-cli-agent-wrappers) | rejected | high | medium | Retired; a second delegation path |
| [A named surface in the playbook](#a-named-surface-in-the-playbook) | rejected | medium | high | Couples a core playbook to one tool |

### Config-registered agents

Every worker, internal or external, is an agent invoked the same way.

- **Pros:** one mental model for the runner; the user swaps workers in their own
  tier; core stays free of tool-specific code.
- **Cons:** the user writes the agent and its rule; booping never shapes the
  agent's prompt.
- **Complexity:** low.
- **Reversibility:** high.

### Generated CLI-agent wrappers

A compile step renders a wrapper agent per external CLI worker.

- **Pros:** an external CLI looks like a native agent.
- **Cons:** a non-homogeneous fork in delegation that confused the orchestrator; a
  build step and its templates to maintain.
- **Complexity:** high.
- **Reversibility:** medium.

### A named surface in the playbook

The code-review playbook briefs a configured surface agent with a diff ref, a repo
path and a findings shape, and routes its unavailable exit codes to a fallback.

- **Pros:** not named in the source.
- **Cons:** the playbook carries transport and tool details that are userland; a
  second presentation path to keep.
- **Complexity:** medium.
- **Reversibility:** high.

## Consequences

- `core.{name}_playbook.disable_internal_agents: true` leaves only the user's
  agents in a playbook's delegation table.
- The Plannotator agent and its transport script stay global, outside the repo.
