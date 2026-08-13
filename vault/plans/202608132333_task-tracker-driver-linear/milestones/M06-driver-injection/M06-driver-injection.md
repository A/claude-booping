---
id: "06"
title: "Driver-conditional prompt injection into groom"
sp: 4
status: pending
plan: "plans/202608132333_task-tracker-driver-linear/index.md"
---

# M06: Driver-conditional prompt injection into groom

Under `core.tracker.driver: linear` a groom run reads its request from a Linear issue, persists questions instead of asking them interactively, and publishes the plan as a `plan`-labelled issue with milestone sub-issues cross-linked to the request — while the `cli` driver renders exactly what it renders today.

**Scope**: new `playbooks/_partials/tracker_driver.md`, `playbooks/groom/playbook.md` (preamble include), `playbooks/groom/intake/prompt.md` and its body, `playbooks/groom/present/prompt.md` and its body, `playbooks/groom/draft-plan/` body. `src/templates/_partials/_playbook_driving.j2` is deliberately not touched — it drives every interactive run.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | Write the protocol partial: under a `linear` driver it states the persist-and-exit rules — never call `AskUserQuestion`, never wait on a chat reply, write open questions to `clarifications.md` and transition to `awaiting-clarification`, end the run there; on entry, resume from `booping playbook-state` and read answers back out of the sidecar. Renders nothing at all when the driver is absent or `cli`. | `playbooks/_partials/tracker_driver.md` | 1 | pending |
| 6.2 | Include the partial in groom's preamble, which is already `jinja: true` and already includes a partial, guarding on `config.core.tracker.driver == 'linear'` so the `cli` render is byte-identical to the committed report. | `playbooks/groom/playbook.md` | 1 | pending |
| 6.3 | Add the intake block: under `linear`, resolve the request issue ref from the playbook's own ask (`/playbook groom LIN-123`), falling back to `$BOOPING_TRACKER_ISSUE` and stopping with a reported error when neither is present; read the issue with `bin/booping-tracker show --issue {ref}` instead of taking the ask from chat; record `tracker_provider` (the resolved driver name, `linear`) and `tracker_request` (that ref) with `bin/booping frontmatter-update`; and route the scope-challenge questions into `clarifications.md` rather than `AskUserQuestion`. | `playbooks/groom/intake/prompt.md`, `playbooks/groom/intake/{body}.md` | 1 | pending |
| 6.4 | Add the publish-and-approve block: under `linear`, `present` creates the plan issue with `issue-create --label plan` carrying the plan body, creates one sub-issue per milestone file with `--parent`, cross-links plan and request with `relate`, records `tracker_issue`, and then transitions to `awaiting-approval` and **ends the run** instead of asking for approval in chat — the human's approval arrives as a later Linear status move that hermes turns into the next invocation. `draft-plan`'s design-alignment questions route to `clarifications.md` the same way. | `playbooks/groom/present/prompt.md`, `playbooks/groom/present/{body}.md`, `playbooks/groom/draft-plan/{body}.md` | 1 | pending |

Tests: rendering is the surface — `bin/booping render-playbook groom` against a fixture vault pinning `core.tracker.driver: linear` must contain the persist-and-exit rules and the tracker invocations, and against the hermetic fixture (no tracker config) must equal the committed report byte for byte.

## Definition of Done

### Task 6.1

- [ ] The partial contains no motivation prose and no restated context — rules only, in the repo's partial style.
- [ ] With no `core.tracker` key present, the partial renders to nothing, not to an empty heading or a stray blank block.
- [ ] It names `clarifications.md`, the `awaiting-clarification` transition and the resume-from-`playbook-state` entry rule, and states plainly that the run ends after parking.

### Task 6.2

- [ ] `bin/booping render-playbook groom` with no tracker config produces output identical to `playbooks/groom/_reports/output.md`.
- [ ] The same command against a fixture vault with `driver: linear` includes the partial's rules once, in the preamble.

### Task 6.3

- [ ] Under `linear`, intake's body directs reading the request through `booping-tracker show` and never through chat.
- [ ] It records `tracker_provider` and `tracker_request` through `bin/booping frontmatter-update`, never by hand-editing frontmatter.
- [ ] The ref resolution order — ask argument, then `$BOOPING_TRACKER_ISSUE`, then a reported stop — is spelled out in the body, with no branch that guesses a ref.
- [ ] Rendering is the milestone's own test; that the recorded refs actually land in frontmatter is covered by the plan's manual pilot in Final Verification, and this milestone says so rather than claiming integration coverage it does not have.
- [ ] Under `cli`, intake's rendered body is unchanged.

### Task 6.4

- [ ] Under `linear`, present's body creates the plan issue, one sub-issue per file matched by `core.plans.milestones.glob`, and the cross-link — in that order, with the milestone id and title taken from each milestone file's frontmatter.
- [ ] It records `tracker_issue` through `frontmatter-update`, then transitions to `awaiting-approval` and ends; no prose approval ask is rendered under `linear`.
- [ ] Under `cli`, present's rendered body still carries the prose approval gate exactly as today.

## Verify

```
bin/booping render-playbook groom | diff - playbooks/groom/_reports/output.md
bin/booping render-playbook groom --project {fixture vault with driver: linear} | grep -c "clarifications.md"
just snapshots
```

Expected: the first diff is empty; the `linear` render mentions the sidecar in the preamble and in both step bodies; `just snapshots` reports no drift for the `cli` render. Any intended report drift is left for the user to accept — never run `just snapshots-accept`.
