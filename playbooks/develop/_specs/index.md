---
status: done
agents:
  record-decision: ac4233d9aced7ca68
  interview: a16d5cb9825711dfc
  decompose: ab0035dbd7567adac
  states: a90f1e2d6bff037ed
  manifest: a187568290a1adf3a
reviewed_at: 20260802 09:35
playbook_yaml_reviewed_at: 20260802 09:43
regress: skip
---
# develop — Decomposition

Execute a groomed plan by delegating every task to a worker agent — the runner never edits
application code. The **preamble resolves the plan** before the first step — the invocation
argument, else the candidate table of plans sitting at the entry statuses — so the workdir is
known up front and the machine is readable on entry. Intake then adopts that plan: entry status
validated, approval confirmed in-step when the plan is still at `awaiting-plan-review`, then plan
validity checked against the repo's current commit (cheap summary first, full diff only on the
user's word). Provision sets the sprint up in one step — the branch name confirmed with the user
before the branch is created, the milestone groupings worked out internally and never put to the
user. Develop-loop then runs the whole sprint: pick a group, brief a worker agent, close the group
against its DoD and its plan-authored Verify command, commit, report, next group — the project's own guardrails all wait for sprint end — sequentially,
never two workers on one sprint branch. Verify runs detached at sprint end over the project's own
guardrails, and wrap-up updates the documentation, makes the final commit and reports. The run
has **no user-review gate on verify**: the guardrails decide — a green verdict proceeds to
wrap-up, a red one goes back to the runner for fixes and a re-run. The only stop for
confirmation is the branch name. There is no
code-quality review in this playbook and no reviewer step: verify is a validator, and the
guardrails it runs — linter, tests, whatever the project enforces — are what say the branch is
ready to open a PR from and that CI will not fail.

