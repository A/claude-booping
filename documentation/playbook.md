# Playbooks

!!! warning "Unstable — work in progress"
    Playbooks are an experimental feature. The manifest format, step frontmatter, and `/playbook` behaviour may change in breaking ways between releases.

A **playbook** is a multi-step guided procedure driven by the `/playbook` skill. Where the built-in skills (`/groom`, `/develop`, …) are fixed workflows shipped by the plugin, a playbook is yours to write: a set of prompt steps, each optionally delegated to a sub-agent, with review gates where you want to inspect the output before continuing. Most playbooks are yours and live in your vault; a few ship with the plugin (see [Scopes](#scopes)).

A playbook's **structure** lives in `playbook.yaml`: the `graph:` (which steps run, in what order, which in parallel) and the optional `states:` (named state machines that persist run state on disk so a run can be resumed). `playbook.md` keeps **identity and prose** — the manifest frontmatter (`name`, `title`, `summary`, `trigger`, …) and the preamble body. Bodies are plain markdown by default; a playbook can opt into [Jinja rendering](#jinja-bodies) if it needs live project data. Author a playbook by hand and it shows up in `/playbook` immediately.

!!! note "Legacy: `graph:` in `playbook.md` frontmatter"
    A playbook with no `playbook.yaml` still works: `graph:` is read from `playbook.md` frontmatter as before. Declaring `graph:` in **both** places is a blocking STOP — keep exactly one. `state:` / `states:` are `playbook.yaml`-only; there is no frontmatter fallback for them.

## Scopes

Playbooks are discovered from three roots:

- **Core** — `<plugin-root>/playbooks/<name>/`. Shipped with the plugin.
- **Global** — `<home_dir>/_playbooks/<name>/` (default `~/Claude/_playbooks/`). Shared across every project on the machine.
- **Local** — `{vault}/_playbooks/<name>/`. Specific to one project's vault.

**A playbook `name` must be unique across all three roots.** The same name in two roots is a name clash: `/playbook` marks the entry `⚠ clash` in its listing, and rendering the playbook returns a blocking STOP notice instead of the procedure — neither copy runs until one of them is renamed. Nothing is silently hidden. To adapt a playbook you didn't write, either copy it under a new name or leave it alone and attach [lessons](#lessons) to it. Directories whose name starts with `_` (e.g. `_lib`, `_lessons`) are skipped, so you can keep shared helper content alongside playbooks without it being picked up as one.

### Shipped playbooks

One core playbook ships today: **`groom`** — the grooming workflow expressed as a playbook (intake → codebase and web research in parallel → design → draft → present). It is driven by the experimental **`/groom-playbook`** skill, which does nothing but run that playbook.

!!! warning "Experimental — `/groom` is still the one to use"
    `/groom-playbook` is a parallel experiment, not a replacement. [`/groom`](groom.md) remains the supported way to spec a sprint and is unaffected by it.

A playbook of your own named `groom` would clash with it rather than replace it. To bend the shipped procedure to a project, add [lessons](#lessons) under `{vault}/_playbooks/groom/_lessons/`; to fork it, copy the directory under a different name.

## Layout

Each playbook is a directory:

```
<name>/
  playbook.md          # identity frontmatter + plain-markdown preamble body
  playbook.yaml        # structure: graph:, state:, states:
  <step>/              # one directory per step — the directory name IS the step name
    prompt.md          #   the step itself; everything else in the dir is yours
  _lessons/            # standing rules injected into every run of this playbook
  _scripts/            # executables invoked by `script <name>` transition hooks
  _references/         # `_`-prefixed dirs are not steps — free workspace
```

**A step is a directory and `prompt.md` is the step.** Every non-`_` subdirectory holding a `prompt.md` is a step, and its directory name is the step name the graph references. Nothing else in the directory is loaded — sibling files (fixtures, eval configs, prompt variants like `prompt.haiku-4-5.md`) are invisible to the runner. A non-`_` subdirectory without a `prompt.md` is skipped with a warning.

Directory order on disk is irrelevant to the run — **the `graph:` decides which steps run and in what order**. Directories whose name starts with `_` (e.g. `_references/`, `_fixtures/`) are never steps, so you can keep disabled steps and shared material alongside without wiring them in.

## Lessons

A **lesson** is a short standing rule injected into a playbook run — the way to correct a procedure without editing its prompts. Lessons are markdown files named `NNNN_title.md`, kept in `_lessons/` directories and loaded in filename order. Where the directory sits decides who the lesson binds:

| Scope | Directory | Applies to |
| --- | --- | --- |
| Global | `<home_dir>/_playbooks/_lessons/` | every playbook, in every project |
| Project | `{vault}/_playbooks/_lessons/` | every playbook, in this project |
| Playbook | `<root>/<name>/_lessons/` | that one playbook |
| Step | any of the above, plus `step:` in the file's frontmatter | that one step of that playbook |

A lesson file is prose with optional frontmatter:

```markdown
---
title: Name every artifact path absolutely
step: draft
---

Receipts must name paths absolutely — a relative path is ambiguous once the run moves between workdirs.
```

- `title` — *optional*, used in the lesson's heading; defaults to the filename without its extension.
- `step` — *optional*. With it, the lesson reaches only that step. Without it, the lesson binds the whole run. A `step:` naming a step the playbook does not have produces a warning note and the lesson is ignored.

**Same filename in two scopes → the most specific one wins.** A `0002_receipts.md` in both the global and the project `_lessons/` loads once, from the project; the same holds for a playbook-level file present in more than one root. Give lessons distinct names unless you mean to replace one.

**Lessons for a playbook you don't own.** A playbook-level `_lessons/` directory is picked up from *every* root, whether or not that root holds the playbook itself. So a project can attach its own lessons to the shipped `groom` playbook simply by creating `{vault}/_playbooks/groom/_lessons/` — no `playbook.md`, no copy, no name clash.

**Where they surface.** Playbook-scoped lessons render as a `## Lessons` section in the composed procedure, between the preamble and `## Execution graph`; they bind the driver for the whole run. Step-scoped lessons are appended to that step's `booping render-playbook <name> --step <step>` output, so they reach exactly the sub-agent running that step. `--no-lessons` suppresses both, which is useful when diffing a prompt against its file on disk.

## The manifest

Structure lives in `playbook.yaml`, identity and prose in `playbook.md`.

### `playbook.yaml`

- `graph` — mapping of **node name → node**. A node whose value is a **list** is a plain step and the list is its dependency step names; a node whose value is a **mapping** is a [subgraph](#subgraphs). This is the whole structure: membership (only mapped steps run), order (a step runs after all its dependencies), and parallelism (steps whose dependencies are all satisfied by earlier waves run together).
- `state` — *optional*, the name of the `states:` entry that governs the **outer** graph.
- `states` — *optional*, mapping of state-machine name → machine. See [Run state](#run-state).

A subgraph node may carry its own `state:` key, naming the machine that governs each of its instances.

### `playbook.md` frontmatter

- `name` — identifier, unique across all discovery roots (a duplicate is a blocking name clash).
- `title` — human-readable name.
- `summary` — one-line description shown in the `/playbook` listing.
- `trigger` — natural-language hint the skill matches the user's request against.
- `requires_project` — *optional*, default `false`. When `true`, the playbook only runs with a booping project attached: `/playbook` flags it in the listing and refuses to run it without a project, and `booping render-playbook` refuses to render it (stderr + exit 1).
- `jinja` — *optional*, default `false`. When `true`, the preamble and every step body are rendered as Jinja templates against live project context. See [Jinja bodies](#jinja-bodies).
- `graph` — *legacy fallback only*, same shape as `playbook.yaml`'s `graph:`. Used when the playbook has no `playbook.yaml`.

The manifest **body** is a preamble — a playbook-level instruction inserted above the rendered procedure. No step calls: the graph, not the body, decides what runs.

`<step>/prompt.md` frontmatter (the step identifier comes from the directory name, not frontmatter):

- `summary` — one-line description of the step, rendered into the step's section as a `Summary:` instruction bullet. It is where a step declares execution hints in its own domain words — e.g. *"Can be paralleled as one agent per feature"* — since the runner knows nothing about a playbook's domain.
- `agent` — how the step runs (see the grammar below).
- `review_gate` — when non-null, `/playbook` stops after the step, presents the output, and continues only on your explicit confirmation. `null` runs straight through.
- `title` — *optional* human-readable heading for the step. When absent, the rendered heading is the titleized directory name (e.g. `current-time` → `Current Time`).
- `inputs` — *optional* list of what the step expects to be handed. Each entry is either a mapping `{what, from}` (`from` *optional*) or a plain string shorthand for `what`. **Advisory**: the driver uses them to build the step's `## Inputs` block, but the step is not limited to them, and `from` is freeform prose — it is not validated against the graph. A malformed entry warns on stderr and is skipped.
- `outputs` — *optional* list of plain strings naming what the step produces. They feed later steps' `inputs` and become the step's return contract; without them the driver asks for `artifacts written + outcome, ≤ 5 lines`.

The step **body** is the prompt for that step.

```yaml
---
summary: Draft the plan against the approved design
agent: sonnet:high
review_gate: Plan draft ready — approve before presenting?
inputs:
  - from: design
    what: approved design doc (path or content)
  - from: user
    what: any sizing constraints stated in conversation
outputs:
  - plan draft written to {workdir}/plan.md
---
```

### The `agent` grammar

A single `agent` field decides how the step executes:

- `null` — run the step **inline** in the driving conversation, no sub-agent. An inline step can never share a parallel wave (see below).
- `<model>:<effort>` where `model` ∈ `{opus, sonnet, haiku, fable}` (e.g. `sonnet:high`, `haiku:medium`) — spawn a **generic sub-agent** with that model and effort.
- any other non-null string — spawn a **named sub-agent** via `subagent_type=<value>`. The value is used verbatim, so colons are fine for namespaced agents (e.g. `booping:booping-researcher`, `general-purpose`).

## Jinja bodies

By default every body — the manifest preamble and each `prompt.md` — is passed through **verbatim**. Braces, `{{ }}`, and template-looking text are just text.

Set `jinja: true` in the manifest frontmatter to opt the **whole playbook** in (it is all-or-nothing — there is no per-step flag). Bodies are then rendered as Jinja templates with the same project context the built-in skills get: the attached project, its config, and the shared fragments the plugin ships. Include paths are resolved **relative to the plugin root**, so they work identically whatever scope your playbook lives in:

```markdown
---
name: ship
title: Ship
summary: Prepare, check in parallel, then publish.
trigger: run the ship playbook
jinja: true
requires_project: true
---
{% import "_partials/_plan_transitions.j2" as plan_transitions with context %}
# Ship

{{ plan_transitions.render("develop") }}

{% include "_partials/_shared_instructions.j2" %}
```

Two things change once you opt in:

- **Project context is required.** Rendering a `jinja: true` playbook without a project attached produces a blocking `STOP` notice instead of the procedure. Pair it with `requires_project: true`.
- **A template error is a blocking notice**, not a crash — the failure is reported in-band and the playbook refuses to run.

A Jinja body is meaningless until rendered — the `booping render-playbook <name> --step <step>` fetch every step body goes through returns it already rendered (see below).

## How the graph renders

`/playbook` resolves the graph into **waves** — a step joins the earliest wave in which all its dependencies sit in a prior wave. Steps sharing a wave run in parallel.

- **Step bodies are never embedded** — every section ends with the line *Run `booping render-playbook <name> --step <step>` for content.*, the same for plain and `jinja: true` playbooks. A section carries only metadata: summary, dependencies, wave siblings, `Inputs:` / `Outputs:`, agent, review gate.
- **Delegated steps fetch their own body** — the driver never runs the fetch command for a sub-agent step. It spawns the agent with a bootstrap prompt: the fetch command ("treat its stdout as your full instruction"), a `## Run-time context` block (project, specs dir, plus `workdir` / `instance` where they apply), a `## Inputs` block resolved from the section's declared inputs and prior steps' receipts, and a `## Return` contract built from the declared outputs. An inline step (`agent: null`) is the only case where the driver runs the fetch itself and executes the stdout.
- **Parallel wave members must set `agent`** — inline steps (`agent: null`) can't run in parallel, so a step that shares a wave with others must delegate to a sub-agent.
- **Review gates pause after the wave** — once every member of a wave finishes, each member's gate is presented (labeled by step) and the run waits for your confirmation before the next wave.

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

**Repeat semantics.** `repeat` is prose, not a count — the driver reads it against the output of the steps in `dependencies` and decides how many instances to run. No `repeat` key means exactly one instance. Each instance walks the inner waves on its own — its own `--step` fetch per inner step, never a body reused across instances — and each inner step's `review_gate` fires per instance. Instances run in parallel only when **every** inner step sets an `agent`; if any inner step is inline, instances run one at a time.

**One level only.** A subgraph cannot contain another subgraph.

Subgraph-specific STOP conditions (on top of the usual [notices](#notices)):

- the node mapping has an unknown key, or is missing `dependencies` or `graph`;
- `dependencies` is not a list, `graph` is not a non-empty mapping, or `repeat` is not a string;
- an inner node's value is a mapping (nested subgraph);
- a step name appears in more than one scope.

In the rendered procedure the subgraph shows up as a mermaid cluster, a nested entry in the wave list, and a `## Subgraph: <name>` intro section (`After:`, `Repeat:`, `Inner waves:`) followed by its inner step sections, each tagged `Part of: <name>`.

## Run state

Without `states:`, a run lives entirely in one conversation — close it and the run is gone. Declare `states:` and the run's progress is persisted in **artifacts on disk**, so a run can be inspected, resumed later, and advanced only through legal transitions.

A `states:` entry is a **named state machine**:

- `artifact` — path to the markdown file holding this machine's status, **relative to the run workdir**. A `{instance}` placeholder makes the machine per-instance (one artifact per subgraph instance) and is only legal when some subgraph references the machine.
- `initial` — the status a freshly bootstrapped artifact starts in. Must be a key of `statuses`.
- `statuses` — mapping of status name → `{transitions: [...]}` or `{terminal: true}`. Each transition has `to`, and optionally `when` (the trigger prose the driver matches a step outcome against), `gates` (verifiable preconditions the driver judges before firing), and `hooks` (mechanical side effects the CLI runs).

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
            hooks: ["frontmatter-update intaken=@now"]
      researching:
        transitions:
          - to: developing-steps
            when: both research steps returned and design confirmed
            gates: ["research-codebase and research-web done, findings recorded"]
            hooks: ["frontmatter-update researched=@now commit=@head", "script check-findings"]
      developing-steps:
        transitions:
          - to: done
            when: every step instance terminal
            gates: ["every steps/*/index.md status: done"]
            hooks: ["frontmatter-update completed=@now"]
      done: {terminal: true}
  step:
    artifact: steps/{instance}/index.md
    initial: spec-ing
    statuses:
      spec-ing:
        transitions:
          - to: reviewing
            when: spec written
            hooks: ["frontmatter-update spec_done=@now"]
      reviewing:
        transitions:
          - to: done
            when: user confirmed the spec
            gates: ["explicit user confirmation captured"]
            hooks: ["frontmatter-update confirmed=@now"]
      done: {terminal: true}
```

### Hooks

Two hook forms are available on a transition:

- `frontmatter-update [<file>] <key>=<val> ...` — set frontmatter keys on the artifact, or on `<file>` when a target is given. Values interpolate `@now` (UTC `yyyymmdd hh:mm`), `@today` (`yyyymmdd`) and `@head` (attached repo's HEAD sha).
- `script <name>` — run `<playbook-dir>/_scripts/<name>`.

The optional `<file>` target is the first token after the hook name that carries no `=`. It resolves against the **run workdir** — the same anchor as the machine's `artifact` — and may carry `{instance}`, interpolated with the instance slug (legal only when an instance is in scope). The file must exist; a missing file is an error (exit 2) that aborts the transition — nothing is created. A file without a frontmatter block gets one prepended, the existing content becoming the body unchanged. In the mutation report a file-target update prints as `frontmatter <file>: k=v` instead of the plain `frontmatter: k=v`.

The status set itself is implicit — the CLI always writes `status: <to>` before running the transition's hooks.

### `_scripts/` contract

A `script <name>` hook runs the executable at `<playbook-dir>/_scripts/<name>`:

- it must exist and be executable, or the transition fails (exit 2) without mutating anything further;
- it runs with the **run workdir** as its cwd;
- it receives `BOOPING_ARTIFACT` (absolute artifact path), `BOOPING_WORKDIR` (absolute run workdir) and `BOOPING_INSTANCE` (the instance slug, empty for a non-instance machine);
- a non-zero exit aborts the transition; the script's stderr is relayed.

### Run workspace

A run gets its own workdir; artifact paths resolve against it and the playbook directory stays read-only source. The convention `/playbook` follows is:

```
{vault}/_runs/<playbook>/<run-slug>/
```

with `<run-slug>` = `{YYYYMMDD}-<kebab-topic>`. Every state command takes `--workdir <path>` (default: cwd).

### Commands

`booping playbook-state <playbook> [--workdir PATH]` — read-only. Prints YAML: the playbook name, the resolved workdir, and per `states:` entry its `artifact`, its current `status` and the `next:` edges leaving it (each with `to` and, when declared, `when` / `gates`). A per-instance entry reports an `instances:` mapping keyed by slug, discovered by globbing the artifact path. An artifact that does not exist yet reports `status: not-started` with a single bootstrap edge to the machine's `initial`. Exits 1 for an unknown playbook, a missing workdir, a playbook with no `states:`, or an artifact with no `status:` key.

`booping playbook-transition <playbook> <to> [--state NAME] [--instance SLUG] [--workdir PATH]` — the only writer of run state. `--state` defaults to the outer graph's `state:` ref; `--instance` is required exactly when the artifact path carries `{instance}`. It reads the artifact's current status, checks that `<to>` is reachable from it, sets `status: <to>`, then runs the matched transition's hooks in order. A missing artifact is bootstrapped — legal only when `<to>` is the machine's `initial`. Re-running the same target is idempotent. It prints a **mutation report** (created/`from → to`/each frontmatter line/each script result) which is the authoritative record — the driver relays it and never re-reads the artifact to verify. Illegal transitions exit 1; hook failures exit 2.

### Resume

Everything needed to resume lives on disk. `/playbook` runs `booping playbook-state <name> --workdir <workdir>` on entry — first run and every resume — and restarts from the reported frontier: work already past its status is skipped, the first non-terminal status is re-entered, and `not-started` means bootstrap on the first transition. Nothing hand-edits an artifact's `status:` or a hook-written key; only `playbook-transition` mutates run state.

### How state renders

A playbook with `states:` renders a `## State` section right after `## Execution graph`: the `playbook-state` invocation for that playbook, then per machine its referencing scopes, artifact path, initial status, the exact `playbook-transition` invocation (with `--state` / `--instance` where the machine needs them), and a status → `to` / `when` / `gates` / `hooks` table. A playbook without `states:` renders no such section.

## Notices

Problems in the manifest surface as in-band notices when you render (or run) the playbook:

- **Blocking `STOP` notices** — the playbook refuses to run. Causes: a step named in the graph has no `<name>/prompt.md` file; a dependency names a step that isn't in the graph; the graph has a cycle; the graph is missing entirely; an inline step shares a parallel wave; `graph:` is declared in both `playbook.yaml` and `playbook.md` frontmatter; `playbook.yaml` is unparseable or is not a mapping; a `states:` entry is malformed (missing `artifact`, an `initial` that is not one of its `statuses`, or `{instance}` in the artifact path with no subgraph referencing it); a `state:` ref names a states entry that does not exist; a `jinja: true` playbook rendered without project context, or whose body fails to render; the playbook `name` is defined in more than one root.
- **Warning notes** — a step directory that exists on disk but isn't wired into the graph, a `states:` entry no graph scope references, or a lesson whose `step:` names a step the playbook doesn't have, produces a note; the step never runs, the entry is never used, the lesson is ignored.

## Authoring a global playbook

Create the directory under your home vault root:

```
~/Claude/_playbooks/my-playbook/playbook.md
~/Claude/_playbooks/my-playbook/playbook.yaml
~/Claude/_playbooks/my-playbook/first/prompt.md
~/Claude/_playbooks/my-playbook/second/prompt.md
```

Fill in `playbook.md` with the identity frontmatter and a plain-markdown preamble body, and `playbook.yaml` with the `graph:` (plus `state:` / `states:` if the run should be resumable). Write each `<step>/prompt.md` with its own frontmatter and prompt body. Run `/playbook` in any project and it appears in the listing with scope `global`.

## Authoring a local playbook

Same shape, but under the project's vault:

```
{vault}/_playbooks/my-playbook/playbook.md
{vault}/_playbooks/my-playbook/playbook.yaml
{vault}/_playbooks/my-playbook/<step>/prompt.md
```

It appears in `/playbook` with scope `local`. Pick a `name` no global or core playbook already uses — sharing one is a name clash and neither runs until you rename.

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

Each step directory (`prep/`, `lint/`, `tests/`, `publish/`) holds a `prompt.md` with its own frontmatter and prompt body. `lint` and `tests` both depend only on `prep`, so they share a wave; `publish` waits for both.

The rendered procedure lists the waves as:

```
1. prep
2. lint ∥ tests
3. publish
```

`prep` runs first (fetching its own body via `booping render-playbook ship --step prep`). Then `lint` and `tests` spawn together in one message and run in parallel — both must set `agent`. Once both finish (and any review gates are cleared), `publish` runs.

## Rendering

`booping render-playbook <name>` renders the composed procedure to stdout, or to a file with `--output PATH` (`--output -` writes to stdout). An unknown playbook name exits 1. Graph problems don't fail the command — they render as the in-band STOP/Note notices described above (exit 0).

The composed output carries a `## Lessons` section when any playbook-scoped [lesson](#lessons) applies.

Three flags help while authoring:

- `--step <step>` — print just that step's body (rendered, for a `jinja: true` playbook), with no heading, instruction bullets, or gate wrapping, followed by the lessons targeting that step. This is the command every composed step section points at: each delegated step runs it itself from its bootstrap prompt, the driver runs it for inline steps, and it is handy for eyeballing one prompt in isolation.
- `--no-lessons` — drop the `## Lessons` section from the composed output and the step-lesson append from `--step`, leaving the bodies alone.
- `--project <path>` — resolve context against the vault at `<path>` instead of whatever project is attached to the current directory. Lets you render a `requires_project` or `jinja: true` playbook from anywhere.

## Evals and harness

Playbook eval suites and their run harness live **vault-side** at `~/Claude/_playbooks/`, with their own `README`. They are not part of this repository — the plugin only discovers, composes, and drives playbooks; authoring, evaluating, and iterating on them happens in the vault.
