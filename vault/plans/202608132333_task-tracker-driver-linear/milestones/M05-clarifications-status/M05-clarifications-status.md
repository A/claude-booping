---
id: "05"
title: "awaiting-clarification status and clarifications sidecar"
sp: 3
status: pending
plan: "plans/202608132333_task-tracker-driver-linear/index.md"
---

# M05: awaiting-clarification status and clarifications sidecar

groom can park on `awaiting-clarification` with its open questions persisted in `clarifications.md` and the status to come back to recorded in `return_to`, then resume from a later invocation.

**Scope**: `playbooks/groom/playbook.yaml` (new status, two entering edges, two return edges), `src/config.yaml` (a `clarifications.md` seed in the groom scaffold), `docs/clarifications.md` (the sidecar's format, lazy-linked), `booping-python/e2e/cases/playbook-{state,transition}/`. The step bodies that write the file are M06's; the hooks that post it are M04's.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Add the `awaiting-clarification` status to groom's `run` machine with two entering edges — from `framing` and from `drafting` — each carrying `frontmatter-update index.md return_to={source status}` as its first hook, then `script tracker-comment clarifications.md` and `script tracker-sync`. The `when` text states that the run raised questions it cannot answer itself and wrote them to `clarifications.md`; the gate requires every question in the file to be open and attributed. | `playbooks/groom/playbook.yaml` | 1 | pending |
| 5.2 | Add the two return edges, `awaiting-clarification` to `framing` and to `drafting`, gated on every question in `clarifications.md` carrying an answer and on the target matching `return_to`, with `frontmatter-update index.md return_to=null` and `script tracker-sync` as hooks. Add `awaiting-clarification` to the `in-spec` superstate so the `cancelled` edge covers it. | `playbooks/groom/playbook.yaml` | 1 | pending |
| 5.3 | Define the sidecar format and seed it: `docs/clarifications.md` documents one H2 per question — `## C{n} — {topic} — open|answered` — with `**Asked:**` (date and the step that raised it), `**Question:**`, optional `**Options:**`, and `**Answer:**` followed by free markdown until the next H2, so multi-line answers need no escaping; add `clarifications.md` to `core.groom_playbook.scaffold` seeded with the H1 and no questions. | `docs/clarifications.md`, `src/config.yaml` | 1 | pending |

`when:` and `gates:` are free prose judged by the run, exactly as every existing groom transition writes them — no new manifest syntax is introduced by this milestone.

Tests: corpus cases at the `playbook-transition` boundary — `framing` to `awaiting-clarification` stamps `return_to=framing`, the return edge clears it, an illegal return (to a status that is not `return_to`) is refused — plus a `playbook-state` case showing `awaiting-clarification` in the frontier with both return edges listed.

## Definition of Done

### Task 5.1

- [ ] `bin/booping playbook-transition groom awaiting-clarification --workdir {plan-dir}` from `framing` writes `status: awaiting-clarification` and `return_to: framing`, and from `drafting` writes `return_to: drafting`.
- [ ] The mutation report lists the `frontmatter-update` line before both script hooks.
- [ ] `return_to` is written only by the hook — no step body and no manual edit sets it.

### Task 5.2

- [ ] The return edge to the status named in `return_to` succeeds and clears the key to null.
- [ ] `bin/booping playbook-state groom --workdir {plan-dir}` on a parked run reports `awaiting-clarification` with both return edges and their gates.
- [ ] Cancelling from `awaiting-clarification` works through the `in-spec` superstate.
- [ ] All four new edges carry `script tracker-sync` as their last hook, per M04's rule.

### Task 5.3

- [ ] `docs/clarifications.md` specifies the H2 shape, the `open`/`answered` marker, every bold field, and that the answer body runs to the next H2 — with one worked example carrying a multi-line, multi-paragraph answer.
- [ ] A fresh groom scaffold emits `clarifications.md` carrying its H1 and nothing else.
- [ ] The document states that a question is answered when its H2 says `answered` **and** its `**Answer:**` body is non-empty, so the gate has one unambiguous test.

## Verify

```
just e2e -k playbook-transition
just e2e -k playbook-state
bin/booping scaffold core.groom_playbook.scaffold /tmp/m05-scaffold-check --set title="T" --set type=feature
```

Expected: the new clarification cases pass; the frontier report shows the parked status with its return edges; the scaffold diff includes an empty `clarifications.md`.
