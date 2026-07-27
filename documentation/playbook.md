# Playbooks

!!! warning "Unstable — work in progress"
    Playbooks are an experimental feature. The manifest format, step frontmatter, and `/playbook` behaviour may change in breaking ways between releases.

A **playbook** is a user-authored, multi-step guided procedure that lives in the vault and is driven by the `/playbook` skill. Where the built-in skills (`/groom`, `/develop`, …) are fixed workflows shipped by the plugin, a playbook is yours to write: a set of prompt steps, each optionally delegated to a sub-agent, with review gates where you want to inspect the output before continuing.

A playbook's structure is declared by a **`graph:` frontmatter mapping** — each step lists the steps it depends on. The graph defines which steps run, in what order, and which run in parallel. The individual step files stay plain markdown — no Jinja anywhere. Author a playbook by hand and it shows up in `/playbook` immediately.

## Scopes and shadowing

Playbooks are discovered from three roots:

- **Core** — `<plugin-root>/playbooks/<name>/`. Shipped with the plugin.
- **Global** — `<home_dir>/_playbooks/<name>/` (default `~/Claude/_playbooks/`). Shared across every project on the machine.
- **Local** — `{vault}/_playbooks/<name>/`. Specific to one project's vault.

When the same playbook `name` exists in more than one root, precedence is **core < global < local** — the narrowest scope wins and the wider ones are hidden. This lets a project override a shared playbook without touching the global copy, and a global playbook override a shipped one. Directories whose name starts with `_` (e.g. `_lib`) are skipped, so you can keep shared helper content alongside playbooks without it being picked up as one.

## Layout

Each playbook is a directory:

```
<name>/
  playbook.md          # manifest: metadata + graph frontmatter, plain-markdown preamble body
  <step>/              # one directory per step — the directory name IS the step name
    prompt.md          #   the step itself; everything else in the dir is yours
  _references/         # `_`-prefixed dirs are not steps — free workspace
```

**A step is a directory and `prompt.md` is the step.** Every non-`_` subdirectory holding a `prompt.md` is a step, and its directory name is the step name the graph references. Nothing else in the directory is loaded — sibling files (fixtures, eval configs, prompt variants like `prompt.haiku-4-5.md`) are invisible to the runner. A non-`_` subdirectory without a `prompt.md` is skipped with a warning.

Directory order on disk is irrelevant to the run — **the `graph:` frontmatter decides which steps run and in what order**. Directories whose name starts with `_` (e.g. `_references/`, `_fixtures/`) are never steps, so you can keep disabled steps and shared material alongside without wiring them in.

## Frontmatter contract

`playbook.md` frontmatter:

- `name` — identifier, unique within a root (used for shadowing).
- `title` — human-readable name.
- `summary` — one-line description shown in the `/playbook` listing.
- `trigger` — natural-language hint the skill matches the user's request against.
- `requires_project` — *optional*, default `false`. When `true`, the playbook only runs with a booping project attached: `/playbook` flags it in the listing and refuses to run it without a project, and `booping render-playbook` refuses to render it (stderr + exit 1).
- `graph` — mapping of **step name → list of dependency step names**. This is the whole structure: membership (only mapped steps run), order (a step runs after all its dependencies), and parallelism (steps whose dependencies are all satisfied by earlier waves run together).

The manifest **body** is a plain-markdown preamble — a playbook-level instruction inserted verbatim above the rendered procedure. No Jinja, no step calls.

`<step>/prompt.md` frontmatter (the step identifier comes from the directory name, not frontmatter):

- `summary` — one-line description of the step, rendered into the step's section as a `Summary:` instruction bullet. It is where a step declares execution hints in its own domain words — e.g. *"Can be paralleled as one agent per feature"* — since the runner knows nothing about a playbook's domain.
- `agent` — how the step runs (see the grammar below).
- `review_gate` — when non-null, `/playbook` stops after the step, presents the output, and continues only on your explicit confirmation. `null` runs straight through.
- `title` — *optional* human-readable heading for the step. When absent, the rendered heading is the titleized directory name (e.g. `current-time` → `Current Time`).

