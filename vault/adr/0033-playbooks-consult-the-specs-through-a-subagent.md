---
type: adr
title: Playbooks consult the specs through a subagent
summary: A read-only subagent tells playbooks what the specs already decide, contradict or leave open.
created_by: claude
created_at: 2026-10-16
updated_at: 2026-10-17
status: superseded
values: [value/0002, value/0013, value/0012]
issues: []
---

Superseded by adr/0034 (2026-10-16): the consult mechanism moved there; the list of named points
where it runs gave way to the base guidance every playbook carries.

## Context

Specs reach the playbooks one way today: rules with `targets:` inject their `brief` into the targeted
step (booping:rule/0001, rule/0020). Values, ADRs, stories and references reach no groom or develop step, and
no step calls `booping specs`; only the `specs` and `project-manager` playbooks read the registry. So a
groom re-decides what an accepted ADR settled, a develop worker picks a default an ADR already
answers, and autonomous runs record defaults with no reference to a record. The orchestrator showed the
same gap on 2026-10-16: it set out to groom a request whose every decision was already made, wrote
adr/0032 after a one-word grep, and its autonomous runs logged defaults without citing records.

Reading the registry inline costs context: 104 project records plus core and global ones, and most
are irrelevant to any one request (value/0002). Agents already return bounded answers (booping:rule/0009) and
the driver owns every vault read and write (adr/0012, rule/0019). booping:rule/0030 makes groom name the values
in play and flag departures; idea/0008 (open) proposes ADR drafts for a plan's real forks.

## Criteria

- A playbook knows what the specs already decide before it decides.
- The main context grows by a bounded list, not by records.
- Departures from a record are visible to the owner, or recorded when no owner is present.

## Decision

1. **Specs consult.** A read-only subagent (`booping-researcher`) gets the question and the registry's
   index (`booping specs ls`, one summary line per record across every tier), opens only the records
   whose summary bears on it, and returns at most 15 lines in four groups: **decided** (records that
   already settle part of it, ref and how), **contradicted** (records the request or plan goes
   against, ref and why), **values in play** (refs), **silent** (what no record covers).
2. **Where it runs.**
   - groom: once at intake, on the request; again in the draft for each fork the draft meets.
   - develop: only when a worker hits a decision the plan does not make, before any default.
   - code-review: once per review, on the diff's intent, to check it against accepted ADRs and rules.
   - orchestrator and project-manager: before routing a request (groom, direct brief or a record
     first) and before self-accepting a decision in an autonomous run.
3. **What happens with the answer.** *Decided* is cited in the plan or the defaults file instead of
   being re-decided. *Contradicted* is shown to the owner at the next review gate, or in an
   autonomous run recorded with the ref and a `[clarify]` marker and never silently overridden.
   *Values in play* feed booping:rule/0030, whose targets widen from groom to develop and code-review.
   *Silent* is where a new record may be due: a real fork goes to idea/0008 (still open; this ADR
   gives it a trigger, not its design).
4. **After develop**, the driver updates the records the sprint touched: an ADR's status, a story it
   delivered, a `spec-gap` issue where the code now departs from a record.
5. The behaviour reaches each playbook as targeted rules (rule/0020), not as edits to every prompt.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [Subagent consult](#subagent-consult) | accepted | medium | high | Bounded context, reads only what bears on the question |
| [Index inline in the prompt](#index-inline-in-the-prompt) | rejected | low | high | Every step pays for the whole index and judges relevance itself |
| [Deterministic retrieval](#deterministic-retrieval) | rejected | medium | high | Tags and paths miss records about the same decision in other words |
| [Rule briefs only](#rule-briefs-only) | rejected | low | high | Today's state: ADRs and values never reach the steps |

### Subagent consult

The decision above.

- **Pros:** the main context gets 15 lines; the subagent reads bodies only when summaries say so; one
  return contract for every caller.
- **Cons:** a subagent call per consult (cost and a little latency); its judgement of relevance can
  miss a record.
- **Complexity:** medium — the consult brief, targeted rules per playbook, the after-develop update.
- **Reversibility:** high — rules can be retargeted or retired.

### Index inline in the prompt

Every step receives `booping specs ls` and reads what it wants.

- **Pros:** no extra call.
- **Cons:** a hundred-plus lines in every step's context, growing with the registry; the step itself
  must judge relevance mid-task.
- **Complexity:** low.
- **Reversibility:** high.

### Deterministic retrieval

`booping specs relevant <paths|tags>` picks records by tags, `sources` and touched paths.

- **Pros:** free and repeatable (value/0015).
- **Cons:** records are prose about decisions; a request in other words or a new path matches nothing.
  Useful later as the subagent's pre-filter, not as the consult itself.
- **Complexity:** medium.
- **Reversibility:** high.

### Rule briefs only

Keep injection of rule briefs as the only path.

- **Pros:** no work.
- **Cons:** values, ADRs and stories stay invisible to groom and develop; decisions repeat.
- **Complexity:** low.
- **Reversibility:** high.

## Consequences

- A consult brief in `src/` (the return contract above) and targeted rules for groom, develop,
  code-review, project-manager; booping:rule/0030's targets widen.
- The orchestrator's own process follows the same rule (consult before routing and before
  self-accepting); hermes-pet's CLAUDE.md line on updating `specs/` moves into the core as point 4.
- A measurable check: re-groom corpus case `s3-booping-specs-site-registries` and see whether the
  consult reports its decisions as already made.
