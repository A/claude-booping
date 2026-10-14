---
type: adr
title: A step is inline, assisted or detached, set by one detached field
summary: The runner performs most steps itself; heavy reads go to a configured researcher that is resumed, not respawned; only a step that must not enter the runner's context is detached.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
values: [value/0002, value/0012]
sources: [playbooks/groom/_specs/DECISIONS.md, playbooks/retro/_specs/index.md, playbooks/code-review/_specs/DECISIONS.md, vault/notes/20260802-groom-skill-vs-playbook-metrics.md, vault/researches/20260802-01-31_framework-cli-extraction-research.md, CHANGELOG.md, CLAUDE.md]
---

## Context

The first groom playbook spawned one sub-agent per step through a step `agent:`
key. The skill-versus-playbook measurements traced the playbook's cost mostly to
call count and to content carried in context, and found researcher delegation
net-cheaper: a skill run that skipped the researcher paid about 1.2M extra
main-thread cache-read for inline reads. Some steps need isolation for a different
reason: code review's `review` step is detached so the diff never enters the
runner's context.

## Decision

Three delegation levels, set by the single `detached:` step field:

- **inline** — no `detached:`; the runner performs the step.
- **assisted** — the runner owns the step and hands heavy reads to the agent named
  by `core.research_agent`, which returns a compressed summary; the runner records
  the agent's id and resumes the same agent on loopbacks instead of spawning a
  fresh one.
- **detached** — `detached: <model>:<effort>` runs a generic sub-agent,
  any other string a named one; parallel co-members of a wave must be detached.

The `agent:` key is gone, and a leftover one stops the run. Groom runs its steps in
the driving session; its research steps are assisted and its cross-review is the
only detached step.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [Three levels in one field](#three-levels-in-one-field) | accepted | medium | medium | Delegate only where it pays |
| [A sub-agent per step](#a-sub-agent-per-step) | rejected | low | high | Groom's first shape; more calls and re-briefing |
| [Detached parallel briefs](#detached-parallel-briefs) | rejected | medium | high | Hands vault reads to agents |

### Three levels in one field

The runner keeps the conversation and the vault; agents get bounded work.

- **Pros:** the runner's context stays small where reads are heavy; an assisted
  agent keeps its warm context across loopbacks; one field replaces `agent:`.
- **Cons:** an assisted step's body must brief its agent itself; a detached step's
  body goes to the agent, so the runner never reads it.
- **Complexity:** medium.
- **Reversibility:** medium.

### A sub-agent per step

Every step runs in its own sub-agent named by `agent:`.

- **Pros:** every step starts from a clean context.
- **Cons:** each step re-reads and re-briefs; the user's conversation sits with the
  runner, not with the step's agent.
- **Complexity:** low.
- **Reversibility:** high.

### Detached parallel briefs

Retro's two mining briefs as two detached steps in one parallel wave.

- **Pros:** parallelism declared in the graph.
- **Cons:** the lesson set must reach both briefs verbatim from the runner, and the
  cross-check of their returns is the runner's; detaching would hand the vault
  lesson read to the agents.
- **Complexity:** medium.
- **Reversibility:** high.

## Consequences

- Retro's `prepare` is one assisted step issuing two parallel briefs.
- An external researcher is wired by setting `core.research_agent`, not by editing a
  step.
