# Playbooks

A **playbook** is a user-authored, multi-step guided procedure that lives in the vault and is driven by the [/playbook](playbooks.md) skill. Where the built-in skills (`/groom`, `/develop`, …) are fixed workflows shipped by the plugin, a playbook is yours to write: an ordered sequence of prompt steps, each optionally delegated to a sub-agent, with review gates where you want to inspect the output before continuing.

A playbook's **manifest body is a Jinja template**: you compose the procedure by calling `inline_step` / `reference_step`, and the call order is the run order. The individual step files stay plain markdown — no Jinja in a step body. Author a playbook by hand and it shows up in `/playbook` immediately.

## Scopes and shadowing

Playbooks are discovered from two roots:

- **Global** — `<home_dir>/_playbooks/<name>/` (default `~/Claude/_playbooks/`). Shared across every project on the machine.
- **Local** — `{vault}/_playbooks/<name>/`. Specific to one project's vault.

When the same playbook `name` exists in both roots, the **local one shadows the global one** — the project-local version wins and the global one is hidden. This lets a project override a shared playbook without touching the global copy. Directories whose name starts with `_` (e.g. `_lib`) are skipped, so you can keep shared helper content alongside playbooks without it being picked up as one.

## Layout

Each playbook is a directory:

```
<name>/
  playbook.md          # manifest: metadata frontmatter + Jinja body composing the steps
  steps/
    <step>.md          # one file per step, in any order on disk
```

The loader globs `steps/*.md` (sorted; `_`-prefixed files skipped), but disk order is irrelevant to the run — **the manifest body decides which steps appear and in what order** via its composition calls.

## Frontmatter contract

`playbook.md` frontmatter:

- `name` — identifier, unique within a root (used for shadowing).
- `title` — human-readable name.
- `summary` — one-line description shown in the `/playbook` listing.
- `trigger` — natural-language hint the skill matches the user's request against.

There is **no `steps:` list** — the manifest body composes the steps (see below).

`steps/<step>.md` frontmatter:

- `name` — step identifier (referenced from the manifest body).
- `summary` — one-line description of the step.
- `agent` — how the step runs (see the grammar below).
- `review_gate` — when non-null, `/playbook` stops after the step, presents the output, and continues only on your explicit confirmation. `null` runs straight through.
- `title` — *optional* human-readable heading for the step. When absent, the rendered heading is the titleized `name` (e.g. `current-time` → `Current Time`).

### The `agent` grammar

A single `agent` field decides how the step executes:

- `null` — run the step **inline** in the driving conversation, no sub-agent.
- `<model>:<effort>` where `model` ∈ `{opus, sonnet, haiku, fable}` (e.g. `sonnet:high`, `haiku:medium`) — spawn a **generic sub-agent** with that model and effort.
- any other non-null string — spawn a **named sub-agent** via `subagent_type=<value>`. The value is used verbatim, so colons are fine for namespaced agents (e.g. `booping:booping-researcher`, `general-purpose`).

The step **body** is the prompt for that step (plain markdown — never Jinja).

## The manifest body

The `playbook.md` body is a Jinja template. Two functions compose steps:

- `{{ inline_step('name') }}` — pull the step's body **inline** into the rendered procedure.
- `{{ reference_step('name') }}` — emit a pointer to the step file instead of its body: `Read [Title](<abs path>) for content.`

Call order defines the run sequence — there is no separate ordered list. A step file that is never called simply doesn't appear in the render. Calling an unknown step name **fails the render**.

Each call renders as a `## <Title>` section. If the step has a sub-agent (`agent` non-null) and/or a `review_gate`, the section opens with an `Instructions:` block:

- a **sub-agent bullet** — present when `agent` is non-null, describing how to spawn the step (generic model:effort agent, or named `subagent_type`).
- a **review-gate bullet** — present when `review_gate` is set, carrying the gate text.

When neither is present the `Instructions:` block is omitted entirely and the section is just the heading plus the body (inline) or the `Read …` pointer (reference). Gates are therefore **rendered from frontmatter, not written into step bodies** — the `/playbook` skill reads the gate bullet and owns pausing/enforcement.

## Authoring a global playbook

Create the directory under your home vault root:

```
~/Claude/_playbooks/my-playbook/playbook.md
~/Claude/_playbooks/my-playbook/steps/first.md
~/Claude/_playbooks/my-playbook/steps/second.md
```

Fill in `playbook.md` with the manifest frontmatter above, then write the body as a Jinja template that calls `inline_step` / `reference_step` in the order you want the steps to run. Write each `steps/<step>.md` with its own frontmatter and plain-markdown prompt body. Run `/playbook` in any project and it appears in the listing with scope `global`.

## Authoring a local playbook

Same shape, but under the project's vault:

```
{vault}/_playbooks/my-playbook/playbook.md
{vault}/_playbooks/my-playbook/steps/...
```

It appears in `/playbook` with scope `local` and, if it shares a `name` with a global playbook, shadows it for that project.

## Rendering

`booping render-playbook <name>` renders the composed procedure — the manifest body with every `inline_step` / `reference_step` call expanded — to stdout, or to a file with `--output PATH` (`--output -` writes to stdout). An unknown playbook name exits 1; an unknown step name raises during the render.

## Worked example

A global playbook `demo` with two steps. The first reports the time inline behind a review gate; the second is delegated to a generic `sonnet:high` sub-agent and pulled in by reference.

`~/Claude/_playbooks/demo/playbook.md`:

```markdown
---
name: demo
title: Demo
summary: Show off inline + reference step composition.
trigger: run the demo playbook
---

{{ inline_step('current-time') }}

{{ reference_step('write-report') }}
```

`~/Claude/_playbooks/demo/steps/current-time.md`:

```markdown
---
name: current-time
summary: Report the current time.
agent: general-purpose
review_gate: "Ask the user if they want to continue; proceed only after an explicit answer."
---

Report the current date and time in UTC and local time.
```

`~/Claude/_playbooks/demo/steps/write-report.md`:

```markdown
---
name: write-report
title: Write Report
summary: Draft a short status report.
agent: sonnet:high
---

Draft a one-paragraph status report from the timestamp above.
```

`booping render-playbook demo` produces roughly:

```markdown
## Current Time

Instructions:
- Spawn a sub-agent (subagent_type: general-purpose) with the prompt below.
- Review gate: Ask the user if they want to continue; proceed only after an explicit answer.

Report the current date and time in UTC and local time.

## Write Report

Instructions:
- Spawn a generic sub-agent (model: sonnet, effort: high) with the referenced content.

Read [Write Report](/abs/path/to/demo/steps/write-report.md) for content.
```

Run trace under `/playbook`:

1. `/playbook` lists `demo` (scope `global`).
2. The skill renders the composed procedure and works through it top to bottom.
3. Step 1 runs (its `agent` names `general-purpose`), returns the timestamps; its `review_gate` **stops** the run and asks the user.
4. The user answers; execution resumes.
5. Step 2 spawns a `sonnet:high` sub-agent that reads the referenced step file and drafts the report.
6. The run closes with a short summary combining the outputs.

## Evals and harness

Playbook eval suites and their run harness live **vault-side** at `~/Claude/_playbooks/`, with their own `README`. They are not part of this repository — the plugin only discovers, composes, and drives playbooks; authoring, evaluating, and iterating on them happens in the vault.
