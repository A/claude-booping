# Integrating external agents

booping ships with built-in worker agents (`booping-developer`, `booping-researcher`). You can extend any skill to delegate to **your own** agent instead — a headless CLI worker, a browser review surface, a remote model, anything you can drive from a Claude Code subagent.

The whole integration is config + a self-contained agent file. There is no build step, no code change in the plugin, and no restart.

## The pattern

An external agent is wired in three pieces:

1. **A self-contained global agent** at `~/.claude/agents/<id>.md`. A normal Claude Code subagent definition: frontmatter (`name`, `description`, `tools`, `model`, …) plus a body that owns the *interaction* — take a briefing, drive whatever external thing the agent fronts (a CLI, a script, a service), validate the result, and report. Because it lives under `~/.claude/agents/`, Claude Code registers it for every project and you invoke it by its bare name via the `Agent` tool (`subagent_type="<id>"`).

2. **Vault config registration** in `~/Claude/{project}/config.yaml`, under `skills.<name>.agents.<id>`. The entry is **plain** — just `good_for` / `bad_for` bullets (and an optional `disable_internal_agents` on the skill). No `type`, no `command`, no `internal`. This is what makes the agent show up in the skill's *Available Agents* table, so the orchestrator knows when to reach for it.

3. **A skill extension** at `~/Claude/{project}/_booping/skill_<name>.md` that shapes the briefing: which fields to pass, how to invoke (`subagent_type="<id>"`), how to read the returned message, and what fallback to take if the agent is absent or fails.

The skill's *Available Agents* table is rendered from config by `_available_agents.j2`. A plain (non-internal) entry renders as a bare `subagent_type="<id>"` invocation — exactly how your global agent is registered. Nothing else is required: no generated wrapper, no `/compile`, no restart.

### `good_for` / `bad_for`

These bullets steer the orchestrator's delegation choice. `good_for` lists the work this agent is the right tool for; `bad_for` lists work to keep in the skill or route elsewhere. Write them from the skill's point of view — "when should `/develop` pick this over `booping-developer`?"

### `disable_internal_agents`

Set `skills.<name>.disable_internal_agents: true` to hide booping's built-in agents from that skill's table, leaving only the agents you explicitly registered. Use it when your external agent should be the *only* worker the skill ever delegates to.

### The extension channel

`_booping/skill_<name>.md` is loaded into the skill's context at invocation time. It is where you tell the orchestrator *how* to brief and invoke your agent — the agent file itself only knows how to drive its backend, not which fields a given skill should hand over. The two together form the contract: the skill extension shapes the request, the agent body fulfils it.

See [Project config](project_config.md) for the config merge mechanics and [Vault](vault.md) for the extension-file conventions.

## Case A — `plannotator-reviewer` (browser review, transport script)

A bespoke agent that drives a browser review surface, wired into [/code-review](code_review.md). The agent fronts a global transport script (`~/.claude/bin/booping-plannotator-review`) that launches the review, seeds findings, opens the browser, and blocks until the human submits.

### Global agent — `~/.claude/agents/plannotator-reviewer.md`

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

The agent body maps booping findings to the annotation contract, writes the batch to a temp file, runs `~/.claude/bin/booping-plannotator-review <ref> <batch.json>`, and returns the human's feedback verbatim. On a degraded exit code it returns a `SURFACE UNAVAILABLE` signal instead of erroring, so the caller can fall back to chat-only.

### Vault config — `~/Claude/{project}/config.yaml`

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

### Skill extension — `~/Claude/{project}/_booping/skill_code-review.md`

Tells `/code-review` to route *every* diff through the browser instead of printing findings in chat:

```markdown
### Plannotator browser review — required surface

This project reviews every diff in Plannotator, never in chat.
`plannotator-reviewer` is a required agent: if it is not in the Available
Agents table, stop and tell the user. Do not fall back to a chat-only review.

After findings are computed, delegate to `plannotator-reviewer` via the
`Agent` tool (`subagent_type="plannotator-reviewer"`). Brief it with:
- the resolved diff ref (PR URL, or a non-URL token like `HEAD`),
- the repo path to run in,
- every finding as `file:lineStart[-lineEnd] · side · severity · snippet · fix · rationale`.

The agent's returned message is the human's feedback — proceed from it directly.
If it returns a `SURFACE UNAVAILABLE` signal, surface the failure and stop.
```

