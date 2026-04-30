# Project config

booping reads a single structured config — `src/config.yaml` in the plugin — and merges any project-local override from `~/Claude/{project}/config.yaml` over it at skill-load time. This page tours every top-level key and explains the override mechanic.

## Snapshot: `src/config.yaml`

For context, the current plugin defaults. Source of truth: [`src/config.yaml`](https://github.com/A/claude-booping/blob/master/src/config.yaml) (this snapshot may lag).

<details>
<summary>Show full config</summary>

```yaml
sprint:
  default_threshold_sp: 35
  redecompose_threshold: 5
  max_milestones_per_agent: 2
  scale:
    - { sp: 1, meaning: "Simple text/config change, no risk" }
    - { sp: 2, meaning: "Simple task, predictable, no risk" }
    - { sp: 3, meaning: "Medium task, minor risks but predictable overall" }
    - { sp: 4, meaning: "Complex task, medium risk, may need small research but clear enough" }
    - { sp: 5, meaning: "Research task — developer needs to clarify and decompose further before proceeding" }

tasks:
  - type: feature
    description: "New user-facing capability. Needs business goal, design, milestones, DoD."
    doc_uri: ${CLAUDE_PLUGIN_ROOT}/docs/task_feature.md
  - type: bug
    description: "Defect — observed behavior diverges from expected. Needs triage, reproduction, root-cause hypothesis, minimal fix, and a regression test."
    doc_uri: ${CLAUDE_PLUGIN_ROOT}/docs/task_bug.md
  - type: refactoring
    description: "Internal structure change with no user-visible behavior change. Needs current-vs-target design, migration steps, and a no-behavior-change DoD."
    doc_uri: ${CLAUDE_PLUGIN_ROOT}/docs/task_refactoring.md

skills:
  help: {}

  install: {}

  develop:
    agents:
      booping-developer:
        good_for:
          - "All coding tasks — always delegate; never edit application code from the orchestrator"
      booping-researcher:
        good_for:
          - "Phase 0 drift spot-check: given a large set of plan-named files, determine whether actual file shape matches the plan's assumptions"
        bad_for:
          - "Milestone-diff review — that stays in the skill"
          - "Single-file reads — call Read directly"

  groom:
    agents:
      booping-researcher:
        good_for:
          - "Wide read or web search where results must be aggregated outside this skill's context and returned as a summary"
          - "Map blast radius across many files (which modules and integrations a change touches)"
          - "Extract patterns from a corpus too large to read directly (e.g. 'common shapes across 30 test files')"
          - "Verify package versions, image tags, API endpoints, CLI flags against current docs when many sources need to be checked"
          - "Cross-system architecture investigation across multiple repos or services"
          - "Compare framework/library options with deep tradeoff analysis"
        bad_for:
          - "Small checks — single-file reads, one-off greps, existence checks"
          - "When the information cannot be meaningfully compressed without losing signal the caller needs to decide"
          - "When the skill already needs to read the same few files for other reasons"
          - "When the question fits in a few lines of `ls`/`grep` output"

  learn:
    status: awaiting-learning

  retro:
    status: awaiting-retro
    agents:
      booping-researcher:
        good_for:
          - "Phase 0 session-log search: scan ~/.claude/projects/ across all session logs for the plan's time window and aggregate into a structured summary of user questions, blockers, and detours"
        bad_for:
          - "Single-file reads — call Read directly"
          - "Phase 2 sprint analysis — stays in the orchestrator"
          - "Phase 4 lesson cross-check — stays in the orchestrator using the in-context lesson set"

  code-review:
    status: awaiting-retro
    agents:
      booping-researcher:
        good_for:
          - "Blast-radius reads on large diffs (≥ ~5 files) aggregated into a compressed summary of touched modules and integration points"
        bad_for:
          - "Single-file reads — call Read directly"
          - "Small greps or existence checks that fit in a few lines of output"
      booping-developer:
        good_for:
          - "Applying user-approved non-trivial fixes surfaced by the review (BLOCKER or SUGGESTION)"
        bad_for:
          - "Trivial inline nits — orchestrator handles those directly"

  chat:
    agents:
      booping-researcher:
        good_for:
          - "Vault-wide reads aggregated into a summary (e.g. what plans exist, recurring themes across retros)"
          - "Plan or retro content extraction across ≥3 files where the results need to be compressed before returning to the skill"
          - "Web search aggregation when the user asks an open question that requires pulling from multiple sources"
        bad_for:
          - "Single-file reads — call Read directly"
          - "Simple greps or existence checks that fit in a few lines of output"
          - "Questions answerable with a short `ls` or `grep`"

git:
  commit_message: '<agent>: <plan title> <message>'
  branches:
    - branch: feat/
      when:
        - feature
    - branch: fix/
      when:
        - bug
    - branch: refactor/
      when:
        - refactoring
    - branch: chore/
      when:
        - other
        - tooling, dependency bumps, formatting

plan:
  statuses:
    backlog:
      desc: "Parked plan — not actively being worked on. Sibling stubs from split sprints and user-filed ideas not yet in grooming live here."
      owner: groom
      terminal: false
      artifacts:
        - "Plan stub at ~/Claude/{project}/plans/{YYYYMMDD}-{kebab-title}.md (split siblings or parked ideas)"
      transitions:
        - to: in-spec
          skill: groom
          when: "User asks /groom to shape a parked plan, or /groom is invoked on a fresh request"
        - to: cancelled
          skill: groom
          when: "User shelves the request before grooming"
          on_exit:
            - "set `completed: yyyymmdd hh:mm`"

    in-spec:
      desc: "/groom is actively specifying — researching, designing, drafting the plan."
      owner: groom
      terminal: false
      artifacts:
        - "Plan at ~/Claude/{project}/plans/{YYYYMMDD}-{kebab-title}.md with all milestones, SP estimates, and DoDs"
        - "Sibling stub plans (one per split sprint) under the same plans/ path"
      transitions:
        - to: awaiting-plan-review
          skill: groom
          when: "Draft is complete and ready to present to the user"
          gates:
            - "Cross-validation run (see [cross-validation](${CLAUDE_PLUGIN_ROOT}/docs/cross_validation.md)) — single-file-bug skip acceptable"
            - "Every task estimated; any task ≥ redecompose_threshold SP has been re-decomposed"
          on_exit:
            - "set `planned: yyyymmdd hh:mm`"
            - "set `commit: <repo HEAD>` from `context.project.git_commit`"
        - to: backlog
          skill: groom
          when: "User parks the work mid-grooming to revisit later"
        - to: cancelled
          skill: groom
          when: "User shelves the work mid-grooming"
          on_exit:
            - "set `completed: yyyymmdd hh:mm`"

    awaiting-plan-review:
      desc: "Plan drafted; /groom is presenting to the user and awaiting explicit approval, change request, or cancellation."
      owner: groom
      terminal: false
      transitions:
        - to: ready-for-dev
          skill: groom
          when: "User explicitly approves the plan ('looks good', 'ship it'). Silence does not count."
          gates:
            - "Explicit user approval captured"
        - to: in-spec
          skill: groom
          when: "User requests changes that require re-research or re-design"
        - to: cancelled
          skill: groom
          when: "User shelves the plan instead of approving"
          on_exit:
            - "set `completed: yyyymmdd hh:mm`"

    ready-for-dev:
      desc: "Approved by user. Queued for /develop to claim."
      owner: develop
      terminal: false
      transitions:
        - to: in-progress
          skill: develop
          when: "/develop claims the plan at the start of its execute phase"
          on_exit:
            - "set `started: yyyymmdd hh:mm`"
            - "set `commit: <repo HEAD>` from `context.project.git_commit` (only after the user confirmed the plan is still valid, or the legacy fallback applied)"

    in-progress:
      desc: "/develop has claimed the plan and is executing milestones."
      owner: develop
      terminal: false
      artifacts:
        - "Code changes per milestone on the sprint branch"
        - "DoD checkboxes flipped to [x] as tasks complete"
      transitions:
        - to: awaiting-retro
          skill: develop
          when: "All milestones done"
          gates:
            - "Every DoD checkbox marked [x]"
            - "Final Verification green"
          on_exit:
            - "set `completed: yyyymmdd hh:mm`"
            - "suggest `/retro <plan-path>`"
        - to: fail
          skill: develop
          when: "Unrecoverable blocker on the same milestone"
          gates:
            - "Two fix attempts documented in the plan"
            - "User has approved the abort"
          on_exit:
            - "set `completed: yyyymmdd hh:mm`"

    awaiting-retro:
      desc: "All milestones done; waiting for /retro to write the retrospective."
      owner: retro
      terminal: false
      transitions:
        - to: awaiting-learning
          skill: retro
          when: "Retrospective written and saved"
          gates:
            - "Retrospective markdown saved to retrospectives/"
            - "Self-review checklist passed"
          on_exit:
            - "set `retro: retrospectives/YYYYMMDD-{kebab-title}.md`"
            - "set `goal: success | partial | fail`"
        - to: done
          skill: retro
          when: "User opts to skip retro for a stale plan and mark it done without retrospective or learning"
          on_exit:
            - "set `goal: skipped`"

    awaiting-learning:
      desc: "Retro written; waiting for /learn to absorb lessons."
      owner: learn
      terminal: false
      transitions:
        - to: done
          skill: learn
          when: "All accepted learnings written"
          gates:
            - "User confirmed the review table"
            - "Every accepted lesson written to its target file"
          on_exit:
            - "set `completed: yyyymmdd hh:mm`"

    done:
      desc: "Terminal success. /learn has absorbed all lessons."
      terminal: true

    fail:
      desc: "Terminal technical failure. /develop hit an unrecoverable blocker."
      terminal: true

    cancelled:
      desc: "Terminal product decision. User shelved the plan."
      terminal: true
```

</details>

## Top-level keys

### `sprint`

Sprint sizing thresholds and the story-point scale. Drives `/groom`'s split proposals, the per-task re-decompose gate, and `/develop`'s milestone grouping.

- **`sprint.default_threshold_sp`** — soft cap on total SP per plan. Above this, `/groom` proposes splitting the plan into sibling stubs. Default: `35`.
- **`sprint.redecompose_threshold`** — per-task SP value at or above which `/groom` must re-decompose the task before the plan can leave `in-spec`. Default: `5`.
- **`sprint.max_milestones_per_agent`** — cap on consecutive milestones grouped into one `booping-developer` briefing by `/develop`. Default: `2`.
- **`sprint.scale`** — the 1–5 SP definitions rendered into `/groom`'s body. Each entry is `{sp, meaning}`. Replace wholesale to redefine the scale; do not partial-edit (lists merge by replacement, see below).

### `git`

Branch and commit conventions consumed by `/develop`.

- **`git.commit_message`** — the conventional commit format string the orchestrator follows for in-plan commits.
- **`git.branches`** — list of `{branch, when}` entries. `branch` is the literal prefix (e.g. `feat/`, `fix/`); `when` is a list of short matches against the plan `type` (`feature`, `bug`, `refactoring`) or freeform descriptors. `/develop` walks this list to pick the sprint branch prefix.

### `tasks`

The task-type taxonomy `/groom` classifies every request against. Each entry is `{type, description, doc_uri}`. The matching `doc_uri` lazy-loads detailed guidance for that task type during grooming. Adding a new task type means adding both a `tasks` entry and the corresponding doc under `docs/`.

### `plan.statuses`

The full plan-lifecycle definition: every status, who owns it, what it produces, what transitions out of it, what gates each transition has, and what `on_exit` mutations fire. Skills render only the slice they own (transitions where `skill: <self>`), so editing this key reshapes every skill's plan-transitions table at the next skill load.

Each status carries:

- `desc` — one-line human description.
- `owner` — the skill that owns this state.
- `terminal` — bool; terminal states (`done`, `fail`, `cancelled`) cannot transition out.
- `artifacts` — list of strings describing what the state produces.
- `transitions` — list of `{to, skill, when, gates?, on_exit?}`.

See [Plan lifecycle overview](https://github.com/A/claude-booping/blob/main/src/templates/docs/plan_lifecycle_overview.md.j2) for the rendered status graph; or run `bin/booping render src/templates/docs/plan_lifecycle_overview.md.j2` locally.

### `skills.<name>.agents`

Per-skill delegation guidance rendered into each skill's "Available agents" table. Each agent entry has `good_for` (a list of bullets describing when to delegate) and an optional `bad_for` (when not to). Currently populated for `groom`, `develop`, `retro`, `code-review`, and `chat`.

Skills also use `skills.<name>.status` to declare the single status they own (e.g. `learn → awaiting-learning`, `retro → awaiting-retro`).

## Overriding for one project

Drop a YAML file at `~/Claude/{project}/config.yaml` to override or extend the plugin's defaults for that project. The override file deep-merges over `src/config.yaml` at render time:

- **Dict keys merge.** A project key is added or replaces the plugin's value; sibling keys the project file does not mention fall through unchanged.
- **List keys replace wholesale.** If the project file sets `sprint.scale` or `git.branches`, the project list replaces the plugin list entirely — there is no element-level merge.
- **No rebuild required.** The merge happens at skill-load time, every time. Edit, save, run a skill — the new values are live.

The override takes effect at the next skill load. Nothing in `src/files/` or the build artefacts is touched.

### Example: tweak the SP threshold and add a branch convention

`~/Claude/{project}/config.yaml`:

```yaml
sprint:
  default_threshold_sp: 25  # smaller cap for this project's faster cadence

git:
  branches:                 # list — replaces the plugin defaults wholesale
    - branch: feat/
      when: [feature]
    - branch: fix/
      when: [bug]
    - branch: refactor/
      when: [refactoring]
    - branch: docs/
      when: [docs, documentation]   # new prefix for doc-only plans
    - branch: chore/
      when: [other, tooling]
```

After the next skill load, `/groom` proposes splitting at 25 SP instead of 35, and `/develop` picks `docs/` for plans typed `docs`.

Because lists replace wholesale, the project file must include every branch entry it wants to keep — omitting a row removes it. Dict keys behave the opposite way: `sprint.default_threshold_sp: 25` does not affect `sprint.redecompose_threshold` or `sprint.scale`, which fall through from the plugin defaults.

## Verifying the merged config

Run `bin/booping debug-context` from the project directory (the one with the `.booping` marker) to dump the assembled context — including the merged config — as YAML. This is the authoritative answer to "what value is the skill actually seeing?"
