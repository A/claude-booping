# Playbooks

A **playbook** is a user-authored, multi-step guided procedure that lives in the vault and is driven by the [/playbook](playbooks.md) skill. Where the built-in skills (`/groom`, `/develop`, …) are fixed workflows shipped by the plugin, a playbook is yours to write: an ordered list of prompt steps, each optionally delegated to a sub-agent, with review gates where you want to inspect the output before continuing.

Playbooks are plain markdown with YAML frontmatter — no Jinja, no build step. Author them by hand and they show up in `/playbook` immediately.

## Scopes and shadowing

Playbooks are discovered from two roots:

- **Global** — `<home_dir>/_playbooks/<name>/` (default `~/Claude/_playbooks/`). Shared across every project on the machine.
- **Local** — `{vault}/_playbooks/<name>/`. Specific to one project's vault.

When the same playbook `name` exists in both roots, the **local one shadows the global one** — the project-local version wins and the global one is hidden. This lets a project override a shared playbook without touching the global copy. Directories whose name starts with `_` (e.g. `_lib`) are skipped, so you can keep shared helper content alongside playbooks without it being picked up as one.

## Layout

Each playbook is a directory:

```
<name>/
  playbook.md          # manifest: metadata + ordered step list
  steps/
    <step>.md          # one file per step, in any order on disk
```

## Frontmatter contract

`playbook.md` frontmatter:

- `name` — identifier, unique within a root (used for shadowing).
- `title` — human-readable name.
- `summary` — one-line description shown in the `/playbook` listing.
- `trigger` — natural-language hint the skill matches the user's request against.
- `steps` — ordered list of step names. Each entry maps to `steps/<step>.md`.

`steps/<step>.md` frontmatter:

- `name` — step identifier.
- `summary` — one-line description of the step.
- `agent` — the sub-agent to run this step (by bare name), or `null` to run the step inline in the conversation.
- `model` — model hint for the step.
- `effort` — effort hint for the step.
- `review_gate` — when non-null, `/playbook` stops after the step, presents the output, and continues only on your explicit confirmation. `null` runs straight through.

The step's **body** is the prompt for that step. When `/playbook` runs a step it appends a `## Run-time context` block (`specs_dir`, `project`) after the body so steps can reference where to write and which project they run against.

## Authoring a global playbook

Create the directory under your home vault root:

```
~/Claude/_playbooks/my-playbook/playbook.md
~/Claude/_playbooks/my-playbook/steps/first.md
~/Claude/_playbooks/my-playbook/steps/second.md
```

Fill in `playbook.md` with the manifest frontmatter above, list your steps in order under `steps:`, and write each `steps/<step>.md` with its own frontmatter and prompt body. Run `/playbook` in any project and it appears in the listing with scope `global`.

## Authoring a local playbook

Same shape, but under the project's vault:

```
{vault}/_playbooks/my-playbook/playbook.md
{vault}/_playbooks/my-playbook/steps/...
```

It appears in `/playbook` with scope `local` and, if it shares a `name` with a global playbook, shadows it for that project.

## Worked example

A minimal global playbook `test` with three steps, each delegated to `general-purpose`. Step 1 carries a review gate.

`~/Claude/_playbooks/test/playbook.md`:

```yaml
---
name: test
title: Test
summary: Smoke-test the playbook runner end to end.
trigger: run the test playbook
steps:
  - current-time
  - hcmc-weather
  - btc-price
---
```

`~/Claude/_playbooks/test/steps/current-time.md`:

```markdown
---
name: current-time
summary: Report the current time.
agent: general-purpose
review_gate: "Ask the user if he sleeps; continue only after an explicit answer."
---

Report the current date and time in UTC and local time.
```

Run trace:

1. `/playbook` lists `test` (scope `global`).
2. The orchestrator reads each step file and spawns the sub-agent with the step body plus an appended `## Run-time context` block (`specs_dir`, `project`).
3. Step 1 returns the timestamps; its `review_gate` **stops** the run and asks the user.
4. The user answers; execution resumes.
5. Steps 2–3 run and return a weather line and a BTC price line.
6. The run closes with a one-paragraph summary combining all three outputs.

## Evals and harness

Playbook eval suites and their run harness live **vault-side** at `~/Claude/_playbooks/`, with their own `README`. They are not part of this repository — the plugin only discovers and drives playbooks; authoring, evaluating, and iterating on them happens in the vault.