The step **body** is the prompt for that step (plain markdown — never Jinja).

### The `agent` grammar

A single `agent` field decides how the step executes:

- `null` — run the step **inline** in the driving conversation, no sub-agent. An inline step can never share a parallel wave (see below).
- `<model>:<effort>` where `model` ∈ `{opus, sonnet, haiku, fable}` (e.g. `sonnet:high`, `haiku:medium`) — spawn a **generic sub-agent** with that model and effort.
- any other non-null string — spawn a **named sub-agent** via `subagent_type=<value>`. The value is used verbatim, so colons are fine for namespaced agents (e.g. `booping:booping-researcher`, `general-purpose`).

## How the graph renders

`/playbook` resolves the graph into **waves** — a step joins the earliest wave in which all its dependencies sit in a prior wave. Steps sharing a wave run in parallel.

- **First-wave step bodies are embedded** in the rendered procedure, ready to run.
- **Later steps are fetched when their wave starts** — the render points at the step file and `/playbook` reads it then.
- **Parallel wave members must set `agent`** — inline steps (`agent: null`) can't run in parallel, so a step that shares a wave with others must delegate to a sub-agent.
- **Review gates pause after the wave** — once every member of a wave finishes, each member's gate is presented (labeled by step) and the run waits for your confirmation before the next wave.

## Notices

Problems in the graph surface as in-band notices when you render (or run) the playbook:

- **Blocking `STOP` notices** — the playbook refuses to run. Causes: a step named in the graph has no `<name>/prompt.md` file; a dependency names a step that isn't in the graph; the graph has a cycle; the graph is missing entirely; an inline step shares a parallel wave.
- **Warning notes** — a step directory that exists on disk but isn't wired into the graph produces a note and simply never runs.

## Authoring a global playbook

Create the directory under your home vault root:

```
~/Claude/_playbooks/my-playbook/playbook.md
~/Claude/_playbooks/my-playbook/first/prompt.md
~/Claude/_playbooks/my-playbook/second/prompt.md
```

Fill in `playbook.md` with the manifest frontmatter (including `graph:`) and a plain-markdown preamble body. Write each `<step>/prompt.md` with its own frontmatter and prompt body. Run `/playbook` in any project and it appears in the listing with scope `global`.

## Authoring a local playbook

Same shape, but under the project's vault:

```
{vault}/_playbooks/my-playbook/playbook.md
{vault}/_playbooks/my-playbook/<step>/prompt.md
```

It appears in `/playbook` with scope `local` and, if it shares a `name` with a global playbook, shadows it for that project.

## Worked example

A **diamond**: prepare once, run lint and tests in parallel, then publish after both.

`~/Claude/_playbooks/ship/playbook.md`:

```markdown
---
name: ship
title: Ship
summary: Prepare, check in parallel, then publish.
trigger: run the ship playbook
graph:
  prep: []
  lint: [prep]
  tests: [prep]
  publish: [lint, tests]
---

Ship the current change set. Stop at the first hard failure.
```

Each step directory (`prep/`, `lint/`, `tests/`, `publish/`) holds a `prompt.md` with its own frontmatter and prompt body. `lint` and `tests` both depend only on `prep`, so they share a wave; `publish` waits for both.

The rendered procedure lists the waves as:

```
1. prep
2. lint ∥ tests
3. publish
```

`prep` runs first (its body embedded). Then `lint` and `tests` spawn together in one message and run in parallel — both must set `agent`. Once both finish (and any review gates are cleared), `publish` runs.

## Rendering

`booping render-playbook <name>` renders the composed procedure to stdout, or to a file with `--output PATH` (`--output -` writes to stdout). An unknown playbook name exits 1. Graph problems don't fail the command — they render as the in-band STOP/Note notices described above (exit 0).

## Evals and harness

Playbook eval suites and their run harness live **vault-side** at `~/Claude/_playbooks/`, with their own `README`. They are not part of this repository — the plugin only discovers, composes, and drives playbooks; authoring, evaluating, and iterating on them happens in the vault.