The run workdir is the groomed plan's own directory in the resolved vault, `plans/{slug}/`, and
its `index.md` is both the plan document and the machine's artifact — develop continues on the
file groom left behind, so the entry transition (`ready-for-dev` → in-progress) is a machine edge,
not step prose. The machine is develop's subset of the shared plan lifecycle, joined to groom's at
the edges: it accepts **both** `ready-for-dev` and `awaiting-plan-review` as entry statuses and
finishes at the review handoff, with the failure branch reachable from any executing point — an
unrecoverable blocker after two documented fix attempts and a user-approved abort — verification
included. Its statuses **are** the shared plan-lifecycle names written straight onto
`status:`: no `plan_status:` mirror and no playbook-local `_scripts/`, unlike groom (hook details
are the state step's to settle). The `/develop` skill stays untouched and remains the default
entry point; the two invariants it closes on — no application code written by the runner, no scope
additions — belong in the preamble, not repeated per step.

## Graph

```yaml
graph:
  intake: []
  provision: [intake]
  develop-loop: [provision]
  verify: [develop-loop]
  wrap-up: [verify]
```

A flat chain, no subgraph: the milestone-group loop is **internal to `develop-loop`**, which walks
the groups in order and spawns one worker agent per group. Keeping the loop inside one step is
what keeps it sequential — no wave can put two workers on one sprint branch — and keeps the
per-group bookkeeping (DoD checkboxes, task rows, milestone status, the milestone commit) in the
step that owns it. `verify` is the only detached step; every other step runs in the driving
conversation.

## Steps

| Step                          | Summary                                                                                                                                                                                                                                                                                                                                                                                                         | Inputs                                                                                                                                                                                                                                                                                                    | Artifact                                                                                                         | Gate                                                                                               | Delegation                                                       | Model         | Spec                                  |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- | ------------- | ------------------------------------- |
| intake                        | adopt the approved plan the preamble resolved: validate its status against an entry transition — confirming the user's approval in-step when it entered at `awaiting-plan-review` — then check plan validity against the repo's current commit — cheap summary first, full diff only after the user opts to revalidate; trivial drift patched in place with approval, non-trivial drift halted back to grooming | the plan — milestones, tasks with their file lists, DoD, Verify, status and commit baseline; whether the user has already approved it; the repo's own conventions; current repo HEAD and what changed since the baseline; on a legacy plan with no baseline, the actual shape of the files the plan names | drift findings carried in conversation; in-place plan edits on trivial drift                                     | none — the drift questions are asked in-step; a status mismatch or non-trivial drift stops the run | assisted — researcher agent for the legacy file-shape spot-check | opus-5:medium | [spec](steps/intake/index.md)         |
| provision | set the sprint up: pick the branch from the plan's task type per the branch conventions, propose a kebab-case name and create it only after the user confirms — one branch per sprint, the same name reused across repos — then work out the milestone groups the briefings will cover, grouped only where shared context makes one worker cheaper than one per milestone and within the configured ceiling | the plan's task type, title, milestones with their story points and execution order; how much context consecutive milestones share; the grouping ceiling from config; the project's branch conventions; the repo's current branch and whether a branch for this sprint exists; drift findings raised at intake | the sprint branch, created in the attached repo; the milestone groups and their order, held in conversation | the user confirms the branch name before the branch is created — the groupings are internal and never put to the user | inline | opus-5:medium | [spec](steps/provision/index.md) |
| develop-loop | run the sprint group by group in one pass: pick the next group, brief a worker agent on every milestone in it — per-milestone request, related files, DoD and Verify — and always delegate, even for a one-line change; on the worker's report verify the output, flip the DoD checkboxes, the task rows and the milestone status to done, run the milestone's plan-authored Verify command — the project's own guardrails all wait for sprint end — commit once per milestone, report what shipped, and move to the next group | the confirmed groups and their order; each milestone's tasks, related files, DoD and Verify; the project conventions the worker must follow; the plan's scope boundary; the worker's report and the resulting diff; the commit-message convention; fix attempts already spent on a failing issue | code changes on the sprint branch, one commit per milestone; plan updated — checkboxes, task rows, milestone statuses; a per-group summary in chat | none — the per-group report is informational, never a stop | assisted — one worker agent per group, spawned from within the step | opus-5:medium | [spec](steps/develop-loop/index.md) |
| verify | run the project's guardrails over the finished sprint once — tests, lint, typecheck, formatter, whatever else must hold for a PR to open without CI failing — plus the plan's own bookkeeping, every DoD checkbox `[x]` and every milestone `done`, read off disk, and return what passed and what failed; no code-quality judgement, no fixes applied here | the project's own guardrail tooling and the signals that identify it; the plan's Final Verification commands; the sprint branch as it stands; the plan's DoD checkboxes and milestone statuses as recorded | guardrail and completeness results returned to the runner | none — the guardrails decide: green proceeds to wrap-up, red goes back for fixes and a re-run | detached | sonnet-5:medium | [spec](steps/verify/index.md) |
| wrap-up | close the sprint: update the documentation the work invalidated or added, make the final commit, and report the sprint to the user with the handoff to review — completeness was already confirmed in verify's report, wrap-up re-checks nothing | the verification results and the review outcome; what the sprint changed and which docs it touches; the final DoD and milestone state; the commit-message convention | documentation updated; the closing repo commit; the sprint report in chat; the plan at its exit status | none — the gate was taken on verify | inline | opus-5:medium | [spec](steps/wrap-up/index.md) |

A failure at `verify` is delegated to a worker agent as a fix and the step re-run; two failed
attempts on the same issue take the failure branch, which is also reachable mid-loop on an
unrecoverable blocker — two documented fix attempts plus a user-approved abort.

`develop-loop` is **assisted, not detached**: the runner owns the loop and the plan bookkeeping,
and the coding work is what leaves the conversation — one worker agent per group, spawned from
inside the step exactly as the skill does today. `verify` is the one step whose body an agent
fetches and performs.

## States

See [states.md](states.md).

## Questions

- [x] ~~Where does plan selection happen — preamble or intake?~~ — the **preamble** resolves it:
      the invocation argument, else the candidate table of plans at the entry statuses. The
      workdir is therefore known before the first step and the machine is readable on entry.
- [x] ~~Which incoming statuses must the machine accept, and does develop mirror `plan_status:`
      through `_scripts/` the way groom does?~~ — it accepts **both** `ready-for-dev` and
      `awaiting-plan-review`, intake confirming the user's approval in the latter case. No mirror
      and no playbook-local `_scripts/`: the machine's statuses **are** the shared plan-lifecycle
      names, written straight onto `status:`. Hook details are the state step's to settle — none
      are decided here.
- [x] ~~Should the playbook gate between milestone groups?~~ — no. The group-completion report
      stays informational; `develop-loop` walks every group without a stop.
- [x] ~~Quality commands per milestone or once at sprint end, and do review templates / task-type
      guidance attach here?~~ — **once at sprint end**: the skill body wins over
      `docs/development_quality_checks.md`. Review templates and task-type guidance stay out of
      develop's scope — they are groom / code-review surfaces.
- [x] ~~May new shared partials be added under `playbooks/_partials/`?~~ — yes: branch conventions
      with the commit-message format, and a develop-flavoured agents block. `plan_frontmatter`,
      `plan_structure` and `sprint_planning` are reused as-is.
- [x] ~~Is the failure exit reachable mid-sprint?~~ — yes, from any executing point on an
      unrecoverable blocker (two documented fix attempts plus a user-approved abort),
      verification included.
- [x] ~~Who performs the code review, and does it deserve a step of its own?~~ — there is **no**
      code review here and no reviewer step or agent. `verify` is a validator: guardrails only —
      linter, tests and whatever else confirms the branch is ready to open a PR from and that CI
      will not fail. The guardrails decide by themselves — no user confirmation of the results;
      they must be discoverable per the step's discovery ladder.
- [x] ~~Do per-group quality checks run inside `develop-loop`?~~ — no. **Sprint-end only**: a
      group closes on its milestones' plan-authored Verify commands alone, and every project-wide
      check waits for the detached `verify`.
