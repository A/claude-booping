# /compile

Regenerate the repo-local native wrapper agents for every `type: cli` agent, then restart Claude Code to pick them up.

## What it does

`/compile` is booping's **static-generation entrypoint**. Today it has one job: keep the generated cli-agent wrappers in sync with your config. Future static-update work lands under the same command.

It runs `booping compile`, which:

1. Resolves the attached repo from the project context and ensures `<repo>/.claude/agents/` exists.
2. Scans the merged config (`src/config.yaml` + `~/Claude/{project}/config.yaml`) for every `type: cli` agent.
3. Writes a native wrapper agent to `<repo>/.claude/agents/cli_agent_<id>.md` for each one, and **prunes** any `cli_agent_*.md` whose id is no longer configured.
4. Prints a per-id created / updated / removed diff and a final `Restart Claude Code to apply.` line.

The wrapper is a native Claude sub-agent (`subagent_type="cli_agent_<id>"`) that orchestrates the external worker: it calls `booping run-agent <id>`, validates the result against the briefing's Definition of Done, retries once on failure, and reports in the standard milestone format. See [CLI agent delegation](https://github.com/A/claude-booping/blob/main/docs/cli_agent_delegation.md) for the full mechanism.

## When to run it

Run `/compile` whenever the set of `type: cli` agents changes:

- You added, removed, or renamed a `type: cli` agent in `~/Claude/{project}/config.yaml`.
- You changed an agent's `good_for` / `bad_for` (these are baked into the wrapper body).
- A skill's Available Agents table tells you a cli agent is missing from the registry.

## Restart required

Claude Code scans its agent registry once at startup and freezes it for the session — there is no live file-watcher over the agent directories, and the `SessionStart` hook fires *after* the scan. A wrapper generated mid-session is therefore not invokable until the next launch. `/compile` always ends by telling you to restart; do it before delegating to a freshly generated cli agent.

The generated `cli_agent_*.md` files are gitignored by prefix. Hand-authored agents under `.claude/agents/` (which carry no `cli_agent_` prefix) stay tracked and are never touched by `compile`.

## Command

```text
/compile
```

No arguments. The skill surfaces `booping compile`'s output verbatim.
