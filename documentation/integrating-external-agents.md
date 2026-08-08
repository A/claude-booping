# Integrating external agents

booping ships with built-in worker agents (`booping-developer`, `booping-researcher`). You can also wire any playbook to delegate to **your own** agent — a plain Claude Code agent with different instructions or a cheaper model, or a Claude Code agent that fronts an external CLI worker or a browser review surface.

Every integration comes down to two pieces of project config:

- **`core.{name}_playbook.agents.<id>`** in your vault config (`~/Claude/{project}/config.yaml`) registers the agent with that playbook. Each entry carries `good_for` / `bad_for` bullets that guide it toward the right choice. The block name is the playbook name with `-` replaced by `_` — `develop` → `core.develop_playbook`, `code-review` → `core.code_review_playbook`.
- **A targeted lesson in `_lessons/`**, aimed at the step that delegates (`develop/develop-loop`), tells that step to use your agent and what to hand it. See [Playbooks → Lessons](playbook.md#lessons).

The agent's own prompt is yours to write — booping never shapes it.

You invoke an agent by its bare name through the `Agent` tool (`subagent_type="<id>"`). Any agent file you drop into `~/.claude/agents/` is registered for every project automatically; if you add it mid-session, start a new session to pick it up.

See [Project config](project_config.md) for the config-merge rules and [Vault](vault.md) for where lessons live.

## How to disable internal agents

booping's built-in agents (`booping-developer`, `booping-researcher`) stay available to every playbook by default. When you want your external agent to be the *only* worker a playbook delegates to, the built-ins can compete against it and the playbook may pick a built-in when you wanted yours.

Set `core.{name}_playbook.disable_internal_agents: true` on that block. This leaves only the agents you registered yourself, so the delegation table always points at your external agent. The flag (and the per-agent `internal` marker it filters on) is documented in the [`agents` key tour](project_config.md#corename_playbookagents).

## Level 1 — Connect an external Claude Code agent

The simplest case: a plain global Claude Code agent — same kind booping ships, just yours. Maybe it carries different instructions, or runs on a cheaper model like haiku. You want a playbook (say `develop`) to use it to write code.

**1. Create the agent** at `~/.claude/agents/haiku-developer.md`:

```markdown
---
name: haiku-developer
description: Lightweight developer worker for small, well-scoped coding briefings. Use from the develop playbook when the milestone group is simple enough to run on a cheaper model.
tools: Read, Write, Edit, Bash
model: haiku
---

You implement the milestone(s) in the briefing the skill hands you.
Stay within the related files listed. Report back in milestone format.

[...your workflow, hard rules, report format...]
```

**2. Register it** in `~/Claude/{project}/config.yaml`:

```yaml
core:
  develop_playbook:
    agents:
      haiku-developer:
        good_for:
          - "Small, well-scoped milestone groups where a cheaper model is enough"
        bad_for:
          - "Large or tricky changes that need the stronger built-in worker"
```

**3. Tell the playbook to use it** — write a targeted lesson at `~/Claude/{project}/_lessons/0001_prefer-haiku-developer.md`:

```markdown
---
title: Prefer haiku-developer for small groups
targets:
  - develop/develop-loop
---

For small, well-scoped milestone groups, delegate to `haiku-developer`
(`subagent_type="haiku-developer"`). Brief it with the request, the related
files, and the DoD + Verify pasted from the plan. Its returned message is the
milestone report.
```

That's the whole integration — no CLI, no script.

## Level 2 — Wrap an external CLI worker

To delegate to an external CLI (for example, a headless coding CLI), front it with a Claude Code agent.

The split is what makes this work:

- **The agent owns the interaction.** It takes the briefing, drives the external CLI, validates the result against the briefing's definition of done, and reports back in milestone format. All CLI trivia (flags, model selection, retries) lives in the agent body, which you author.
- **A targeted lesson shapes the briefing.** A lesson aimed at the delegating step tells that step which fields to pass and how to invoke the agent — the agent itself only knows how to drive its backend, not what a given step should hand over.

When the backend needs more orchestration than a single command (a server, a browser, readiness checks), put that trivia in a global transport script under `~/.claude/bin/` and have the agent call the script instead of reimplementing it. Case (a) below is that shape; case (b) drives a CLI directly.

### Step by step

1. Create a global agent at `~/.claude/agents/<id>.md` that drives your CLI and reports in milestone format.
2. Ask Claude to wire the agent into the target playbook's config — you should end up with a `core.{name}_playbook.agents.<id>` block like the examples below.
3. Ask Claude to shape the briefing — a targeted lesson in `_lessons/` aimed at the delegating step.
4. Test it: run the playbook and confirm it delegates to your agent.

## Level 3 — Go-to examples

Two reference recipes you can adapt.

### (a) `plannotator-reviewer` — browser code review

A bespoke agent that drives a browser review surface, wired into the [code-review playbook](code_review.md). The agent fronts a global transport script (`~/.claude/bin/booping-plannotator-review`) that launches the review, seeds findings, opens the browser, and blocks until the human submits.

**Global agent — `~/.claude/agents/plannotator-reviewer.md`**

```markdown
---
name: plannotator-reviewer
description: Seeds booping code-review findings into a Plannotator browser review, lets a human review code + AI comments together, and returns their feedback.
tools: Read, Write, Bash
model: sonnet
---

You drive the Plannotator browser review surface for booping's code-review
playbook. You own only the *interaction*: map findings to Plannotator's
annotation contract, run the transport script, and return the human's feedback.

All transport trivia (port, launch, readiness, curl, exit codes) lives in
`~/.claude/bin/booping-plannotator-review` — do not reimplement it.

[...mapping table, procedure, report contract...]
```

The agent body maps booping findings to the annotation contract, writes the batch to a temp file, runs `~/.claude/bin/booping-plannotator-review {ref} {batch.json}`, and returns the human's feedback verbatim. The playbook, not the agent, owns the vault: it records that verdict in the run's `codereviews/` artifact.

**Vault config — `~/Claude/{project}/config.yaml`**

```yaml
core:
  code_review_playbook:
    agents:
      plannotator-reviewer:
        good_for:
          - "Interactive browser review of a diff with AI findings pre-seeded; human confirms/dismisses inline and feedback returns to the harness"
        bad_for:
          - "Headless / CI runs, no display available, or a quick chat-only review"
```

### (b) `pi-developer` — CLI delegation

A headless one-shot CLI worker, wired into the [develop playbook](develop.md). There is no transport script — the agent runs the external CLI (`pi --print …`) directly via its own `Bash`.

**Global agent — `~/.claude/agents/pi-developer.md`**

```markdown
---
name: pi-developer
description: Developer worker that implements a milestone group by driving the pi headless CLI (one-shot, non-interactive). Use from the develop playbook when delegating a coding briefing to the external pi worker instead of the built-in booping-developer.
tools: Read, Bash
model: sonnet
---

You implement a milestone group by driving the `pi` headless CLI. You own only
the *interaction*: take the briefing, hand it to `pi`, validate the result
against the briefing's DoD/Verify, retry once on shortfall, and report in
milestone format.

`pi` is a one-shot, non-interactive command. You run it directly via Bash:
`pi --print --provider ollama-cloud --model kimi-k2.6 "$(cat "$brief")"`

[...procedure, hard rules, report format...]
```

The agent body writes the briefing to a temp file, runs the pinned `pi` invocation, checks `git status --porcelain` against the briefing's DoD, retries once with a correction on shortfall, and reports in the standard milestone format.

**Vault config — `~/Claude/{project}/config.yaml`**

```yaml
core:
  develop_playbook:
    agents:
      pi-developer:
        good_for:
          - "Implementing a milestone group via the headless pi CLI (one-shot, non-interactive) — the preferred worker for coding tasks in this repo"
        bad_for:
          - "Drift spot-checks or non-coding reads — those stay in the skill or go to booping-researcher"
```

**Targeted lesson — `~/Claude/{project}/_lessons/0002_brief-pi-developer.md`**

```markdown
---
title: Briefing the pi-developer worker
targets:
  - develop/develop-loop
---

For this project, prefer `pi-developer` for milestone-group implementation.

When you delegate, invoke `pi-developer` (`subagent_type="pi-developer"`) and
brief it with:
- the request for each milestone in the group,
- the related files to touch / read,
- the DoD for each milestone (paste verbatim from the plan),
- the Verify commands (paste verbatim from the plan),
- project / stack context.

The agent's returned message is its milestone report — verify from it as usual.
```
