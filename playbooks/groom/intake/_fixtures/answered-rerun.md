# Input — answered-rerun

Fold the user's answers into the framing. A first pass already ran on this request: it wrote
the `## Framing` section of `plans/20260801-develop-sprint-resume/index.md`, created
`plans/20260801-develop-sprint-resume/plan.md` beside it, and returned three scope questions.
The user has now answered all three, one line each, and asked for one more thing.

The user's request, verbatim — unchanged since the first pass:

> make `/develop` resume an interrupted sprint without re-running finished milestones

Run start of the first pass: **2026-08-01 10:20 UTC**. This re-run: **2026-08-01 11:05 UTC**.

The user's answers, in the order the first pass numbered the questions:

1. In the plan's own frontmatter — one key naming the last milestone group that finished. I do
   not want a second file to keep in sync.
2. Restart that group from the top. Resuming part-done inside a milestone is out of scope —
   the group is the unit.
3. Trust the record. The final verification pass at the end of the sprint re-runs everything
   anyway.

And one more thing, unprompted: before we design this, go and research how other task runners
do resumable runs — I want the current practice on the web, not just what our repo already does.

The project is `claude-booping`. Its repository conventions, the task-type catalogue with the
per-type grooming guidance, the project vault (`plans/`, parked plans included) and the run
workdir — the plan directory `plans/20260801-develop-sprint-resume/` — all sit on disk in the
current working directory. Read what the re-framing needs before writing anything.

## Context files

<file path="plans/20260801-develop-sprint-resume/index.md">
---
status: framing
---
# Develop sprint resume

## Framing

### Request

> make `/develop` resume an interrupted sprint without re-running finished milestones

### Restated problem

`/develop` claims a plan at `ready-for-dev`, moves it to `in-progress`, and works the plan one
milestone group at a time, briefing each group into a fresh sub-agent and committing its work
before the next. Nothing on the plan records which groups have already finished — the
frontmatter carries `started:` and nothing else — so a sprint that is interrupted, by a dead
session or by the user stopping one, leaves the plan at `in-progress` with no way to tell
finished work from pending. The next `/develop` run on that plan begins at the first milestone
and repeats work that is already committed. The request is that a resumed run pick up where the
interrupted one stopped.

### Task type

`feature` — a new user-facing capability: `/develop` gains behaviour it does not have today,
with an outcome the user can name (no repeated work on a resumed sprint), a design and
milestones of its own. Not a `bug`: nothing diverges from expected behaviour, an interrupted
run restarts from the top because that is all it was ever built to do, and there is no defect
to triage or reproduce. Not a `refactoring`: what changes is the observable behaviour of a
resumed run, not the internal structure behind unchanged behaviour, so a "no behaviour change"
DoD would be false.

### Scope boundaries

**In scope**

- recording per-milestone-group progress somewhere a later `/develop` run can read it
- `/develop` reading that record when it claims a plan already at `in-progress`, and skipping
  the groups the record marks finished
- picking up a sprint that was interrupted in the middle of a milestone group, part-done
- what a resumed run shows the user about what it decided to skip and why

**Out of scope**

- resuming a sprint in a different repository, or on a different branch than the interrupted
  run used
- how milestone groups are sized or bundled in the first place — that is groom's side of the
  handoff
- resuming any skill other than `/develop`

### Web research

Not requested — the request asks for no deep web research, and none was asked for since.

### Scope challenge

- [ ] Where should the progress record live — the plan's own frontmatter, its body, or a
      separate file in the vault?
- [ ] Should a sprint interrupted mid-milestone resume that group part-done, or restart the
      group from the top?
- [ ] Must a resumed run re-run the finished groups' `Verify` commands before skipping them, or
      trust the record?
</file>

<file path="plans/20260801-develop-sprint-resume/plan.md">
---
title: Develop sprint resume
type: feature
status: framing
sp: null
split_from: null
created: 2026-08-01
planned: null
started: null
completed: null
retro: null
goal: null
summary: ""
commit: null
---
</file>

<file path="CLAUDE.md">
# booping plugin — project guide

Claude Code plugin that grooms and executes plans across user projects. Plans live in the
per-project vault — `~/Claude/{project}/` by default, or a repo-local directory when the
`.booping` marker carries a `vault_path:` key. Skills, agents, templates and config live in
this repo.

## Plan lifecycle

