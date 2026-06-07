# CLI agent delegation (experimental)

Route a skill's delegation to an external command-line worker (e.g. `pi --print`) instead of a native Claude Code subagent.

This is experimental — only the `/develop` skill currently delegates this way. Other skills ignore `type: cli` entries.

## How it works

A `type: cli` agent is fronted by a **generated native wrapper agent**. Skills invoke the wrapper like any native agent via the `Agent` tool (`subagent_type="cli_agent_<id>"`); they never call the external command directly. The wrapper encapsulates the orchestration: it calls `booping run-agent <id>` (the mechanical floor — see below), validates the worker's output against the briefing's Definition of Done, retries once with a correction on failure, and reports in the standard milestone format.

The wrappers are materialized by **`booping compile`** (exposed as the `/compile` skill), which renders one `<repo>/.claude/agents/cli_agent_<id>.md` per configured cli agent and prunes wrappers whose id is gone. The generated files are gitignored by their `cli_agent_` prefix; hand-authored agents (no prefix) stay tracked and untouched.

### Restart requirement

Claude Code scans its agent registry once at startup and freezes it for the session. A wrapper generated mid-session is not invokable until the next launch, so `/compile` always ends by telling you to **restart Claude Code to apply**. If a skill's Available Agents table reports that a cli agent is missing from the registry, run `/compile` and restart.

## Example: `pi-developer` under `/develop`

Drop this into `~/Claude/<project>/config.yaml` to route `/develop`'s worker to the `pi` CLI:

```yaml
skills:
  develop:
    # Make /develop see only the explicitly defined agents below.
    disable_internal_agents: true
    agents:
      # `pi-developer` is the agent id — e.g. used to look up the agent body
      # at `<vault>/_booping/agent_pi-developer.md`, and the generated wrapper's
      # registry name `cli_agent_pi-developer`.
      pi-developer:
        # `cli` makes this entry runnable as an external command instead of a
        # native Claude Code subagent.
        type: cli
        # Shell command to exec. `{{ prompt }}` is substituted with the final
        # prompt, safely quoted against any briefing content. Omit the
        # placeholder and the prompt is appended as the last positional arg.
        command: "pi --print {{ prompt }}"
        good_for:
          - "Implements one milestone group per invocation"
        bad_for:
          - "Exploratory questions or non-git work"
```

After editing config, run `/compile` and restart Claude Code. The agent then shows up in `/develop`'s Available Agents table as a native invocation (`subagent_type="cli_agent_pi-developer"`).

## Giving the agent a soul

The final prompt sent to the CLI is composed by `booping run-agent` from two pieces:

1. `~/Claude/<project>/_booping/agent_<id>.md` — the role / workflow / hard rules / report format the worker needs. This is the place to define how your CLI worker should behave: same content a native agent's body would carry.
2. The per-turn briefing handed in by the wrapper.

The extension file is optional but recommended — without it the worker only sees the briefing for the current turn.

## The mechanical floor: `booping run-agent`

`booping run-agent <id> --briefing-file <path>` is the unchanged mechanical layer the wrapper drives. It resolves the cli agent in merged config, prepends the soul + output contract to the briefing, execs the configured `command`, prints the worker's output plus a `--- changed files ---` trailer, and logs the invocation. It is also usable standalone for inspection. The wrapper, not the skill, is what calls it.
