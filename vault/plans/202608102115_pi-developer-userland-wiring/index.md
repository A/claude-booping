---
title: "Userland pi-developer wiring — develop milestones via local pi worker"
type: "feature"
status: done
sp: 7
related_to: null
created: 2026-08-10 21:16
planned: null
started: 2026-08-11 11:39
completed: 2026-08-11 13:24
code_reviews: []
sessions:
- b5e708f2-eefd-4d33-a843-4ce4194817fa
- c1b856d7-de92-4a5c-89e5-f94d22fafe04
retro: null
summary: pi-developer proxy agent drives ~/.bin/pi-developer (Qwen3-Coder-Next) 
  as develop's milestone worker via vault config
commit: 6f7f781f26ac8002f8d6f6e498453409690f21ac
reviewed_at: 2026-08-11 11:34
metrics_active_minutes: 116
metrics_models:
- claude-fable-5
metrics_tokens_input: 282
metrics_tokens_output: 129943
metrics_tokens_cache_creation: 696885
metrics_tokens_cache_read: 11453333
---

# Userland pi-developer wiring — develop milestones via local pi worker

## Context

The develop playbook delegates each milestone group to the plugin-shipped `booping:booping-developer` agent — a Claude worker on paid API. A local worker path already exists in pieces: `~/.bin/pi-developer` runs headless `pi` pinned to the llama-swap box at `http://10.0.0.106:8080` with a scrubbed environment (only `ollama-local` can authenticate), and the stale `~/.claude/agents/pi-developer.md` agent still drives the retired `pi-agent --provider ollama-cloud --model glm-5.1` invocation and is used nowhere.

After this plan, `~/.claude/agents/pi-developer.md` is a compact proxy: it takes develop's path-based briefing, composes the pi worker's prompt (rendered booping developer body + the briefing's paths), runs `~/.bin/pi-developer` with model `Qwen3-Coder-Next`, validates the result against the milestone's DoD/Verify, retries once, and reports in the milestone format the runner parses. Develop picks it up through the vault config's `core.develop_playbook.agents` map — the external-agent mechanism `documentation/integrating-external-agents.md` case (b) documents — with zero edits to core claude-booping files.

## Decisions

- **Proxy pattern**: the Claude-side agent carries only interaction logic — compose prompt, invoke script, validate, retry once, report. All *worker* instruction content comes from the rendered booping developer body, so the pi worker follows the same contract `booping-developer` does and the two never drift — one source (user-confirmed: proxy body compact, worker prompt = agent body + inputs).
- **Prompt composition**: the proxy renders the worker body with `/home/anton/Dev/@A/claude-booping/bin/booping render src/templates/agents/booping-developer.md.j2` (run from the plugin repo root — verified to render cleanly), writes it to a `mktemp` file, and appends the briefing's `## Inputs` block with **absolute paths**. `pi` has read/edit tools and reads the milestone file, feedback and index itself — paths, never pasted bodies, matching develop's own briefing contract.
- **Pinned invocation**: `~/.bin/pi-developer -f {prompt-file} -m Qwen3-Coder-Next -C {workdir}` — model id verified live on the box (`curl /v1/models`). Retry-on-shortfall exactly once via `--continue` (verified in `pi --help`; the script forwards unrecognized options verbatim). Endpoint, provider and env scrubbing stay the script's business — the agent never sets them.
- **Config tier**: vault config (`{vault}/config.yaml`) first; promotion to global `~/.config/booping/config.yaml` is a later, separate step once the wiring proves out (user-confirmed). Entry shape mirrors the core `agents.*` entries minus `internal:`.
- **Selection**: `good_for` reads "all development tasks — use instead of booping-developer" (user's wording). Internal agents stay enabled — no `disable_internal_agents` — because `core.develop_playbook.fallback_agent` still points at `booping:booping-developer` for fix briefings, and researcher delegation is untouched.
- **Commit semantics**: `~/.claude/agents/pi-developer.md` lives outside any git repo — that milestone's report says `Commit: none (file outside repository)` explicitly, so the runner's commit validation reads it from the contract instead of failing it. The vault-config milestone commits normally (repo-local vault).
- **Report format**: the proxy reports in the exact `## Milestone {id}` / `Files touched:` / `Verify:` / `Commit:` format the rendered developer body defines — no new format is invented.
- **Hardcoded userland paths**: absolute `/home/anton/...` paths in the agent body are acceptable — this is single-user wiring, not shippable plugin content.
- **No lesson file**: selection is steered by `good_for` alone; develop's default briefing already carries everything the proxy needs (paths + workdir), so no `develop/develop-loop`-targeted lesson is written.

## Architecture

```
develop/develop-loop
  briefing (paths: milestone contract, feedback?, index.md, CLAUDE.md; workdir; return contract)
    → Agent(subagent_type="pi-developer")            # ~/.claude/agents/pi-developer.md — proxy
        1. render worker body:  bin/booping render src/templates/agents/booping-developer.md.j2
        2. prompt file (mktemp) = rendered body + briefing paths block
        3. ~/.bin/pi-developer -f {prompt} -m Qwen3-Coder-Next -C {workdir}
             → pi --print --provider ollama-local --model Qwen3-Coder-Next   (env-scrubbed)
               → reads milestone/index, edits repo code, runs ## Verify, commits
        4. validate: git status/log + stdout vs the milestone's DoD/Verify
        5. shortfall → one corrective re-run with --continue; then report
    → milestone-format report → runner validates diff vs DoD, flips checkboxes, transitions
```

Load-time inputs: `core.develop_playbook.agents` (vault tier) feeds the develop steps' Available Agents table; the proxy agent file auto-registers from `~/.claude/agents/` (new Claude Code session required after creation).

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [Rewrite the pi-developer proxy agent](milestones/M01-proxy-agent-rewrite/M01-proxy-agent-rewrite.md) | 3 | done |
| 02 | [Wire pi-developer into develop via vault config](milestones/M02-vault-config-wiring/M02-vault-config-wiring.md) | 2 | done |
| 03 | [End-to-end smoke through the proxy path](milestones/M03-e2e-smoke/M03-e2e-smoke.md) | 2 | done |

## Final Verification

- [ ] `booping render-playbook develop` lists `pi-developer` in every step's Available Agents table with the intended `good_for`/`bad_for`, and core files show no diff (`git status` in the plugin repo touches only `vault/`).
- [ ] Fresh-session check: `pi-developer` appears as an available agent type and its body matches the rewritten file.
- [ ] End-to-end receipt from M03 reviewed: scratch-repo commit made by the pi worker, proxy report in milestone format, validation caught the seeded shortfall.

## Out of scope

- No global-config promotion (`~/.config/booping/config.yaml`) — a later step after the wiring proves out.
- No edits to core claude-booping surfaces: `src/`, `playbooks/`, `agents/`, `skills/`, `docs/`, `documentation/` all untouched.
- No change to `fallback_agent`, `disable_internal_agents`, or the develop briefing shape.
- No changes to `~/.bin/pi-developer` itself — the script is taken as-is.
- No post-implementation reshape milestone (user-confirmed).

## CLAUDE.md impact

No CLAUDE.md changes required — every artifact is userland (`~/.claude/agents/`, vault config); core repo surfaces are untouched by design.
