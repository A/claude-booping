# CLI agent delegation (experimental)

Route a skill's delegation to an external command-line worker (e.g. `pi --print`) instead of a native Claude Code subagent.

This is experimental — only the `/develop` skill currently delegates this way. Other skills ignore `type: cli` entries.

## Example: `pi-developer` under `/develop`

Drop this into `~/Claude/<project>/config.yaml` to route `/develop`'s worker to the `pi` CLI:

```yaml
skills:
  develop:
    # Hide the built-in agents so /develop only sees this cli worker.
    disable_internal_agents: true
    agents:
      pi-developer:
        # `cli` makes this entry runnable as an external command instead of a
        # native Claude Code subagent.
        type: cli
        # Shell command to exec. `{{ prompt }}` is substituted with the
        # `shlex.quote`-d final prompt — safe against any briefing content.
        # Omit the placeholder and the quoted prompt is appended as the last
        # positional arg.
        command: "pi --print {{ prompt }}"
        good_for:
          - "Implements one milestone group per invocation"
        bad_for:
          - "Exploratory questions or non-git work"
```

The agent shows up in `/develop`'s Available Agents table; the orchestrator pipes the briefing to it on stdin.

## Giving the agent a soul

The final prompt sent to the CLI is composed from two pieces:

1. `~/Claude/<project>/_booping/agent_<id>.md` — the role / workflow / hard rules / report format the worker needs. This is the place to define how your CLI worker should behave: same content a native agent's body would carry.
2. The per-turn briefing handed in by `/develop`.

The extension file is optional but recommended — without it the worker only sees the briefing for the current turn.
