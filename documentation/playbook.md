# Playbooks

A **playbook** is a multi-step guided procedure driven by the `/playbook` skill — the one skill booping ships. Where a skill is a fixed workflow, a playbook is yours to write: prompt steps, each optionally detached into a sub-agent, with review gates that pause for inspection. Most live in your Project Vault; a few ship with the plugin (see [Levels](#levels)).

A playbook's **structure** lives in `playbook.yaml`: the `graph:` (which steps run, in what order, which in parallel) and the optional `states:` (named state machines that persist run state on disk so a run can be resumed). `playbook.md` keeps **identity and prose** — the manifest frontmatter (`name`, `title`, `summary`, `trigger`, …) and the preamble body. Bodies are plain markdown by default; a playbook can opt into [Jinja rendering](#jinja-bodies) for live project data. Author one by hand and it shows up in `/playbook` immediately.

!!! note "Legacy: `graph:` in `playbook.md` frontmatter"
    A playbook with no `playbook.yaml` still works: `graph:` is read from `playbook.md` frontmatter. Declaring `graph:` in **both** places is a blocking STOP — keep exactly one. `state:` / `states:` are `playbook.yaml`-only; there is no frontmatter fallback.

## Levels

Playbooks are discovered from the core, global and project levels:

- **Core** — `<plugin-root>/playbooks/<name>/`. Shipped with the plugin.
- **Global** — `<home_dir>/_playbooks/<name>/` (default `~/Claude/_playbooks/`). Shared across every project on the machine.
- **Project** — `{vault}/_playbooks/<name>/`. Specific to one Project Vault.

**A playbook `name` must be unique across levels.** The same name at two levels is a name clash: `/playbook` marks the entry `⚠ clash` in its listing, and rendering the playbook returns a blocking STOP notice instead of the procedure — neither copy runs until one of them is renamed. To adapt a playbook you didn't write, copy it under a new name or attach [lessons](#lessons) to it. Directories whose name starts with `_` (e.g. `_lib`, `_partials`) are skipped, so shared helper content can sit alongside playbooks.

### Shipped playbooks

Core playbooks own the main workflow:

- **`setup`** — machine config, then vault scaffold and `.booping` marker. See [Install](install.md).
- **`groom`** — spec a sprint (intake → codebase and web research → draft → cross-review → present). See [groom](groom.md).
- **`develop`** — execute a plan (intake → provision → develop-loop → verify → wrap-up). See [develop](develop.md).
- **`retro`** — capture what shipped versus the spec. See [retro](retro.md).
- **`learn`** — fold retro findings into durable rules. See [learn](learn.md).
- **`code-review`** — review a confirmed scope: findings, verdict, approved fixes, recorded in the run's own `codereviews/` artifact. See [code-review](code_review.md).
- **`migrate`** — bring a vault up to the plugin's current migration watermark.
- **`playbook-authoring`** — the procedure for writing a new playbook.

Run any of them with `/playbook <name>`. A playbook of your own sharing a core name clashes with it rather than replaces it.

## Layout

Each playbook is a directory:

```
<name>/
  playbook.md          # identity frontmatter + plain-markdown preamble body
  playbook.yaml        # structure: graph:, state:, states:
  <step>/              # one directory per step — the directory name IS the step name
    prompt.md          #   the step itself; everything else in the dir is yours
  _scripts/            # executables invoked by `script <name>` transition hooks
  _references/         # `_`-prefixed dirs are not steps — free workspace
```

**Every non-`_` subdirectory holding a `prompt.md` is a step**, and its directory name is the step name the graph references. Nothing else in the directory is loaded — sibling files (fixtures, test configs, prompt variants like `base.md`) are invisible to the runner. A non-`_` subdirectory without a `prompt.md` is skipped with a warning.

Directory order on disk is irrelevant — **the `graph:` decides which steps run and in what order**. `_`-prefixed directories (`_references/`, `_fixtures/`) are never steps, so disabled steps and shared material can sit alongside without being wired in.

## Lessons

A **lesson** is a short standing rule injected into a playbook run — the way to correct a procedure without editing its prompts. Lessons are markdown files (the convention is `NNNN_title.md`), loaded in filename order from exactly **two** directories:

| Level | Directory | Reaches |
| --- | --- | --- |
| Global | `<home_dir>/_lessons/` (default `~/Claude/_lessons/`) | every project on the machine |
| Project | `{vault}/_lessons/` | this project only |

Neither directory decides *what* a lesson binds — the file's own `targets:` frontmatter does. A lesson with no usable `targets:` is injected nowhere: **lessons are opt-in.**

```markdown
---
title: Name every artifact path absolutely
targets:
  - groom
  - ship/publish
  - agent:booping-developer
---

Receipts must name paths absolutely — a relative path is ambiguous once the run moves between workdirs.
```

- `title` — *optional*, used in the lesson's heading; defaults to the filename without its extension.
- `targets` — the list of things this lesson is injected into. A bare scalar (`targets: groom`) counts as a one-entry list.

### Target forms

Exact names only — no globs, no wildcards, no negation:

| Form | Example | Injected into |
| --- | --- | --- |
| `{playbook}` | `groom` | the `## Lessons` section of that playbook's composed procedure |
| `{playbook}/{step}` | `ship/publish` | that one step's prompt, on both the `--step` and inline surfaces |
| `agent:{id}` | `agent:booping-developer` | that agent's body, at agent load time |
| `skill:{name}` | `skill:playbook` | that skill's body, at skill load time |

A lesson may carry several entries, of mixed forms. An entry matching none of these forms is ignored (see [Notices](#notices)).

Injection happens in `booping render-playbook` itself — there is no lessons partial to include, and a playbook cannot opt out.

!!! warning "Agent targets reach booping's own agents only"
    `agent:` targets are injected into the plugin's internal agents — `agent:booping-developer` and `agent:booping-researcher`. An [external or global agent](integrating-external-agents.md) at `~/.claude/agents/<id>.md`, and a sub-agent spawned by model tier (`detached: sonnet:high`), receive **no** targeted lessons: their bodies are not rendered by booping. To reach one of those, target the step it performs (`{playbook}/{step}`) — the step prompt is fetched by the agent itself.

**Same filename in both directories → the project copy wins.** A `0002_receipts.md` present in `~/Claude/_lessons/` and in `{vault}/_lessons/` loads once, from the vault. Give lessons distinct names unless you mean to shadow one.

**Where they surface.** Playbook-targeted lessons render as a `## Lessons` section in the composed procedure, between the preamble and `## Playbook Steps`; they bind the driver for the whole run. Step-targeted lessons are appended to that step's `booping render-playbook <name> --step <step>` output, so they reach exactly the agent running that step (and the embedded body when the playbook renders steps inline). `agent:{id}` and `skill:{name}` lessons render inside the named agent's or skill's body when it loads — `skill:playbook` shapes the `/playbook` skill itself. `--no-lessons` suppresses both sections *and* the lesson notices, so the output matches a lesson-free vault byte for byte.

!!! note "Retired: playbook-local `_lessons/` and `step:`"
    A `_lessons/` directory inside a discovery root or inside a playbook directory is not read, and neither is a lesson's `step:` frontmatter key. Move those files into `{vault}/_lessons/` (or `<home_dir>/_lessons/`) and express `step: draft` as `targets: [<playbook>/draft]`. While a retired directory still holds markdown, every render of that playbook emits a non-blocking migration note naming it.

## The manifest

### `playbook.yaml`

- `graph` — mapping of **node name → node**. A node whose value is a **list** is a plain step and the list is its dependency step names; a node whose value is a **mapping** is a [subgraph](#subgraphs). This is the whole structure: membership (only mapped steps run), order (a step runs after all its dependencies), and parallelism (steps whose dependencies are all satisfied by earlier waves run together).
- `state` — *optional*, the name of the `states:` entry that governs the **outer** graph.
- `states` — *optional*, mapping of state-machine name → machine. See [Run state](#run-state).

A subgraph node may carry its own `state:` key, naming the machine that governs each of its instances.

### `playbook.md` frontmatter

- `name` — identifier, unique across the core, global and project levels (a duplicate is a blocking name clash).
- `title` — human-readable name.
- `summary` — one-line description shown in the `/playbook` listing.
- `trigger` — natural-language hint the skill matches the user's request against.
- `requires_project` — *optional*, default `false`. When `true`, the playbook only runs with a booping project attached: `/playbook` flags it in the listing and refuses to run it without a project, and `booping render-playbook` refuses to render it (stderr + exit 1).
- `jinja` — *optional*, default `false`. When `true`, the preamble and every step body are rendered as Jinja templates against live project context. See [Jinja bodies](#jinja-bodies).
- `inline_steps` — *optional*, default `false`. When `true`, each runner-performed step's body is embedded in its section of the composed procedure instead of the fetch command. Detached steps are unaffected. See [How the graph renders](#how-the-graph-renders).
- `graph` — *legacy fallback only*, same shape as `playbook.yaml`'s `graph:`. Used when the playbook has no `playbook.yaml`.

The manifest **body** is a preamble — a playbook-level instruction inserted above the rendered procedure. No step calls: the graph, not the body, decides what runs.

`<step>/prompt.md` frontmatter (the step identifier comes from the directory name, not frontmatter):

- `summary` — one-line description of the step, rendered into the step's section as a `Summary:` instruction bullet. It is where a step declares execution hints in its own domain words — e.g. *"Can be paralleled as one agent per feature"*.
- `detached` — *optional*. Present → the step runs inside a sub-agent; absent → the runner performs it. See [Delegation levels](#delegation-levels).
- `review_gate` — when non-null, `/playbook` stops after the step, presents the output, and continues only on your explicit confirmation. `null` runs straight through.
- `title` — *optional* human-readable heading for the step. When absent, the rendered heading is the titleized directory name (e.g. `current-time` → `Current Time`).

The step **body** is the prompt for that step.

```yaml
---
summary: Draft the plan against the approved design
detached: sonnet:high
review_gate: Plan draft ready — approve before presenting?
---
```

## Delegation levels

A step runs at one of three levels. Only the third has mechanics; the first two are the same runtime shape and differ in what the step body asks for.

- **inline** — the runner fetches the step body and performs the step itself, in the driving conversation. Everything the step reads lands in the driver's context. No frontmatter key.
- **assisted** — the runner still performs the step, but delegates the heavy reads or research inside it to the configured researcher agent, which returns a compressed summary. The driver's context holds the summary, not the sources. Expressed as prose in the step body — no frontmatter key. The spawn's agent id comes back with the summary, so a follow-up goes to that same agent by id — its context, the sources already read, intact — rather than a fresh spawn re-reading everything.
- **detached** — an agent fetches and performs the whole step body; the runner sees only the returned receipt. This is the only level with mechanics: the `detached:` frontmatter key.

The researcher an assisted step delegates to is the `core.research_agent` config key (core default `booping:booping-researcher`), overridable per project. A `jinja: true` body reads it as `{{ config.core.research_agent }}`; an optional key is read defensively with `{% if config.core.get("my_key") %}`.

### The `detached` grammar

- **key absent** — not detached: the runner performs the step (inline or assisted). Such a step can never share a parallel wave (see below).
- `<model>:<effort>` where `model` ∈ `{opus, sonnet, haiku, fable}` (e.g. `sonnet:high`, `haiku:medium`) — spawn a **generic sub-agent** with that model and effort.
- any other non-null string — spawn a **named sub-agent** via `subagent_type=<value>`. The value is used verbatim, so colons are fine for namespaced agents (e.g. `booping:booping-researcher`, `general-purpose`).

There is no `null` value: `agent: null` is replaced by omitting the key. `agent:` is the **legacy name** of this key — a step still carrying it renders a blocking `**STOP — tell the user:**` notice telling you to rename it to `detached:`.

Under `jinja: true` the value is a template like any body, so the agent can come from config instead of being hard-coded:

```yaml
---
summary: Second-model review of the written plan
detached: "{{ config.core.groom_playbook.cross_review_agent or '' }}"
---
```

When the key it names is absent from the merged config the value renders empty and the step degrades to runner-performed rather than spawning an agent with no name — so a playbook can offer an optional reviewer, and let the preamble say to skip the step when none is configured.

## Jinja bodies

By default every body — the manifest preamble and each `prompt.md` — is passed through **verbatim**. Braces, `{{ }}`, and template-looking text are just text.

Set `jinja: true` in the manifest frontmatter to opt the **whole playbook** in (all-or-nothing — there is no per-step flag). Bodies — plus the `summary` and `detached` frontmatter fields of each step — are then rendered as Jinja templates with the same project context the built-in skills get: the attached project, its config, and the shared fragments the plugin ships. Include paths resolve through a chain — the body's own directory, then the playbook directory, then each discovery root (project, global, core), then the plugin's own template root — so a fragment shipped under `playbooks/_partials/` is reachable as `_partials/<file>` whatever level your playbook lives at:

```markdown
---
name: ship
title: Ship
summary: Prepare, check in parallel, then publish.
trigger: run the ship playbook
jinja: true
requires_project: true
---
# Ship

{% set playbook_agents = config.core.ship_playbook %}
{% include "_partials/playbook_agents.md" %}

{% include "_partials/_git_guide.j2" %}
```

- **Project context is required.** Rendering a `jinja: true` playbook without a project attached produces a blocking `STOP` notice instead of the procedure. Pair it with `requires_project: true`.
- **A template error is a blocking notice**, not a crash — the failure is reported in-band and the playbook refuses to run.

A Jinja body is meaningless until rendered — the `booping render-playbook <name> --step <step>` fetch every step body goes through returns it already rendered.

## How the graph renders

`/playbook` renders the graph as a **step table** — one row per step, in dependency order, carrying the step name, its dependencies, its summary and its review gate.

- **Step bodies are fetched, not embedded** — by default every section ends with the command that fetches the body, the same for plain and `jinja: true` playbooks. The procedure the driver holds is therefore proportional to the graph — step table plus per-step metadata, never bodies — and each body enters exactly one context, only when its step runs. A runner-performed step's section is a metadata block (summary, dependencies, review gate) closed by *Run `booping render-playbook <name> --step <step>` for content.* A **detached** step's section is instead one order to the driver — its summary as a paragraph, its review gate when it has one, then *Tell the `<agent>` agent to get its instructions by calling this command: `booping render-playbook <name> --step <step>`.* Its dependencies and wave order are omitted there; the step table already carries them.
- **`inline_steps` embeds the runner's bodies** — with `inline_steps: true` in the manifest (or `--inline-steps` on the command), a runner-performed step's section carries its rendered body, with that step's lessons already appended, in place of *both* the metadata block and the fetch command; its summary, dependencies and review gate stay in the step table. Detached steps keep fetch-form, so their agents still fetch their own body. A body that fails to render is a blocking `STOP` notice like any other.
- **Delegated steps fetch their own body** — the driver never runs the fetch command for a sub-agent step. It spawns the agent with a bootstrap prompt: the fetch command ("treat its stdout as your full instruction"), a `## Run-time context` block (project, plus `workdir` / `instance` where they apply), a `## Inputs` block assembled from the run-time context and prior steps' receipts, and a uniform `## Return` contract (`artifacts written + outcome, ≤ 5 lines`) — a richer contract belongs in the step body. A step without `detached:` is the only case where the driver runs the fetch itself and executes the stdout.
- **Steps that can run together must be `detached:`** — a step the runner performs itself can't run in parallel, so steps whose dependencies are satisfied at the same time must all be `detached:`.
- **Review gates pause after the batch** — once every step running together finishes, each one's gate is presented (labeled by step) and the run waits for your confirmation before the next batch.

## Subgraphs

A `graph:` node whose value is a **mapping** is a *subgraph*: a named group of steps with its own inner graph, optionally run more than once.

```yaml
graph:
  manifest: []
  pipeline:
    dependencies: [manifest]
    repeat: once per feature listed by manifest; instances may run in parallel
    graph:
      spec: []
      fixtures: [spec]
      tests: [spec]
  publish: [pipeline]
```

- `dependencies` — *required*, list of **outer** node names the subgraph waits for. Same role as a plain step's dependency list; the whole group joins a wave as one node.
- `graph` — *required*, non-empty mapping of **inner** step name → inner dependency names. Inner waves are resolved exactly like outer ones.
- `repeat` — *optional* prose. Its presence means the group runs once per instance the prose describes.
- `state` — *optional*, the name of the `states:` entry governing each instance of this subgraph. See [Run state](#run-state).

**Scope rule.** `dependencies` reference outer names only; inner dependencies reference inner names only. There is no cross-scope edge: an inner step cannot depend on an outer step, and an outer step depends on the subgraph as a whole. Step names are addressed flat and must be unique across the whole playbook — an inner step still lives in its own `<step>/prompt.md` directory at the playbook root.

**Repeat semantics.** `repeat` is prose, not a count — the driver reads it against the output of the steps in `dependencies` and decides how many instances to run. No `repeat` key means exactly one instance. Each instance walks the inner waves on its own — its own `--step` fetch per inner step, never a body reused across instances — and each inner step's `review_gate` fires per instance. Instances run in parallel only when **every** inner step is `detached:`; if any inner step is runner-performed, instances run one at a time.

**One level only.** A subgraph cannot contain another subgraph.

Subgraph-specific STOP conditions (on top of the usual [notices](#notices)):

- the node mapping has an unknown key, or is missing `dependencies` or `graph`;
- `dependencies` is not a list, `graph` is not a non-empty mapping, or `repeat` is not a string;
- an inner node's value is a mapping (nested subgraph);
- a step name appears in more than one scope.

In the rendered procedure the subgraph shows up as its own step-table row tagged `*(subgraph)*` (carrying its outer dependencies and its `repeat` prose), followed by its inner steps tagged `*(in <name>)*`, plus a `## Subgraph: <name>` intro section (`After:`, `Repeat:`, `Inner waves:`) and its inner step sections, each tagged `Part of: <name>`.

## Run state

Without `states:`, a run lives entirely in one conversation — close it and the run is gone. Declare `states:` and the run's progress is persisted in **artifacts on disk**, so a run can be inspected, resumed later, and advanced only through legal transitions.

A `states:` entry is a **named state machine**:

- `artifact` — *optional*, path to the markdown file holding this machine's status, **relative to the run workdir**. A `{instance}` placeholder makes the machine per-instance (one artifact per subgraph instance) and is only legal when some subgraph references the machine. A machine may declare no `artifact:` at all — useful when the file's path is only known at run time — and is then addressed exclusively with `--target` on every state command.
- `initial` — the status a freshly bootstrapped artifact starts in. Must be a key of `statuses`.
- `statuses` — mapping of status name → `{transitions: [...]}` or `{terminal: true}`. Each transition has `to`, and optionally `when` (the trigger prose the driver matches a step outcome against), `gates` (verifiable preconditions the driver judges before firing), and `hooks` (mechanical side effects the CLI runs).
- `superstates` — *optional*, mapping of group name → `{states: [...], transitions: [...]}`. Every status the group lists inherits its transitions, and a status's own edge to the same `to` wins over the inherited one. A group may also carry `on_exit` / `on_entry` hook lists, run when a transition crosses its boundary.

A machine is wired to a graph scope by a `state:` ref: the top-level `state:` governs the outer graph, a subgraph's `state:` governs each of its instances.

```yaml
state: main
graph:
  intake: []
  research-codebase: [intake]
  research-web: [intake]
  design: [research-codebase, research-web]
  step-pipeline:
    dependencies: [design]
    state: step
    repeat: once per item the design names
    graph:
      step-spec: []
      step-review: [step-spec]

states:
  main:
    artifact: index.md
    initial: intaking
    statuses:
      intaking:
        transitions:
          - to: researching
            when: intake step complete
            gates: ["request + scope captured in the artifact"]
            hooks:
              - frontmatter-update intaken="{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"
      researching:
        transitions:
          - to: developing-steps
            when: both research steps returned and design confirmed
            gates: ["research-codebase and research-web done, findings recorded"]
            hooks:
              - frontmatter-update researched="{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}" commit="{{ macro('core.macros.git_commit') }}"
              - script check-findings
      developing-steps:
        transitions:
          - to: done
            when: every step instance terminal
            gates: ["every steps/*/index.md status: done"]
            hooks:
              - frontmatter-update completed="{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"
      done: {terminal: true}
  step:
    artifact: steps/{instance}/index.md
    initial: spec-ing
    statuses:
      spec-ing:
        transitions:
          - to: reviewing
            when: spec written
            hooks:
              - frontmatter-update spec_done="{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"
      reviewing:
        transitions:
          - to: done
            when: user confirmed the spec
            gates: ["explicit user confirmation captured"]
            hooks:
              - frontmatter-update confirmed="{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"
      done: {terminal: true}
```

### Hooks

Two hook forms on a transition:

- `frontmatter-update [<file>] <key>=<val> ...` — set frontmatter keys on the artifact, or on `<file>` when a target is given. The hook form takes `key=val` pairs only, no flags.
- `script <name> [args...]` — run the executable named `<name>`, passing every token after it as argv.

The `booping frontmatter-update` **command** carries a flag the hook form does not: `--append <key>=<val>` appends the value to the **list** under `<key>` instead of setting it — a missing key is created as a one-entry list, a value the list already holds is not added again, and a key that already holds a scalar is an error. A `script` hook shelling out to it is how a history key such as `sessions:` grows across transitions without YAML editing.

A hook value is **Jinja-rendered with the `macro` global**, the same one rendered bodies call — a timestamp is `completed="{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"`, with the format at the call site. Because the clock goes through the macro system, a `macro_stubs:` mapping in the merged config pins it — the same config fragment `--stub-macro` merges on a render — so a transition is reproducible the way a render is. The hook string is tokenised with `shlex`, so quote any value carrying spaces. A value with no Jinja in it passes through untouched, and a macro or Jinja error aborts the transition (exit 2) with the offending value on stderr.

The repo's HEAD sha is likewise a macro, `core.macros.git_commit`, which carries `cwd: repo` so it resolves against the repo directory rather than the process cwd (the run workdir during a transition).

The optional `<file>` target is the first token after the hook name that carries no `=`. It resolves against the **run workdir** — the same anchor as the machine's `artifact` — and may carry `{instance}`, interpolated with the instance slug (legal only when an instance is in scope). The file must exist; a missing file is an error (exit 2) that aborts the transition — nothing is created. A file without a frontmatter block gets one prepended, the existing content becoming the body unchanged. In the mutation report a file-target update prints as `frontmatter <file>: k=v` instead of the plain `frontmatter: k=v`.

The status set itself is implicit — the CLI always writes `status: <to>` before running the transition's hooks.

### `_scripts/` contract

A `script <name>` hook runs an executable found by name:

- resolution probes `<playbook-dir>/_scripts/<name>` first, then `<root>/_scripts/<name>` at each level, most specific first — Project Vault, then global home, then the plugin's own `playbooks/`. The first hit wins; if none exists the transition fails (exit 2) with every probed path named. A script two playbooks share therefore lives once at the root level (`playbooks/_scripts/` for the shipped ones), and a playbook-local file of the same name shadows it;
- it must be executable, or the transition fails (exit 2) without mutating anything further;
- the hook line is tokenised with `shlex` and every token after the script name is passed through as argv, which is how one shared script serves several playbooks — `script close-working-set --verdicts --prefix retro --stage retrospectives` reaches the script as those three flags;
- it runs with the **run workdir** as its cwd;
- it receives `BOOPING_ARTIFACT` (absolute artifact path), `BOOPING_WORKDIR` (absolute run workdir) and `BOOPING_INSTANCE` (the instance slug, empty for a non-instance machine);
- a non-zero exit aborts the transition; the script's stderr is relayed.

!!! warning "A hook that mirrors outward should absorb its own failure"
    `status:` is written **before** the hooks run, so a script failing at hook time aborts the transition with the artifact already advanced. That is the right shape for a script guarding an invariant — the abort is the signal. It is the wrong shape for one pushing state to a system outside the vault: the failure would leave the vault ahead of that system with no way back. The shipped `tracker-sync` and `tracker-comment` scripts therefore report a failed push on stderr and exit 0, leaving re-running the push as the reconcile.

### Run workspace

A run gets its own workdir; artifact paths resolve against it and the playbook directory stays read-only source. A playbook's preamble names the workdir convention it wants — the plan-track playbooks make the plan's own directory the workdir, and the retro and code-review playbooks use the vault root. Absent one, `/playbook` falls back to:

```
{vault}/_runs/<playbook>/<run-slug>/
```

with `<run-slug>` = `{YYYYMMDD}-<kebab-topic>`. Every state command takes `--workdir <path>` (default: cwd).

### Commands

`booping playbook-state <playbook> [--target PATH] [--workdir PATH]` — read-only. Prints YAML: the playbook name, the resolved workdir, and per `states:` entry its `artifact`, its current `status` and the `next:` edges leaving it (each with `to` and, when declared, `when` / `gates`). A per-instance entry reports an `instances:` mapping keyed by slug, discovered by globbing the artifact path. `--target PATH` names the artifact outright (workdir-relative or absolute) instead of each machine's declared `artifact:`, and is required for a machine that declares none. An artifact that does not exist yet — or exists without a `status:` key, as a freshly written retrospective does — reports `status: not-started` with a single bootstrap edge to the machine's `initial`. Exits 1 for an unknown playbook, a missing workdir, a playbook with no `states:`, or a machine without `artifact:` and no `--target`.

`booping playbook-transition <playbook> <to> [--state NAME] [--target PATH] [--instance SLUG] [--workdir PATH]` — the only writer of run state. `--state` defaults to the outer graph's `state:` ref; `--instance` is required exactly when the artifact path carries `{instance}`; `--target PATH` names the artifact outright (workdir-relative or absolute), is mutually exclusive with `--instance`, and is required for a machine that declares no `artifact:`. With no `--workdir`, an **absolute** `--target` ending in the machine's declared `artifact:` implies the workdir — `--target {vault}/plans/x/index.md` on a machine declaring `artifact: index.md` runs hooks in `{vault}/plans/x`; a relative target, a non-matching absolute one, or a machine declaring no `artifact:` falls back to cwd. It reads the artifact's current status, checks that `<to>` is reachable from it, sets `status: <to>`, then runs the matched transition's hooks in order. A missing artifact — or one whose frontmatter has no `status:` key yet — is bootstrapped, legal only when `<to>` is the machine's `initial`; bootstrapping an existing file writes `status:` into its frontmatter, keeping the other keys intact. Re-running the same target is idempotent. It prints a **mutation report** (created/`from → to`/each frontmatter line/each script result) which is the authoritative record — the driver relays it and never re-reads the artifact to verify. Illegal transitions exit 1; hook failures exit 2.

### Resume

`/playbook` runs `booping playbook-state <name> --workdir <workdir>` on entry — first run and every resume — and restarts from the reported frontier: work already past its status is skipped, the first non-terminal status is re-entered, and `not-started` means bootstrap on the first transition. Nothing hand-edits an artifact's `status:` or a hook-written key; only `playbook-transition` mutates run state.

A resume does not need the run that started it. A run driven from outside a conversation — one invocation per turn, nothing to ask a question in — **parks** rather than blocks: it writes what it needs into a sidecar beside the artifact, transitions into a status that means *waiting*, and ends. The pattern is three pieces, all of them ordinary state machinery:

- a non-terminal **parking status**, reachable from each status a run may stop in and with one return edge back to each of them;
- a **`frontmatter-update` hook on every entering edge** stamping where to come back to (groom writes `return_to`), cleared again by the return edges. A hook value cannot be computed from the transition, so the mapping is one literal per edge — which also keeps the frontier report readable;
- a **sidecar** carrying the content, since frontmatter holds keys and not paragraphs. groom's is `clarifications.md`: one H2 per open question, answered in place, and postable to a tracker verbatim by a `script` hook.

The next invocation reads `playbook-state`, finds the parking status and the recorded return, reads the sidecar, and either takes the return edge or ends again untouched. Every step is a legal transition, so a parked run is indistinguishable from any other resume.

### Cancellation

A run does not have to reach its success terminal: declare a `cancelled` status — terminal like `done` — and reach it from every status a run may be abandoned in. A `superstates:` group does that in one place: it lists the non-terminal statuses and the `to: cancelled` transition they all inherit, so `booping playbook-transition <name> cancelled …` is legal wherever the run stands without an edge repeated per status. Hooks declared on that transition fire like any other's — stamp the artifact, commit the vault. Once cancelled the run is over: `playbook-state` reports the terminal status with no edges leaving it.

### How state renders

A playbook with `states:` renders a `## State` section right after `## Playbook Steps`: the `playbook-state` invocation for that playbook, then per machine its referencing scopes, artifact path, initial status, the exact `playbook-transition` invocation (with `--state` / `--instance` / `--target` where the machine needs them), and a status → `to` / `when` / `gates` table. A playbook without `states:` renders no such section.

## Notices

Problems in the manifest surface as in-band notices when you render (or run) the playbook:

- **Blocking `STOP` notices** — the playbook refuses to run. Causes: a step named in the graph has no `<name>/prompt.md` file; a dependency names a step that isn't in the graph; the graph has a cycle; the graph is missing entirely; a step that is not `detached:` shares a parallel wave; a step carries the legacy `agent:` key instead of `detached:`; `graph:` is declared in both `playbook.yaml` and `playbook.md` frontmatter; `playbook.yaml` is unparseable or is not a mapping; a `states:` entry is malformed (an `initial` that is not one of its `statuses`, or `{instance}` in the artifact path with no subgraph referencing it); a `state:` ref names a states entry that does not exist; a `jinja: true` playbook rendered without project context, or whose body fails to render; the playbook `name` is defined at more than one level.
- **Warning notes** — a step directory that exists on disk but isn't wired into the graph (it never runs), or a `states:` entry no graph scope references (it is never used), produces a note.
- **Lesson notes** — also non-blocking: a [lesson](#lessons) carrying no usable `targets:` entry (it is injected nowhere), a lesson whose `{playbook}/{step}` target names a step this playbook doesn't have (that entry is ignored), and one note per retired lesson directory still holding markdown on disk — a legacy playbook `_lessons/` dir, or the vault's legacy `lessons/` directory. `--no-lessons` suppresses these along with the lesson sections.

## Authoring a global playbook

Create the directory under your home vault root:

```
~/Claude/_playbooks/my-playbook/playbook.md
~/Claude/_playbooks/my-playbook/playbook.yaml
~/Claude/_playbooks/my-playbook/first/prompt.md
~/Claude/_playbooks/my-playbook/second/prompt.md
```

Fill in `playbook.md` with identity frontmatter and a plain-markdown preamble body, `playbook.yaml` with the `graph:` (plus `state:` / `states:` if the run should be resumable), and each `<step>/prompt.md` with its own frontmatter and prompt body. Run `/playbook` in any project and it appears in the listing as a global playbook.

To skip the by-hand part, scaffold the skeleton — `playbook.md`, an empty `playbook.yaml` graph, and `_references/`:

```
bin/booping scaffold core.playbook_authoring_playbook.scaffold ~/Claude/_playbooks/my-playbook \
  --set name=my-playbook
```

See [scaffold trees](project_config.md#scaffold-trees) for the tree itself and how to override or extend it.

## Authoring a project playbook

Same shape, but under the Project Vault:

```
{vault}/_playbooks/my-playbook/playbook.md
{vault}/_playbooks/my-playbook/playbook.yaml
{vault}/_playbooks/my-playbook/<step>/prompt.md
```

It appears in `/playbook` as a project playbook. Pick a `name` no other level already uses.

## Worked example

A **diamond**: prepare once, run lint and tests in parallel, then publish after both.

`~/Claude/_playbooks/ship/playbook.md`:

```markdown
---
name: ship
title: Ship
summary: Prepare, check in parallel, then publish.
trigger: run the ship playbook
---

Ship the current change set. Stop at the first hard failure.
```

`~/Claude/_playbooks/ship/playbook.yaml`:

```yaml
graph:
  prep: []
  lint: [prep]
  tests: [prep]
  publish: [lint, tests]
```

Each step directory (`prep/`, `lint/`, `tests/`, `publish/`) holds a `prompt.md` with its own frontmatter and prompt body.

The rendered procedure lists the steps as:

```
| Step | Dependencies | Summary | Review gate |
| --- | --- | --- | --- |
| `prep` | — | … | — |
| `lint` | `prep` | … | — |
| `tests` | `prep` | … | — |
| `publish` | `lint`, `tests` | … | — |
```

`prep` runs first (fetching its own body via `booping render-playbook ship --step prep`). Then `lint` and `tests` spawn together in one message and run in parallel — both must be `detached:`. Once both finish (and any review gates are cleared), `publish` runs.

## Rendering

`booping render-playbook <name>` renders the composed procedure to stdout, or to a file with `--output PATH` (`--output -` writes to stdout). An unknown playbook name exits 1. Graph problems don't fail the command — they render as the in-band STOP/Note notices described above (exit 0).

The composed output carries a `## Lessons` section when any [lesson](#lessons) targets the playbook by name.

These flags help while authoring:

- `--step <step>` — print just that step's body (rendered, for a `jinja: true` playbook), with no heading, instruction bullets, or gate wrapping, followed by the lessons targeting that step. This is the command every composed step section points at, and it is handy for eyeballing one prompt in isolation.
- `--no-lessons` — drop the `## Lessons` section from the composed output, the step-lesson append from `--step`, and the lesson notices, leaving the bodies alone.
- `--project <path>` — resolve context against the Project Vault at `<path>` instead of whatever project is attached to the current directory. Lets you render a `requires_project` or `jinja: true` playbook from anywhere. It **pins the render to the core and project levels**: the config merge skips the global tier (`~/.config/booping/config.yaml`), and discovery — for playbooks and [lessons](#lessons) alike — skips the global roots (`<home_dir>/_playbooks/`, `<home_dir>/_lessons/`), so the same command renders the same bytes on another machine.
- `--set <dotted.key>=<value>` — override one config value for this render only (repeatable, later pairs win, values stay strings). The pair wins over every config tier, which is how a partial is parameterised from the command line — and how a timestamp a template reads from config gets pinned to a fixed value for a reproducible render.
- `--inline-steps` — embed each runner-performed step's body in its section instead of the fetch command, the same as `inline_steps: true` in the manifest. Detached steps keep fetch-form. Handy for reading a whole procedure as one document.

`--project` and `--set` are not playbook-specific: plain `booping render` accepts both, with the same semantics.
