# Project config

booping reads a single structured config — `src/config.yaml` in the plugin — and merges any project-local override from `~/Claude/{project}/config.yaml` over it at skill-load time. This page tours every top-level key and explains the override mechanic.

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

### `code_review.stack_markers`

Map of `{dependency-substring: template-name}` used by `/code-review` to auto-detect which review templates apply. The substring is matched against the repo's manifest files (`pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`, etc.); the value resolves against both `docs/review_templates/` and `~/Claude/{project}/review_templates/`. See [/code-review](code_review.md#stack-auto-detect).

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
