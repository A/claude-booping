# Any CLI can be a playbook worker

booping's playbooks delegate work through Claude Code's `Agent` tool: develop hands a milestone to a worker agent, code-review hands a diff to a reviewer. Out of the box those workers are Claude agents — but the delegation seam only cares that *something* takes a briefing and returns a report, so any external agent with a CLI (Codex, a headless pi session, an in-house tool) can sit behind it.

The trick is the **agent-proxy pattern**. Rather than teach a playbook about your external tool, you write a thin proxy agent in `~/.claude/agents/` whose only job is to relay the briefing to the external CLI and return its report, then point the playbook's agent slot at the proxy via vault config. The playbook sees no change — it invokes an agent by name and reads a report back. Everything specific to the external tool lives in the proxy's body, which you author.

Two real proxies below: a minimal relay to Codex, and a full develop worker backed by a headless pi session. The dry mechanics — config merge rules, the lesson system, disabling built-in agents — live in [Integrating external agents](../integrating-external-agents.md); this page shows the shape in motion.

## The pattern in one picture

Every proxy integration is the same two files:

1. **The proxy agent** — a markdown file at `~/.claude/agents/{id}.md`. Frontmatter declares the name, a description that tells playbooks when to pick it, and a small tool set (usually just `Bash` and `Read` — a relay doesn't edit code). The body is the relay procedure: take the briefing, hand it to the external CLI, collect the output, report back. Files there register globally for every project; a new Claude Code session picks them up.
2. **The vault config entry** — a block under `core.{name}_playbook.agents.{id}` in `~/Claude/{project}/config.yaml` (or your repo-local vault's). The playbook's agent slot: it puts your proxy into that playbook's delegation table, with `good_for` / `bad_for` bullets steering when it gets picked.

That's the whole surface. No plugin edits, no scripts inside booping — the proxy and the config entry are both userland.

## Worked example 1 — a thin relay to Codex

The simplest possible proxy: an agent that hands its prompt to `codex exec` and returns whatever Codex says, verbatim. It runs on a cheap model because it does no thinking of its own.

`~/.claude/agents/codex.md`:

```markdown
---
name: codex
description: Thin relay to the Codex CLI. Takes a prompt, runs `codex exec` non-interactively in the caller's working directory, and returns Codex's output verbatim. Use when the user asks to delegate a task or question to Codex.
tools: Bash, Read
model: haiku
---

You are a thin relay to the `codex` CLI. You do not solve the task yourself — you hand the prompt to Codex, capture its output, and report it back.

1. Write the prompt you received verbatim to a temp file (avoids shell-quoting issues):
   p="$(mktemp)"; cat > "$p" <<'CODEX_PROMPT_EOF' ... CODEX_PROMPT_EOF
2. Run Codex non-interactively, reading the prompt from stdin:
   codex exec - < "$p"
3. If the caller asked for file changes, run `git status --porcelain` and include the changed-file list in your report.

Hard rules: always `codex exec`, never an interactive session; pass the prompt through unmodified; never answer the task yourself; on failure report `CODEX FAILED (exit {code}): {exact stderr}` instead of inventing output.
```

Three details carry most of the weight, and they recur in every proxy you'll write:

- **The prompt goes through a temp file, not a shell argument.** Briefings contain quotes, backticks, and newlines; `cat > "$p" <<'EOF'` sidesteps all of it.
- **The relay is forbidden from doing the work itself.** Without that rule, the proxy's own model happily answers easy questions and you never find out your external tool was down.
- **Failure is reported, never papered over.** A non-zero exit comes back as an explicit `FAILED` line with the real stderr — the caller decides what to do with it.

This agent isn't wired to a playbook slot — it's a general-purpose relay you invoke by name. To make a playbook prefer it, add the config entry shown in the next example.

## Worked example 2 — a milestone handed to a headless pi session

The Codex relay forwards a prompt and comes straight back. `pi-developer` does the same relay job for a much bigger unit of work: an entire develop milestone, executed by a headless pi session that does its own planning, delegation and validation. The proxy still never edits code and never writes the method — it hands over file links and waits.

`~/.claude/agents/pi-developer.md` (abridged to the load-bearing parts):

```markdown
---
name: pi-developer
description: Hands a milestone to a headless pi session and returns pi's report. pi does the planning, delegation and validation itself.
tools: Read, Bash
model: opus
---

Hand one milestone to pi and return its report. You never edit code — pi's own agents own that.

1. Start it detached; the wrapper returns at once with log/out/err/status paths:
   ~/.claude/bin/pi-developer -D -C {workdir} [--model {model}] \
     "/loop implement {milestone-path}, part of the plan {index-path}"
2. Poll until done:  ~/.claude/bin/pi-developer --status {status-path}
   On RUNNING, call it again. Repeat until DONE.
3. On DONE, read the report:  tail -40 {out-path}
   Return it, prefixed by one line naming the model.

pi commits nothing, by design: the work comes back as a working tree and whoever briefed you owns the commit.
```

Notice what the briefing is: **paths, not pasted content**. Develop briefs workers with the milestone file, the plan index and the workdir; pi has its own read tools and pulls what it needs. The proxy adds nothing and summarises nothing — the report is pi's own, and the develop runner validates it against the milestone's DoD exactly as it would a built-in worker's.

Two conventions here are worth stealing:

- **Long-running backends run detached, with a single sanctioned wait mechanism.** The wrapper script returns immediately with a status file; the proxy polls that file and nothing else. No `sleep` loops, no `pgrep` — a hand-rolled wait tends to watch itself instead of the run.
- **The external worker never commits.** In booping's develop lifecycle the runner owns git history; the proxy passes that rule through to pi, so the work arrives as an uncommitted working tree the runner can validate and commit with scoped staging.

When the backend needs orchestration beyond a single command — launching, readiness checks, log collection — that trivia belongs in a wrapper script (here `~/.claude/bin/pi-developer`), not in the agent body. The agent stays a readable procedure; the script owns the plumbing.

### Pointing develop at it

The config entry is the same shape for any proxy. In your vault's `config.yaml`:

```yaml
core:
  develop_playbook:
    agents:
      pi-developer:
        good_for:
          - "All development tasks — use instead of booping-developer"
        bad_for:
          - "Drift spot-checks or non-coding reads — those go to booping-researcher"
```

With that block in place, `pi-developer` shows up in the develop steps' Available Agents table and the playbook delegates milestones to it — zero edits to the plugin itself. The block name is the playbook name with `-` replaced by `_`, so a reviewer proxy registers under `core.code_review_playbook.agents`. The [`agents` key reference](../project_config.md) covers entry shape and merge rules.

## What generalizes

Strip the two examples down and the recipe is always:

1. Write a proxy at `~/.claude/agents/{id}.md`: relay the briefing (through a temp file), drive the CLI (directly, or via a wrapper script for anything stateful), return the backend's report without editorializing, and report failures as failures.
2. Register it in vault config under the target playbook's `core.{name}_playbook.agents.{id}` with honest `good_for` / `bad_for` bullets.
3. Start a fresh session and run the playbook — it delegates to your proxy like any other agent.

For briefing shaping via targeted lessons, hiding the built-in workers, and the full config-key tour, see [Integrating external agents](../integrating-external-agents.md).
