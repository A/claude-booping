# Integrating external agents

booping ships with built-in worker agents (`booping-developer`, `booping-researcher`). You can also wire any skill to delegate to **your own** agent — a plain Claude Code agent with different instructions or a cheaper model, or a Claude Code agent that fronts an external CLI worker or a browser review surface.

Every integration comes down to two pieces of project config:

- **`skills.<name>.agents.<id>`** in your vault config (`~/Claude/{project}/config.yaml`) tells the skill which agents are available to it. Each entry carries `good_for` / `bad_for` bullets that guide the skill toward the right choice.
- **`_booping/skill_<name>.md`** is where you override or extend a skill's behavior — for example, to tell the skill to use your external agent and how to brief it.

You invoke an agent by its bare name through the `Agent` tool (`subagent_type="<id>"`). Any agent file you drop into `~/.claude/agents/` is registered for every project automatically; if you add it mid-session, start a new session to pick it up.

See [Project config](project_config.md) for the config-merge rules and [Vault](vault.md) for the extension-file conventions.

## How to disable internal agents

booping's built-in agents (`booping-developer`, `booping-researcher`) stay available to every skill by default. When you want your external agent to be the *only* worker a skill delegates to, the built-ins can compete against it and the skill may pick a built-in when you wanted yours.

Set `skills.<name>.disable_internal_agents: true` for that skill. This leaves only the agents you registered yourself, so the skill always reaches for your external agent.

## Level 1 — Connect an external Claude Code agent

The simplest case: a plain global Claude Code agent — same kind booping ships, just yours. Maybe it carries different instructions, or runs on a cheaper model like haiku. You want a skill (say `/develop`) to use it to write code.

**1. Create the agent** at `~/.claude/agents/haiku-developer.md`:

```markdown
---
name: haiku-developer
description: Lightweight developer worker for small, well-scoped coding briefings. Use from /develop when the milestone group is simple enough to run on a cheaper model.
tools: Read, Write, Edit, Bash
model: haiku
---

You implement the milestone(s) in the briefing the skill hands you.
Stay within the related files listed. Report back in milestone format.

[...your workflow, hard rules, report format...]
```

**2. Register it** in `~/Claude/{project}/config.yaml`:

```yaml
skills:
  develop:
    agents:
      haiku-developer:
        good_for:
          - "Small, well-scoped milestone groups where a cheaper model is enough"
        bad_for:
          - "Large or tricky changes that need the stronger built-in worker"
```

**3. Tell the skill to use it** in `~/Claude/{project}/_booping/skill_develop.md`:

```markdown
### Prefer haiku-developer for small groups

For small, well-scoped milestone groups, delegate to `haiku-developer`
(`subagent_type="haiku-developer"`). Brief it with the request, the related
files, and the DoD + Verify pasted from the plan. Its returned message is the
milestone report.
```

That's the whole integration — no CLI, no script.

## Level 2 — Wrap an external CLI worker

To delegate to an external CLI (for example, a headless coding CLI), front it with a Claude Code agent.

The split is what makes this work:

- **The agent owns the interaction.** It takes the briefing, drives the external CLI, validates the result against the briefing's definition of done, and reports back in milestone format. All CLI trivia (flags, model selection, retries) lives in the agent body.
- **The skill extension shapes the briefing.** `_booping/skill_<name>.md` tells the skill which fields to pass and how to invoke the agent — the agent itself only knows how to drive its backend, not what a given skill should hand over.

When the backend needs more orchestration than a single command (a server, a browser, readiness checks), put that trivia in a global transport script under `~/.claude/bin/` and have the agent call the script instead of reimplementing it. Case (a) below is that shape; case (b) drives a CLI directly.

### Step by step

1. Create a global agent at `~/.claude/agents/<id>.md` that drives your CLI and reports in milestone format.
2. Ask Claude to wire the agent into the target skill's config — you should end up with a `skills.<name>.agents.<id>` block like the examples below.
3. Ask Claude to update the skill's extra instructions (`_booping/skill_<name>.md`) to shape the briefing.
4. Test it: run the skill and confirm it delegates to your agent.

## Level 3 — Go-to examples

Two reference recipes you can adapt.

### (a) `plannotator-reviewer` — browser code review

A bespoke agent that drives a browser review surface, wired into [/code-review](code_review.md). The agent fronts a global transport script (`~/.claude/bin/booping-plannotator-review`) that launches the review, seeds findings, opens the browser, and blocks until the human submits.

**Global agent — `~/.claude/agents/plannotator-reviewer.md`**

```markdown
---
name: plannotator-reviewer
description: Seeds booping /code-review findings into a Plannotator browser review, lets a human review code + AI comments together, and returns their feedback.
tools: Read, Write, Bash
model: sonnet
---

You drive the Plannotator browser review surface for booping's `/code-review`.
You own only the *interaction*: map findings to Plannotator's annotation
contract, run the transport script, and return the human's feedback.

All transport trivia (port, launch, readiness, curl, exit codes) lives in
`~/.claude/bin/booping-plannotator-review` — do not reimplement it.

[...mapping table, procedure, report contract...]
```

The agent body maps booping findings to the annotation contract, writes the batch to a temp file, runs `~/.claude/bin/booping-plannotator-review <ref> <batch.json>`, and returns the human's feedback verbatim.

**Vault config — `~/Claude/{project}/config.yaml`**

```yaml
skills:
  code-review:
    agents:
      plannotator-reviewer:
        good_for:
          - "Interactive browser review of a diff with AI findings pre-seeded; human confirms/dismisses inline and feedback returns to the harness"
        bad_for:
          - "Headless / CI runs, no display available, or a quick chat-only review"
```

**Skill extension — `~/Claude/{project}/_booping/skill_code-review.md`**

```markdown
### Plannotator browser review — required surface

This project reviews every diff in Plannotator, never in chat.

After findings are computed, delegate to `plannotator-reviewer`
(`subagent_type="plannotator-reviewer"`). Brief it with:
- the resolved diff ref (PR URL, or a non-URL token like `HEAD`),
- the repo path to run in,
- every finding as `file:lineStart[-lineEnd] · side · severity · snippet · fix · rationale`.

The agent's returned message is the human's feedback — proceed from it directly.
```

### (b) `pi-developer` — CLI delegation

A headless one-shot CLI worker, wired into [/develop](develop.md). There is no transport script — the agent runs the external CLI (`pi --print …`) directly via its own `Bash`.

**Global agent — `~/.claude/agents/pi-developer.md`**

```markdown
---
name: pi-developer
description: Developer worker that implements a milestone group by driving the pi headless CLI (one-shot, non-interactive). Use from /develop when delegating a coding briefing to the external pi worker instead of the built-in booping-developer.
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
skills:
  develop:
    agents:
      pi-developer:
        good_for:
          - "Implementing a milestone group via the headless pi CLI (one-shot, non-interactive) — the preferred worker for coding tasks in this repo"
        bad_for:
          - "Drift spot-checks or non-coding reads — those stay in the skill or go to booping-researcher"
```

**Skill extension — `~/Claude/{project}/_booping/skill_develop.md`**

```markdown
### Briefing the pi-developer worker

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