There is no shared status vocabulary. Each playbook owns its own state machine in `playbooks/{name}/playbook.yaml`, and a plan's `status:` is whatever the running playbook's machine last wrote. The two machines that carry a plan through a sprint:

    groom:   framing → researching → drafting → cross-reviewing → presenting → awaiting-approval → ready-for-dev
    develop: awaiting-plan-review → ready-for-dev → in-progress → awaiting-retro

- `cancelled` is terminal on both machines and reachable from every non-terminal status of either, whenever the user cancels the run. `fail` is develop's other terminal branch, for an unrecoverable blocker.
- A plan no run has claimed yet carries no status: a split stub or a filed idea sits at `status: null` until a groom run picks it up.
- Status moves run through `booping playbook-transition {playbook} {to}`, the only writer of run state. The LLM decides the edge and clears the judgment gates; the command sets the status and runs the edge's hooks — date stamps, commit snapshot, vault commit — in one shot. Hand-editing frontmatter to move a plan is not a supported path.
- Plans carry a `commit:` field, the repo HEAD at the time of the snapshot, stamped on entry to `in-progress` after the user has confirmed the plan is still valid.

## The playbooks

Grooming, execution, retrospectives and learning are playbooks, each driven by `/playbook {name}`. Code review is still a skill.

- `groom` — deep-researches a request and produces a specified, estimated plan with a Definition of Done. Its machine runs from `framing` to `ready-for-dev`.
- `develop` — executes a groomed plan. It claims a plan at `ready-for-dev`, moves it to
  `in-progress`, and works the plan milestone by milestone: each milestone group is briefed
  into a fresh sub-agent that implements it, and the orchestrator commits the group's work
  before briefing the next. Consecutive small milestones are bundled into one briefing. A
  final verification pass runs the project's own lint / typecheck / test tooling plus every
  plan-authored `Verify` command once, at the end of the sprint. Nothing about which groups
  have already finished is written back to the plan while the sprint runs — the plan's
  frontmatter carries `started:` and nothing more — so the only record of progress is the
  commit history and the orchestrator's own context, both of which a new session starts
  without.
- `/code-review` — reviews changed code against layered, stack-aware checklists. It picks a
  review template per plan from the core set under `docs/review_templates/`, and a project's
  own `review_templates/` in the vault override a core template by sharing its name. The
  skill is stateless: chat-only output, no status of its own.
- `retro` — writes a project- and plan-specific sprint retrospective into the vault after a
  sprint reports done. The retrospective shape is built into the skill body; every project
  gets the same headings.
- `learn` — folds a retrospective's lessons into the project-local skill and agent
  extensions under `_booping/`.

## Skill design

- **Wide-domain**: skills must work across stacks — Django, Rust, Hugo. Project-specific
  concerns live in the vault, in `_booping/skill_{name}.md`, `lessons/`, and the project's own
  `CLAUDE.md`. Never in a skill in this repo.
- **Minimum useful context**: show only what the skill needs for the job at hand. Anything a
  single route needs is lazy-loaded from `docs/`, not inlined.
- **Schema over prose**: structured data lives in `src/config.yaml`. If a value is there, the
  skill body renders it rather than restating it.

## Vault layout

- `plans/{YYYYMMDD}-{kebab-title}/plan.md` — a groomed plan is a directory holding its
  `plan.md`, frontmatter per `docs/template_plan_frontmatter.md`; a parked plan not yet groomed
  is still the single stub file `plans/{YYYYMMDD}-{kebab-title}.md`.
- `sprints.md` — a snapshot rendered from the plans; never hand-edited.
- `plan_templates/`, `review_templates/` — project-local templates, discovered alongside the
  core ones and overriding a core template by name.
- `lessons/`, `notes/`, `_booping/` — accumulated lessons, user notes, per-skill extensions.

## Editing conventions

- `skills/{name}/SKILL.md` and `agents/{name}.md` are build artefacts — never hand-edited.
  Edit the template under `src/files/` and run `just build`.
- Conventional commits with a scope: `feat(booping): …`, `fix(install): …`.
- The plugin code stays stack-agnostic — no Python, Django or JS specifics inside skills.
- `just lint`, `just typecheck`, `just test` run ruff, basedpyright and pytest.
</file>

<file path="docs/task-types.md">
# Task types

Every plan is classified as exactly one of these three, and the classification decides which
grooming guidance applies.

| Type          | Description                                                                                                                                                          |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `feature`     | New user-facing capability. Needs a business goal, a design, milestones and a DoD.                                                                                   |
| `bug`         | Defect — observed behaviour diverges from expected behaviour. Needs triage, reproduction, a root-cause hypothesis, a minimal fix, and a regression test.              |
| `refactoring` | Internal structure change with no user-visible behaviour change. Needs a current-vs-target design, migration steps, and a no-behaviour-change DoD.                    |