## Case B — `pi-developer` (headless CLI worker, agent-only)

A headless one-shot CLI worker, wired into [/develop](develop.md). Unlike Case A there is **no transport script** — the agent runs the external CLI (`pi-agent --print …`) directly via its own `Bash`. The whole integration is the agent file plus config plus the skill extension.

### Install step

Drop the agent file into `~/.claude/agents/`:

```bash
cp pi-developer.md ~/.claude/agents/pi-developer.md
```

That is the entire install. Claude Code registers every `~/.claude/agents/*.md` at startup, so the next session sees `pi-developer` as an invokable subagent. (If you add the file mid-session, start a new session to pick it up.)

### Global agent — `~/.claude/agents/pi-developer.md`

```markdown
---
name: pi-developer
description: Developer worker that implements a milestone group by driving the pi-agent headless CLI (one-shot, non-interactive). Use from /develop when delegating a coding briefing to the external pi-agent worker instead of the built-in booping-developer.
tools: Read, Bash
model: sonnet
---

You implement a milestone group by driving the `pi-agent` headless CLI. You own
only the *interaction*: take the briefing, hand it to `pi-agent`, validate the
result against the briefing's DoD/Verify, retry once on shortfall, and report in
milestone format.

`pi-agent` is a one-shot, non-interactive command. You run it directly via Bash:
`pi-agent --print --provider ollama-cloud --model kimi-k2.6 "$(cat "$brief")"`

[...procedure, hard rules, report format...]
```

The agent body writes the briefing to a temp file, runs the pinned `pi-agent` invocation, checks `git status --porcelain` against the briefing's DoD, retries once with a correction on shortfall, and reports in the standard milestone format. On a runtime failure it returns a `PI-AGENT FAILED` signal so the caller can fall back to `booping-developer`.

### Vault config — `~/Claude/{project}/config.yaml`

```yaml
skills:
  develop:
    agents:
      pi-developer:
        good_for:
          - "Implementing a milestone group via the headless pi-agent CLI (one-shot, non-interactive) — the preferred worker for coding tasks in this repo"
        bad_for:
          - "Drift spot-checks or non-coding reads — those stay in the skill or go to booping-researcher"
          - "When pi-agent is unavailable at runtime — fall back to booping-developer"
```

### Skill extension — `~/Claude/{project}/_booping/skill_develop.md`

Tells `/develop` to prefer `pi-developer` for implementation and how to brief it:

```markdown
### Briefing the pi-developer worker

For this project, prefer `pi-developer` for milestone-group implementation.

When you delegate, invoke `pi-developer` via the `Agent` tool
(`subagent_type="pi-developer"`) and brief it with:
- the request for each milestone in the group,
- the related files to touch / read,
- the DoD for each milestone (paste verbatim from the plan),
- the Verify commands (paste verbatim from the plan),
- project / stack context.

The agent's returned message is its milestone report — verify from it as usual.

Fallback: if pi-developer is not in the Available Agents table, or it returns a
`PI-AGENT FAILED` signal, fall back to the built-in `booping-developer`.
```

## Choosing between the two shapes

- **Agent-only (Case B)** — the agent drives a single CLI command directly. Simplest: one file, no script. Use when the backend is a self-contained command.
- **Transport script (Case A)** — a global `~/.claude/bin/<script>` carries the connection/launch/readiness/exit-code trivia, and the agent only owns the findings-to-contract mapping and the report. Use when the backend needs orchestration (a server, a browser, retries) you don't want to bury in the agent prose.

Either way the harness side is identical: a plain `skills.<name>.agents.<id>` config block plus a `_booping/skill_<name>.md` extension. The agent is yours to write; booping just renders it into the skill's delegation table.
