---
type: adr
title: Procedures are playbooks behind one skill
summary: Every booping procedure ships as a playbook driven by the single /playbook skill; a new skill is written only for a surface /playbook cannot drive.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
rules: [rule/0024]
values: [values/0001#plans-run-to-the-end, values/0001#stack-agnostic-core, values/0001#minimal-effective-context, values/0001#quality-at-a-rational-cost]
sources: [playbooks/groom/_specs/DECISIONS.md, playbooks/code-review/_specs/DECISIONS.md, vault/notes/20260802-groom-skill-vs-playbook-metrics.md, CHANGELOG.md, CLAUDE.md]
---

## Context

Booping's procedures started as skills: `/groom`, `/develop`, `/retro`, `/learn`,
`/chat`, `/help`, `/install`, `/code-review`. A skill has no run state, so an
interrupted procedure cannot resume in another session. The groom skill was ported
to a playbook and ran in parallel with it during beta; the other skills followed.
At authoring time the stateless `/code-review` skill was kept because it took an
arbitrary scope with no plan, which a playbook step could not handle then.

Five runs grooming the same feature measured the cost of the playbook shape. The
third playbook version against the second skill run: +61% API calls, +38% cache
read, about 1.75× wall-clock, final context −7%, user wait −48%. The remaining gap
is call count — transitions and gate round-trips — which the note calls the state
machine's floor.

## Decision

`/playbook` is the only skill the plugin ships. Groom, develop, code-review, retro,
learn, setup, migrate and playbook-authoring are core playbooks, discovered beside
the user's global and project playbooks. A playbook carries run state in its own
artifact and resumes across sessions; step bodies load one at a time. A new
procedure is a playbook; a skill is written only for a surface `/playbook` cannot
drive. Code review of an ad-hoc scope moved into the code-review playbook
(`plan: null`), so the stateless skill went too.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [One playbook skill](#one-playbook-skill) | accepted | high | low | Run state, resume, user-extensible procedures |
| [A skill per procedure](#a-skill-per-procedure) | rejected | low | high | No run state; cheaper per run |
| [Playbooks beside the skills](#playbooks-beside-the-skills) | rejected | medium | high | The beta shape; two copies of each procedure |

### One playbook skill

Every procedure is a playbook; `/playbook` lists, selects and drives them.

- **Pros:** run state persisted per artifact and resumable; the user adds procedures
  in their own tiers; one driving protocol instead of one per skill.
- **Cons:** more API calls and about 1.75× wall-clock against the skill on the
  measured groom runs.
- **Complexity:** high — a playbook engine, state machines, a driving protocol.
- **Reversibility:** low — every procedure and the user's own playbooks depend on it.

### A skill per procedure

Each procedure is one skill body rendered at load.

- **Pros:** fewer calls; shorter wall-clock on the measured runs.
- **Cons:** no persisted run state, so no resume across sessions; every skill
  repeats its own driving logic.
- **Complexity:** low.
- **Reversibility:** high.

### Playbooks beside the skills

The playbook ships next to the untouched skill, as during the groom, develop and
retro ports.

- **Pros:** a fallback while the playbook is in beta.
- **Cons:** two copies of each procedure to keep in step.
- **Complexity:** medium.
- **Reversibility:** high.

## Consequences

- `/chat` and `/help` were retired; `skills/` holds only `playbook`.
- A run costs more calls than the old skill did; further squeezing is batching
  transitions with work, which the metrics note calls diminishing returns.
- Authoring a procedure goes through the playbook-authoring playbook.
