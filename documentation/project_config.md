# Project config

booping reads a single structured config — `src/config.yaml` in the plugin — and deep-merges two override tiers over it at skill-load time: a **global** tier (`${XDG_CONFIG_HOME:-~/.config}/booping/config.yaml`) and a **project** tier (`~/Claude/{project}/config.yaml`). The merge order is **core → global → project**, later tiers winning.

## Shape: two top-level keys

The whole config lives under exactly two top-level keys:

- **`home_dir`** — the vault-home base. Top-level because it resolves *where the vault is*, before any namespace inside the config is reachable. See [The global tier](#the-global-tier).
- **`core`** — everything the shipped playbook set owns.

Inside `core` there is one placement rule:

| The key is… | It lives at… |
|---|---|
| owned by exactly one playbook | `core.{name}_playbook.…` |
| shared by the development loop or several playbooks | `core.…` directly |

`{name}` is the playbook's name with `-` replaced by `_` — `groom` → `core.groom_playbook`, `code-review` → `core.code_review_playbook`. The rule applies literally, including to the three scaffold trees.

**`core` is the worked example your own playbooks copy.** A playbook you write declares its own namespace the same way and reads it with `{{ config.core.my_playbook.… }}` (or `{{ config.my_namespace.… }}` to sit outside `core` entirely). The placement rule travels with the copy: a key only your playbook reads sits in its `core.{name}_playbook` block; a key several of your playbooks share sits directly under `core`.

!!! note "Nothing is validated"
    There is no schema gate, no unknown-field warning, and no key restricted to a particular tier. A config declaring an invented `core.my_playbook.whatever` block loads unchanged from any tier, and a project-tier `core.macros` entry is as first-class as a shipped one — it resolves at render time like the rest of the merge. Override a `core.*` key the plugin ships and getting it right is yours.

## Snapshot: `src/config.yaml`

Current plugin defaults, comments trimmed and the per-agent guidance bullets abridged. Source of truth: [`src/config.yaml`](https://github.com/A/claude-booping/blob/master/src/config.yaml) (this snapshot may lag).

<details>
<summary>Show full config</summary>

```yaml
home_dir: ~/Claude/

core:
  research_agent: "booping:booping-researcher"

  macros:
    date: ["date"]
    git_commit:
      command: ["git", "rev-parse", "HEAD"]
      cwd: repo

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
          status:in: [ready-for-dev, in-progress, awaiting-retro, awaiting-learning, done, fail, cancelled]
        sort: "-created"
        columns: [status, title, summary, active_minutes, models]

  develop_playbook:
    git:
      commit_message: '<agent>: <plan title> <message>'
      branches:
        - { branch: feat/,     when: [feature] }
        - { branch: fix/,      when: [bug] }
        - { branch: refactor/, when: [refactoring] }
        - { branch: chore/,    when: ["anything not matching a task type", "tooling, dependency bumps, formatting"] }
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
      codereviews: { type: dir }
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
- **`core.sprint.scale`** — the 1–5 SP definitions rendered into groom's body. Each entry is `{sp, meaning}`. Replace wholesale to redefine the scale — lists merge by replacement.

### `core.task_types`

The task-type taxonomy groom classifies every request against. Each entry is `{type, description, doc_uri}`; `doc_uri` lazy-loads that type's guidance during grooming. A new task type needs both an entry here and the corresponding doc under `docs/`.

### `core.research_agent`

The agent id an **assisted** playbook step delegates its bulk reads to. Default `booping:booping-researcher`. Point it at any agent id — a shipped worker or an external agent you registered — and every assisted step's delegated reads route there; nothing else about the steps changes. It sits directly under `core` because more than one playbook reads it (groom's two research steps, retro's session-log mining and issue research).

### `core.plans.glob`

The plan shape as data: an ordered list of vault-relative glob patterns, defaulting to the single entry `plans/*/index.md`. All plan discovery goes through this list — patterns are tried in order and the first to claim a slug wins, so a vault carrying more than one plan shape lists them all and order decides ties. A vault laid out differently edits this one key. It is also the fallback that every [query spec](#query-specs) without its own `glob` inherits.

### `core.macros`

Shell-outs a rendered body may call by dotted path. Each entry is an **argv list**, never a shell string, run with `shell=False` — either the bare list, or a mapping carrying it under `command:` plus an optional `cwd:` of `repo` or `vault`: the attached repo or the Project Vault. Omit `cwd:` and the command runs in the process's own working directory.

```yaml
core:
  macros:
    date: ["date"]
    branch:
      command: ["git", "rev-parse", "--abbrev-ref", "HEAD"]
      cwd: repo
```

A body calls one with `{{ macro('core.macros.date', '+%H:%M') }}`. The `command:` list is a **prefix** — positional arguments at the call site are appended, so `["date"]` and `["date", "+%Y%m%d"]` are the same shape. stdout is stripped and cached per argv tuple and resolved `cwd` for the process, so a macro must be idempotent within one render, and two argument variants are two separate runs.

For a reproducible render, pin a macro instead of executing it: `--stub-macro DOTTED.PATH=LITERAL` on `booping render`, `booping render-playbook` and `booping scaffold` makes the named macro return the literal without running its command (e.g. `--stub-macro core.macros.date=19700101-00-00`). The flag is repeatable, later pins winning.

Macros are honoured in every tier, project included — a project-tier entry resolves at render time exactly like a shipped one. A project config arrives with a `git clone`, so treat an unfamiliar vault's `core.macros` block the way you would treat any other executable content in a repo.

## Per-playbook keys, under `core.{name}_playbook`

Each shipped playbook owns one block:

### `core.{name}_playbook.agents`

Delegation guidance rendered into that playbook's "Available Agents" table via the shared `playbooks/_partials/playbook_agents.md` partial. Each entry has `good_for` (bullets describing when to delegate) and an optional `bad_for` (when not to). Populated for `groom`, `develop`, `retro`, and `code-review`.

- **`core.{name}_playbook.agents.<id>.internal`** — `true` on booping's built-in workers (`booping-developer`, `booping-researcher`), marking an entry plugin-owned so it can be hidden when the block opts out of built-ins. Self-contained global agents you register omit this flag.
- **`core.{name}_playbook.disable_internal_agents`** — when set, every `internal: true` entry is hidden from that table, leaving only the agents you explicitly registered. See [integrating external agents](integrating-external-agents.md).

### `core.{name}_playbook.status`

The single status this playbook claims from or reads — only `retro` declares one today, `done` (the plan status develop ends at, narrowed by a null `retro:` in the query beside it). It is a **query key**, not a lifecycle definition: point it at a different status and the playbook's picker pulls from another queue. The transitions live in the playbook's `states:` block.

### `core.{name}_playbook.queries.<id>`

A [query spec](#query-specs), living beside the body that renders it.

### `core.{name}_playbook.git`

Develop-only: `commit_message` (the conventional-commit format string for in-sprint commits) and `branches`, a list of `{branch, when}` entries. `branch` is the literal prefix (e.g. `feat/`, `fix/`); `when` is a list of short matches against the plan `type` (`feature`, `bug`, `refactoring`) or freeform descriptors. Develop's `provision` step walks the list to pick the sprint branch prefix.

### `core.groom_playbook.cross_review_agent`

The agent that performs the detached second-model review of a drafted plan. **Default `null`**, so the reviewing step renders as skipped until a global or project config names an agent.

## Where the plan lifecycle lives

Statuses, transitions, gates and hooks are **not** in this config. Each playbook declares its own vocabulary in its `states:` block in `playbooks/<name>/playbook.yaml`, and `booping playbook-transition` is the only thing that writes a plan's `status:`. See [Playbooks → Run state](playbook.md#run-state) for the machine format, and [Vault → `plans/`](vault.md#plans) for how the four shipped playbooks chain their vocabularies through one plan.

To reshape a status flow, edit that playbook's `states:` — or fork the playbook under a new name. No config key overrides it.

## Query specs

A **query spec** is any mapping in the merged config, addressed by its dotted path. The value at the path *is* the spec — no wrapper key:

```bash
bin/booping query --config core.retro_playbook.queries.candidates
```

In a template, `{{ 'core.retro_playbook.queries.candidates' | query }}` yields the rows; the sibling `as_table` filter lays a result out as a markdown table.

Every key is optional:

| Key | Meaning |
|---|---|
| `glob` | Ordered vault-relative patterns; the first to claim a slug wins. Omitted → `core.plans.glob`. |
| `root` | What the globs resolve against. Omitted → the vault; `core` → the plugin root, for content the plugin itself ships (so the spec resolves outside any project). |
| `where` | Clause → value; the clause key carries the operator as a suffix (below). |
| `sort` | Frontmatter field name, `-` prefixed for descending. Valueless rows come last. Omitted → slug order. |
| `columns` | Projection, declared order preserved. `path` and `slug` are always present. |

Any other key is a validation error naming the offending key, so a typo is caught rather than silently ignored.

`where` and `--where` share one fixed operator vocabulary — not an expression language:

| Clause | Meaning |
|---|---|
| `k=v` | equals |
| `k!=v` | does not equal |
| `k:in=a,b` | is one of |
| `k:gt=n` | greater than `n`, numerically |
| `k:lt=n` | less than `n`, numerically |

Clauses are repeatable and all of them apply. A row whose frontmatter lacks the field fails every operator, and so does a value that will not read as a number under `:gt` / `:lt`. Inline arguments (`--where` on the CLI, `query(where={...})` in a template) deep-merge over a resolved spec for that call only.

The CLI mirrors every spec key inline: `--where` (repeatable), `--sort FIELD`, and `--columns A,B` override the resolved spec for that call; `--glob PATTERN` (repeatable and ordered, mutually exclusive with `--config`) queries ad hoc without any spec; `--output` picks the format — `table` (the default), `json`, `yaml`, or `paths`.

A spec lives beside its consumer, never in a central registry. Most shipped specs read the vault's plans; `core.learn_playbook.queries.candidates` overrides `glob` to read `retrospectives/*.md` instead, and `core.migrate_playbook.queries.pending` is the one that reads outside the vault entirely — it declares `root: core` and lists the migrations the plugin itself ships.

## Scaffold trees

Any mapping in the merged config — addressed by its dotted path, like a query spec — can describe a **file/dir tree** that `bin/booping scaffold` materialises on disk:

```
bin/booping scaffold <config-path> <dest> [--force] [--set KEY=VALUE]... [--stub-macro DOTTED.PATH=LITERAL]...
```

`<config-path>` is a dotted path into the merged config — the value there *is* the destination directory's contents, no wrapper key. `<dest>` is created with its parents when missing, and a destination that already holds some of the tree's files is fine: **a file that exists is skipped**, reported as `skipped existing file {path}` and left byte-for-byte alone. `--force` turns that skip into an overwrite of the files the tree names; it never deletes a directory and never touches a path the tree does not name. Exit 0 on success, 1 on a user error (unknown path, malformed tree, bad `--set`, Jinja error in seed content), 2 if a write fails at the OS level. The whole tree is rendered in memory first, so an error leaves the filesystem untouched.

**Stdout contract.** For every file the run actually wrote, scaffold prints a unified diff — `--- /dev/null` (a new file) or `--- {path}` (an overwrite), then `+++ {path}` and the hunks. A file whose rendered content matches what is already on disk, and a file skipped because it exists, produce no diff; created directories keep their one-line `created dir {path}` report, and the run still ends with the `scaffolded N paths — …` count line. `booping frontmatter-update` shares this contract: the diff of the change it made on stdout, nothing at all when the file did not change, its `updated {path}: {keys}` summary and any errors on stderr. Its arguments, flags and exit codes are unchanged; it writes scalars with their YAML type, so ints, floats, booleans and `null` land unquoted and everything else lands as a string.

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

Trees ride the same core → global → project merge as everything else here, so a global or project config can add its own tree or override one leaf of a shipped one. Three ship:

- **`core.playbook_authoring_playbook.scaffold`** — a playbook skeleton: `playbook.md` (identity frontmatter carrying the name you passed, plus a preamble stub), `playbook.yaml` (an empty `graph:`), and an empty `_references/`.

  ```
  bin/booping scaffold core.playbook_authoring_playbook.scaffold \
    ~/Claude/_playbooks/my-playbook --set name=my-playbook
  ```

- **`core.setup_playbook.scaffold`** — the project vault: `plans/`, `retrospectives/`, `codereviews/`, `_lessons/`, `notes/`, plus the seeded `sprints.md` Obsidian Bases fence and a `.gitignore`. Takes no `--set` variables.

- **`core.groom_playbook.scaffold`** — one plan directory: `index.md` seeded with the plan's identity frontmatter (the sole definition of that frontmatter) plus the title as an `#` heading, and an empty `request.md`. Takes `--set title=` and `--set type=`.

  ```
  bin/booping scaffold core.groom_playbook.scaffold \
    ~/Claude/my-project/plans/202608091310_my-plan \
    --set title="My plan" --set type=feature
  ```

## Review templates

The code-review playbook picks its review template by name, and the template set layers across the same three levels as the config itself: the plugin ships a core set, the global level adds machine-wide templates at `<home_dir>/review_templates/`, and the Project Vault's `review_templates/` speaks for one project. Later levels override by name — a global or project template file named like a shipped one replaces it; a new name adds a template to the set.

## Plan frontmatter: `summary`

Each plan file carries a `summary` field in its YAML frontmatter — a one-line statement of the plan's intent (≤ ~120 characters). Groom writes it when drafting the plan; it is the label that surfaces in `sprints.md` and makes plans searchable across the vault.

## The global tier

Machine-wide defaults live at `${XDG_CONFIG_HOME:-~/.config}/booping/config.yaml` (typically `~/.config/booping/config.yaml`; `XDG_CONFIG_HOME` is honoured when set). It deep-merges over the plugin's `src/config.yaml` and is in turn overridden by the per-project file — **core → global → project**. Any key valid in `src/config.yaml` is valid here; the merge rules are identical (dict keys merge, list keys replace wholesale).

The global tier's headline key is **`home_dir`** — the vault-home base under which per-project vaults are scaffolded and resolved (`<home_dir>/<project>/`). It is a raw string (`~` is expanded at vault-resolution time, e.g. `~/Claude/`).

- **Precedence.** A `.booping` marker carrying a `vault_path:` key wins over `home_dir` — a repo-local vault is resolved directly from the marker. `home_dir` only governs the default `<home_dir>/<project>/` layout.
- **Project-tier `home_dir` is a no-op.** By the time the project tier merges, the vault has already been resolved — its location is what tells booping where to read the project config from. Set `home_dir` in the global tier.
- **First-run seeding.** `/playbook setup` settles `home_dir` before touching the project: if the global config file is absent it asks for the vault-home base (default `~/Claude`) and writes it there, then scaffolds the vault with `booping scaffold core.setup_playbook.scaffold <vault_dir>` and records the location in the repo's `.booping` marker.

Read any resolved value — merged across all three tiers — with `booping config-get <dotted.key>` (e.g. `booping config-get home_dir`). `home_dir` prints its raw, unexpanded value.

## Overriding for one project

Drop a YAML file at `~/Claude/{project}/config.yaml` to override or extend the plugin's defaults for that project. It deep-merges over `src/config.yaml` at render time:

- **Dict keys merge.** A project key is added or replaces the plugin's value; sibling keys the project file does not mention fall through unchanged.
- **List keys replace wholesale.** Set `core.sprint.scale` or `core.develop_playbook.git.branches` and the project list replaces the plugin list entirely — there is no element-level merge.
- **`agents` is shallow-merged.** Each agent entry is atomic: an override changing one field of an entry must restate the rest of that entry.
- **No rebuild required.** The merge happens at skill-load time, every time. Edit, save, run a skill — the new values are live.

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

Nothing is validated, so your own playbook declares its namespace and reads it directly:

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

Run `bin/booping debug-context` from the project directory (the one with the `.booping` marker) to dump the assembled context — including the merged config — as YAML: the authoritative answer to what a skill is actually seeing. For a single value, `bin/booping config-get <dotted.key>` prints that key resolved across the core → global → project merge (scalars as raw text, mappings/lists as YAML), and works outside any project too (core + global only).
