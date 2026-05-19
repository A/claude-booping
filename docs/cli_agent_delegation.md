# CLI agent delegation

How to route a skill's delegation to an external command-line worker (e.g. `pi --print`) instead of a native Claude Code subagent, while keeping the per-project extension channel that `/learn` writes to.

Currently wired for `/develop` only.

## Schema

Per-agent config lives under `skills.<name>.agents.<id>` in `src/config.yaml` (or its project override at `~/Claude/<project>/config.yaml`).

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `type` | `"agent"` \| `"cli"` | no (default `"agent"`) | Discriminator. `agent` = native Claude Code subagent invoked via the `Agent` tool. `cli` = external command invoked via `booping run-agent <id>`. |
| `command` | string | yes when `type: "cli"` | Jinja2 template for the shell command. May reference `{{ prompt }}` (the final, `shlex.quote`-d prompt). When absent, the quoted prompt is appended as the last positional arg. |
| `internal` | bool | no (default `false`) | Marks an entry as built-in (e.g. `booping-developer`, `booping-researcher`). Filtered out of the rendered roster when the skill has `disable_internal_agents: true`. |
| `good_for` / `bad_for` | list[str] | no | Delegation guidance rendered into the skill body. |

Per-skill flag (sibling of `agents`):

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `disable_internal_agents` | bool | `false` | When `true`, the `_available_agents.j2` macro skips `internal: true` entries for this skill. Lets a project run on cli workers only. |

## `booping run-agent <id>` invocation contract

```
cat briefing.md | booping run-agent <id>
# or
booping run-agent <id> --briefing-file path/to/briefing.md
```

Steps:

1. Resolve `<id>` from the merged config across all `skills.*.agents`. First match wins. Hard-errors (exit 2) on missing id, `internal: true`, or `type: agent`.
2. Read the briefing from stdin (or `--briefing-file PATH`). If stdin is a TTY and no `--briefing-file` is given, exits 2 with a one-line stderr (prevents indefinite hang in interactive shells).
3. Read the extension from `<vault>/_booping/agent_<id>.md` if present. Absent or empty is fine.
4. Compose the final prompt: `extension + "\n\n---\n\n" + briefing`. When the extension is absent or empty, the briefing alone is passed — no separator, no preamble.
5. Render `command` as a Jinja2 template with one variable `prompt = shlex.quote(final_prompt)`. When `command` contains no `{{ prompt }}` substring, append the quoted prompt as the last positional arg.
6. `subprocess.run(shlex.split(rendered_command), check=False, shell=False)`. stdout/stderr stream to the caller; exit code propagates.

## `command` template + `{{ prompt }}` semantics

The prompt is `shlex.quote`-d **before** substitution, so shell metacharacters in the briefing (`$VAR`, backticks, quotes, newlines) cannot break out of their argument. You are responsible for the surrounding shell syntax in `command`.

**No placeholder** — simplest shape. The quoted prompt is appended as the last positional arg:

```yaml
command: "pi --print"
```

becomes `pi --print '<final-prompt>'`.

**Explicit placement** — to put the prompt mid-command, use a shell-of-shells shape so the prompt survives quoting as a single arg:

```yaml
command: 'sh -c "printf %s \"$1\"" -- {{ prompt }}'
```

**Stdin pipe via `sh -c`** — when the underlying tool wants the prompt on stdin:

```yaml
command: 'sh -c "echo {{ prompt }} | my-tool --read-stdin"'
```

## Final-prompt composition

Extension first (role / project context from `/learn`-emitted `_booping/agent_<id>.md`), then a `\n\n---\n\n` separator, then the briefing. When the extension file is absent or empty, the briefing alone is passed — no separator, no preamble.

## v1 limitation: no rendered body for cli agents

Native agents (e.g. `booping-developer`) carry a baked-in role + workflow + hard-rules + report-format body (`src/templates/_partials/_developer_body.j2`) at render time. **cli agents have no such body.** The single channel between booping and a cli worker is the extension file at `<vault>/_booping/agent_<id>.md` (and the briefing for the current turn).

That file must carry **the full role context** the worker needs: workflow, hard rules, report format, project conventions. Anything you'd expect a native agent's body to contain belongs there.

Future direction: a per-cli-agent body partial. Out of scope today.

## pi-bundle example

Add `pi-mesh` as a cli worker under `/develop` and disable the native developer:

```yaml
# ~/Claude/<project>/config.yaml
skills:
  develop:
    disable_internal_agents: true
    agents:
      pi-mesh:
        type: cli
        command: "pi --print"
        good_for:
          - "Concrete code change in a git-tracked project"
        bad_for:
          - "Exploratory questions or dirty/non-git repos"
```

Two follow-ups the user owns (out of scope here):

- Install `pi` per its own bundle's `INSTALL.md`.
- Write `<vault>/_booping/agent_pi-mesh.md` carrying the full role context (see "v1 limitation" above).

## Long-running command guidance

When the underlying cli runs for more than a few seconds (agent loops, multi-step LLM calls), the orchestrator should invoke `booping run-agent <id>` via the `Bash` tool with `run_in_background: true`, then poll output via `BashOutput`. Do not synchronously block on a multi-minute command in the foreground.