## feature

- Ask the user what outcome they want **after this feature ships** — the user-visible change,
  not the implementation.
- If the request does not already state a clear goal, challenge the user to articulate it. No
  goal, no `ready-for-dev`.
- Capture the agreed outcome in the plan's **Context** section and write the one-line intent
  into the `summary:` frontmatter.

## bug

Work through three questions before drafting anything:

- **Code triage first** — confirm the defect exists in the code before planning a fix. If the
  cause is obvious on inspection (a misread condition, an off-by-one, a wrong argument order),
  groom with the root cause stated up front. If it is not obvious, pause and ask for repro
  steps, environment, expected versus actual — a plan on top of an unconfirmed bug is
  speculation.
- **Ask before drafting when the report is thin.** Missing repro steps, unstated version or
  environment, unclear severity, or behaviour that could plausibly be intended are all blocking.
- **Pick a test strategy up front**: the user verifies manually; an existing automated check
  already covers the surface and will turn green; or a regression test that fails before the
  fix and passes after — the default when the first two do not fit.

No business goal is needed; the implicit goal is "fixed and will not recur". Skip
product-manager elicitation unless it is genuinely unclear whether the current behaviour is a
defect or a decision.

## refactoring

- Ask what the user wants to be true **after the refactoring lands** — an easier extension
  point, removed coupling, fewer foot-guns, faster onboarding.
- No goal, no `ready-for-dev`, the same as a feature.
- The plan must carry a current-vs-target design and migration steps. The DoD is "no behaviour
  change": observable behaviour identical before and after.
</file>

<file path="plans/20260705-review-template-picker/plan.md">
---
title: Review template picker
type: feature
status: done
sp: 8
split_from: null
created: 2026-07-05
planned: 20260705 16:40
started: 20260706 09:10
completed: 20260709 18:05
retro: retros/20260709-review-template-picker.md
goal: success
summary: "/code-review picks a review template per plan, project-local overriding core"
commit: 4f1c9ab
---

# Review template picker

## Context

`/code-review` ran one built-in checklist for every stack. This plan gave the skill a template
catalogue: core templates under `docs/review_templates/`, project-local ones in the vault, a
project template overriding a core one by sharing its name, and per-plan selection driven by
the stack signals in the changed files.
</file>

<file path="plans/20260715-retro-template-picker.md">
---
title: Retro templates
type: bug
status: null
sp: null
split_from: null
created: 2026-07-15
planned: null
started: null
completed: null
retro: null
goal: null
summary: "retros come out in a different shape in every project"
commit: null
---

Parked idea, filed by hand — not groomed yet.

`/retro` writes every retrospective from the same built-in shape, so a Rust project and a
Django project end up with identical headings and neither fits. `/code-review` already picks
its template per plan and lets a project override the core set from its own
`review_templates/`; retro should pick the same way, with a project's own retro templates
winning over the built-in ones.
</file>

<file path="plans/20260718-transition-hook-runner/plan.md">
---
title: Deterministic transition hook runner
type: refactoring
status: awaiting-retro
sp: 13
split_from: null
created: 2026-07-18
planned: 20260718 10:05
started: 20260719 09:00
completed: 20260726 17:30
retro: null
goal: null
summary: "every status move runs through booping transition instead of hand-edited frontmatter"
commit: 9d2e7c1
---

# Deterministic transition hook runner

## Context

Skills moved plans by editing frontmatter and running git by hand, and each one drifted from
the others. This plan moved every mechanical mutation behind `booping transition {to} {plan}`:
status set, date stamps, commit snapshot, `sprints.md` re-render, vault commit — one command,
one authoritative mutation report. No observable change to where a plan can go.
</file>

<file path="plans/20260722-sprints-snapshot-drift/plan.md">
---
title: sprints.md drifts after a manual status edit
type: bug
status: in-progress
sp: 3
split_from: null
created: 2026-07-22
planned: 20260722 11:40
started: 20260730 09:15
completed: null
retro: null
goal: null
summary: "sprints.md keeps a stale row when a plan status is changed outside booping transition"
commit: c07be44
---

# sprints.md drifts after a manual status edit

## Triage

`sprints.md` is re-rendered by the `render-sprints` post hook, which only fires on a
`booping transition` move. A status edited any other way leaves the snapshot showing the old
row until something else transitions. Repro: edit a plan's `status:` in an editor, open
`sprints.md`, the old status is still there.
</file>
