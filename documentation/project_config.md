# Project config

booping reads a single structured config — `src/config.yaml` in the plugin — and deep-merges two override tiers over it at skill-load time: a **global** tier (`${XDG_CONFIG_HOME:-~/.config}/booping/config.yaml`) and a **project** tier (`~/Claude/{project}/config.yaml`). The merge order is **core → global → project**, later tiers winning. This page tours the key space and explains the override mechanic.

## Shape: two top-level keys

The whole config lives under exactly two top-level keys:

- **`home_dir`** — the vault-home base. It has to be top-level because it resolves *where the vault is*, before any namespace inside the config is reachable. See [The global tier](#the-global-tier).
- **`core`** — everything the shipped playbook set owns.

Inside `core` there is one placement rule:

| The key is… | It lives at… |
|---|---|
| owned by exactly one playbook | `core.{name}_playbook.…` |
| shared by the development loop or several playbooks | `core.…` directly |

`{name}` is the playbook's name with `-` replaced by `_` — `groom` → `core.groom_playbook`, `code-review` → `core.code_review_playbook`. The rule is applied literally, including to the two scaffold trees; the verbosity is the price of the convention being teachable.

**`core` is the worked example your own playbooks copy.** A playbook you write declares its own namespace the same way and reads it with `{{ config.core.my_playbook.… }}` (or `{{ config.my_namespace.… }}` if you'd rather not sit under `core` at all).

!!! note "Nothing is validated"
    There is no schema gate, no unknown-field warning, and no key that is restricted to a particular tier. A config declaring an invented `core.my_playbook.whatever` block loads unchanged; so does a project-tier `core.macros` entry, which means a repo carrying a local vault can declare argv that a render executes. Override a `core.*` key the plugin ships and getting it right is yours.

## Snapshot: `src/config.yaml`

For context, the current plugin defaults (comments trimmed). Source of truth: [`src/config.yaml`](https://github.com/A/claude-booping/blob/main/src/config.yaml) (this snapshot may lag).

<details>
<summary>Show full config</summary>

```yaml
home_dir: ~/Claude/

core:
  research_agent: "booping:booping-researcher"

  macros:
    date: ["date"]

  plans:
    glob:
      - plans/*/index.md

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

  task_types:
    - type: feature
      description: "New user-facing capability. Needs business goal, design, milestones, DoD."
      doc_uri: ${CLAUDE_PLUGIN_ROOT}/docs/task_feature.md
    - type: bug
      description: "Defect — observed behavior diverges from expected. Needs triage, reproduction, root-cause hypothesis, minimal fix, and a regression test."
      doc_uri: ${CLAUDE_PLUGIN_ROOT}/docs/task_bug.md
    - type: refactoring
      description: "Internal structure change with no user-visible behavior change. Needs current-vs-target design, migration steps, and a no-behavior-change DoD."
      doc_uri: ${CLAUDE_PLUGIN_ROOT}/docs/task_refactoring.md

  groom_playbook:
    cross_review_agent: null
    agents:
      booping-researcher:
        internal: true
        good_for:
          - "Wide read or web search where results must be aggregated outside this skill's context and returned as a summary"
          - "Map blast radius across many files (which modules and integrations a change touches)"
          - "Extract patterns from a corpus too large to read directly"
          - "Verify package versions, image tags, API endpoints, CLI flags against current docs"
          - "Cross-system architecture investigation across multiple repos or services"
        bad_for:
          - "Small checks — single-file reads, one-off greps, existence checks"
          - "When the information cannot be meaningfully compressed without losing signal"
    queries:
      latest_plans:
        where:
          status:in: [ready-for-dev, in-progress, done, fail, cancelled]
        sort: "-created"
        columns: [status, title, summary]

  develop_playbook:
    git:
      commit_message: '<agent>: <plan title> <message>'
      branches:
        - { branch: feat/,     when: [feature] }
        - { branch: fix/,      when: [bug] }
        - { branch: refactor/, when: [refactoring] }
        - { branch: chore/,    when: [other, "tooling, dependency bumps, formatting"] }
    agents:
      booping-developer:
        internal: true
        good_for:
          - "All coding tasks — always delegate; never edit application code from the orchestrator"
      booping-researcher:
        internal: true
        good_for:
          - "Phase 0 drift spot-check across a large set of plan-named files"
        bad_for:
          - "Milestone-diff review — that stays in the skill"
          - "Single-file reads — call Read directly"

  retro_playbook:
    status: done
    queries:
      candidates:
        where: { status: done, retro: null }
        sort: "-created"
        columns: [status, sp, title, created, completed]
    agents:
      booping-researcher:
        internal: true
        good_for:
          - "Phase 0 session-log search across ~/.claude/projects/ for the plan's time window"
        bad_for:
          - "Single-file reads — call Read directly"

  learn_playbook:
    queries:
      candidates:
        glob: [retrospectives/*.md]
        where: { status: awaiting-learning }
        sort: "-created"
        columns: [status, title, created, plan]

  code_review_playbook:
    queries:
      scope_candidates:
        where: { status: done }
        columns: [sp, title, code_reviews]
    agents:
      booping-researcher:
        internal: true
        good_for:
          - "Blast-radius reads on large diffs (≥ ~5 files) aggregated into a compressed summary"
        bad_for:
          - "Single-file reads — call Read directly"
      booping-developer:
        internal: true
        good_for:
          - "Applying user-approved non-trivial fixes surfaced by the review"
        bad_for:
          - "Trivial inline nits — orchestrator handles those directly"

  migrate_playbook:
    queries:
      pending:
        root: core
        glob:
          - migrations/*/migration.md
        sort: id

  setup_playbook:
    scaffold:
      plans:   { type: dir }
      retrospectives: { type: dir }
      _lessons: { type: dir }
      notes:   { type: dir }
      sprints.md: |
        ```base
        ...an Obsidian Bases fence over plans/...
        ```
      .gitignore: |
        .booping.log

  playbook_authoring_playbook:
    scaffold:
      playbook.md: |
        ...identity frontmatter + preamble stub, seeded with --set name=...
      playbook.yaml: |
        graph: {}
      _references: { type: dir }
```

</details>

## Shared keys, directly under `core`

### `core.sprint`

Sprint sizing thresholds and the story-point scale. Drives the groom playbook's split proposals, the per-task re-decompose gate, and the develop playbook's milestone grouping.

- **`core.sprint.default_threshold_sp`** — soft cap on total SP per plan. Above this, groom proposes splitting the plan into sibling stubs. Default: `35`.
- **`core.sprint.redecompose_threshold`** — per-task SP value at or above which groom must re-decompose the task before the run can leave `drafting`. Default: `5`.
- **`core.sprint.max_milestones_per_agent`** — cap on consecutive milestones grouped into one `booping-developer` briefing by the develop playbook. Default: `2`.
- **`core.sprint.scale`** — the 1–5 SP definitions rendered into groom's body. Each entry is `{sp, meaning}`. Replace wholesale to redefine the scale; do not partial-edit (lists merge by replacement, see below).

### `core.task_types`

The task-type taxonomy groom classifies every request against. Each entry is `{type, description, doc_uri}`. The matching `doc_uri` lazy-loads detailed guidance for that task type during grooming. Adding a new task type means adding both an entry here and the corresponding doc under `docs/`.

### `core.research_agent`

The agent id an **assisted** playbook step delegates its bulk reads to. Default `booping:booping-researcher`. It sits directly under `core` because more than one playbook reads it (groom's two research steps, retro's mining pass, code-review's blast-radius read).

### `core.plans.glob`

The plan shape, as data rather than hidden engine logic: an ordered list of vault-relative glob patterns, defaulting to the single entry `plans/*/index.md`. A vault laid out differently edits this one key. It is also the fallback that every [query spec](#query-specs) without its own `glob` inherits.

### `core.macros`

Shell-outs a rendered body may call by dotted path. Each value is an **argv list** (never a shell string), run with `shell=False`:

```yaml
core:
  macros:
    date: ["date"]
    branch: ["git", "rev-parse", "--abbrev-ref", "HEAD"]
```

A body calls one with `{{ macro('core.macros.date', '+%H:%M') }}`. The declared list is a **prefix** — positional arguments at the call site are appended, so `["date"]` and `["date", "+%Y%m%d"]` are the same shape. stdout is stripped and cached per argv tuple for the process, so a macro must be idempotent within one render, and two argument variants are two separate runs.

Macros are honoured in every tier, project included. A project config arrives with a `git clone`, so treat an unfamiliar vault's `core.macros` block the way you would treat any other executable content in a repo.

## Per-playbook keys, under `core.{name}_playbook`

Each shipped playbook owns one block. What can be in it:

### `core.{name}_playbook.agents`

Delegation guidance rendered into that playbook's "Available Agents" table, via the shared `playbooks/_partials/playbook_agents.md` partial. Each agent entry has `good_for` (a list of bullets describing when to delegate) and an optional `bad_for` (when not to). Currently populated for `groom`, `develop`, `retro`, and `code-review`.

- **`core.{name}_playbook.agents.<id>.internal`** — `true` on booping's built-in workers (`booping-developer`, `booping-researcher`). Marks an entry as plugin-owned so it can be hidden when the block opts out of built-ins (see below). Self-contained global agents you register omit this flag.
- **`core.{name}_playbook.disable_internal_agents`** — when set, every `internal: true` entry is hidden from that table, leaving only the agents you explicitly registered. See [integrating external agents](integrating-external-agents.md).

### `core.{name}_playbook.status`

The single status this playbook claims from or reads — only `retro` declares one today, `done` (the plan status develop ends at, narrowed by a null `retro:` in the query beside it). It is a **query key**, not a lifecycle definition: point it at a different status and the playbook's picker pulls from another queue. The transitions themselves live in the playbook's `states:` block (see below).

### `core.{name}_playbook.queries.<id>`

A [query spec](#query-specs), living beside the body that renders it.

### `core.{name}_playbook.git`

Develop-only: `commit_message` (the conventional-commit format string used for in-sprint commits) and `branches`, a list of `{branch, when}` entries. `branch` is the literal prefix (e.g. `feat/`, `fix/`); `when` is a list of short matches against the plan `type` (`feature`, `bug`, `refactoring`) or freeform descriptors. The develop playbook's `provision` step walks this list to pick the sprint branch prefix.

### `core.groom_playbook.cross_review_agent`

The agent that performs the detached second-model review of a drafted plan. **Default `null`**, so the reviewing step renders as skipped until a global or project config names an agent.

## Where the plan lifecycle lives

Statuses, transitions, gates and hooks are **not** in this config. Each playbook declares its own vocabulary in its `states:` block in `playbooks/<name>/playbook.yaml`, and `booping playbook-transition` is the only thing that writes a plan's `status:`. See [Playbooks → Run state](playbook.md#run-state) for the machine format, and [Vault → `plans/`](vault.md#plans) for how the four shipped playbooks chain their vocabularies through one plan.

To reshape a status flow, edit that playbook's `states:` — or fork the playbook under a new name. There is no config key that overrides it.

## Query specs

A **query spec** is any mapping in the merged config, addressed by its dotted path. The value at the path *is* the spec — no wrapper key:

```bash
bin/booping query --config core.retro_playbook.queries.candidates
```

and in a template, `{{ 'core.retro_playbook.queries.candidates' | query }}`.

Every key is optional:

| Key | Meaning |
|---|---|
| `glob` | Ordered vault-relative patterns; the first to claim a slug wins. Omitted → `core.plans.glob`. |
| `root` | What the globs resolve against. Omitted → the vault; `core` → the plugin root, for content the plugin itself ships (so the spec resolves outside any project). |
| `where` | Clause → value; the clause key carries the operator as a suffix (below). |
| `sort` | Frontmatter field name, `-` prefixed for descending. Valueless rows come last. Omitted → slug order. |
| `columns` | Projection, declared order preserved. `path` and `slug` are always present. |

Any other key is an error naming the legal set, so a typo is caught rather than silently ignored.

`where` and `--where` share one fixed operator vocabulary — not an expression language:

| Clause | Meaning |
|---|---|
| `k=v` | equals |
| `k!=v` | does not equal |
| `k:in=a,b` | is one of |
| `k:gt=n` | greater than `n`, numerically |
| `k:lt=n` | less than `n`, numerically |

Clauses are repeatable and all of them apply. A row whose frontmatter lacks the field fails every operator, and so does a value that will not read as a number under `:gt` / `:lt`. Inline arguments (`--where` on the CLI, `query(where={...})` in a template) deep-merge over a resolved spec for that call only.

A spec lives beside its consumer, never in a central registry. The one shipped spec that isn't about plans is `core.migrate_playbook.queries.pending`, which declares `root: core` and lists the migrations the plugin itself ships.

## Scaffold trees

Any mapping in the config can describe a **file/dir tree** that `bin/booping scaffold` materialises on disk:

```
bin/booping scaffold <config-path> <dest> [--force] [--set KEY=VALUE]...
```

`<config-path>` is a dotted path into the merged config — the value there *is* the destination directory's contents, with no wrapper key. `<dest>` is created with its parents when missing; a non-empty destination aborts unless you pass `--force`, which overwrites only the files the tree names and never deletes a directory. Exit 0 on success, 1 on a user error (unknown path, malformed tree, non-empty destination without `--force`, bad `--set`, Jinja error in seed content), 2 if a write fails at the OS level. The whole tree is rendered in memory first, so an error leaves the filesystem untouched.

How a node is read:

| Config value | Meaning |
|---|---|
| string | File; the string is its content |
| mapping without `type` | Directory; each key is a child's name |
| `{type: file}` | File; optional `content` (absent → empty file) |
| `{type: dir}` | Directory; optional `children` (absent → empty dir) |
| `null` | Error — write `""` for an empty file, `{}` for an empty dir |
| list, number, bool | Error, reported against the node's dotted path |

`type` is reserved: a mapping carrying it is an explicit node descriptor, never a directory named `type`. A filename containing `/`, or equal to `.` or `..`, is rejected before anything is written.

File content is Jinja-rendered, so `{{ config.… }}` and `{{ context.… }}` resolve. **`--set` here binds a bare variable** — `--set name=x` fills `{{ name }}` — unlike `booping render` and `booping render-playbook`, where `--set` merges into the config and you write `{{ config.name }}`.

Trees ride the same core → global → project merge as everything else on this page, so a global or project config can add its own tree or override one leaf of a shipped one. Two ship:

- **`core.playbook_authoring_playbook.scaffold`** — a playbook skeleton: `playbook.md` (identity frontmatter carrying the name you passed, plus a preamble stub), `playbook.yaml` (an empty `graph:`), and an empty `_references/`.

  ```
  bin/booping scaffold core.playbook_authoring_playbook.scaffold \
    ~/Claude/_playbooks/my-playbook --set name=my-playbook
  ```

- **`core.setup_playbook.scaffold`** — the project vault: `plans/`, `retrospectives/`, `_lessons/`, `notes/`, plus the seeded `sprints.md` Obsidian Bases fence and a `.gitignore`. Takes no `--set` variables.

## Plan frontmatter: `summary`

Each plan file carries a `summary` field in its YAML frontmatter — a one-line statement of the plan's intent (≤ ~120 characters). Groom writes it when drafting the plan; it is the human-readable label that surfaces in `sprints.md` and makes plans searchable across the vault.

## The global tier

Machine-wide defaults live at `${XDG_CONFIG_HOME:-~/.config}/booping/config.yaml` (typically `~/.config/booping/config.yaml`; `XDG_CONFIG_HOME` is honoured when set). It deep-merges over the plugin's `src/config.yaml` and is in turn overridden by the per-project file — the full order is **core → global → project**. Any key valid in `src/config.yaml` is valid here; the merge rules are identical (dict keys merge, list keys replace wholesale).

The global tier's headline key is **`home_dir`** — the vault-home base under which per-project vaults are scaffolded and resolved (`<home_dir>/<project>/`). It is a raw string (`~` is expanded at vault-resolution time, e.g. `~/Claude/`).

- **Precedence.** A `.booping` marker carrying a `vault_path:` key still wins over `home_dir` — a repo-local vault is resolved directly from the marker, and `home_dir` is not consulted for it. `home_dir` only governs the default `<home_dir>/<project>/` layout.
- **Project-tier `home_dir` is a no-op.** By the time the project tier merges, the vault has already been resolved (its location is what tells booping where to read the project config from). Setting `home_dir` in `~/Claude/{project}/config.yaml` therefore has no effect — put it in the global tier.
- **First-run seeding.** `/playbook setup` settles `home_dir` before touching the project: if the global config file is absent it asks for the vault-home base (default `~/Claude`) and writes it there, then scaffolds the vault with `booping scaffold core.setup_playbook.scaffold <vault_dir>` and records the location in the repo's `.booping` marker.

Read any resolved value — merged across all three tiers — with `booping config-get <dotted.key>` (e.g. `booping config-get home_dir`). Note that `home_dir` prints its raw, unexpanded value.

## Overriding for one project

Drop a YAML file at `~/Claude/{project}/config.yaml` to override or extend the plugin's defaults for that project. The override file deep-merges over `src/config.yaml` at render time:

- **Dict keys merge.** A project key is added or replaces the plugin's value; sibling keys the project file does not mention fall through unchanged.
- **List keys replace wholesale.** If the project file sets `core.sprint.scale` or `core.develop_playbook.git.branches`, the project list replaces the plugin list entirely — there is no element-level merge.
- **`agents` is shallow-merged.** Each agent entry is atomic: an override that changes one field of an entry must restate the rest of that entry.
- **No rebuild required.** The merge happens at skill-load time, every time. Edit, save, run a skill — the new values are live.

The override takes effect at the next skill load. Nothing in `src/files/` or the build artefacts is touched.

### Example: tweak the SP threshold and add a branch convention

`~/Claude/{project}/config.yaml`:

```yaml
core:
  sprint:
    default_threshold_sp: 25  # smaller cap for this project's faster cadence

  develop_playbook:
    git:
      branches:               # list — replaces the plugin defaults wholesale
        - { branch: feat/,     when: [feature] }
        - { branch: fix/,      when: [bug] }
        - { branch: refactor/, when: [refactoring] }
        - { branch: docs/,     when: [docs, documentation] }   # new prefix
        - { branch: chore/,    when: [other, tooling] }
```

After the next render, groom proposes splitting at 25 SP instead of 35, and develop picks `docs/` for plans typed `docs`.

Because lists replace wholesale, the project file must include every branch entry it wants to keep — omitting a row removes it. Dict keys behave the opposite way: `core.sprint.default_threshold_sp: 25` does not affect `core.sprint.redecompose_threshold` or `core.sprint.scale`, which fall through from the plugin defaults.

### Example: config for a playbook you wrote

Nothing is validated, so a playbook of your own declares its namespace and reads it directly:

```yaml
core:
  ship_playbook:
    registry: ghcr.io/acme
    agents:
      release-bot:
        good_for:
          - "Cutting the tag and pushing the image once the checks are green"
```

The playbook's `jinja: true` bodies then read `{{ config.core.ship_playbook.registry }}` and render the delegation table with `{% set playbook_agents = config.core.ship_playbook %}{% include "_partials/playbook_agents.md" %}`. No plugin change is needed.

## Verifying the merged config

Run `bin/booping debug-context` from the project directory (the one with the `.booping` marker) to dump the assembled context — including the merged config — as YAML. This is the authoritative answer to "what value is the skill actually seeing?" For a single value, `bin/booping config-get <dotted.key>` prints just that key resolved across the core → global → project merge (scalars as raw text, mappings/lists as YAML), and works outside any project too (core + global only).
