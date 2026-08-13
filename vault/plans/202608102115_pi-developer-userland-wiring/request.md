# Framing brief

## Request

> now let's plan next: there is a pi-developer script created exactly for the task of handling each milestone. I want to wire it as pi-developer (old agent isn't used anywhere, so replace it as you want). The pi-developer agent in claude code should call pi-developer script and setup its context, including rendering agent body + give it milestone files to work on. Model i want to use is: http://10.0.0.106:8080/ui/#/models/Qwen3-Coder-Next can you plan this change? Also I explicitly want you to handle everything related to this change out of claude-booping scope. And this must be a userland wiring, not wiring in core claude booping.

## Task type

`feature` — new capability: the develop playbook gains a local-model worker path via the `~/.bin/pi-developer` script. Not `bug`: nothing diverges from expected behavior — the old `~/.claude/agents/pi-developer.md` agent is unused, not broken. Not `refactoring`: the wiring visibly changes what runs a milestone (local Qwen worker instead of the built-in booping-developer / old ollama-cloud pi-agent path), so behavior changes.

## Problem

Today the develop playbook delegates each milestone group to the plugin-shipped `booping:booping-developer` agent (Claude, paid API). A `~/.bin/pi-developer` script exists — headless `pi` pinned to the local llama-swap box at `http://10.0.0.106:8080`, scrubbed env, `--print` one-shot, `-f` prompt file, `-m` model override — but nothing invokes it. The stale `~/.claude/agents/pi-developer.md` agent still drives the retired `pi-agent --provider ollama-cloud --model glm-5.1` invocation and is used nowhere.

What must change: `~/.claude/agents/pi-developer.md` is rewritten to drive `~/.bin/pi-developer`; it composes the worker's context itself — renders the booping developer agent body and hands over the milestone file(s) it was briefed with — runs the script with model `Qwen3-Coder-Next`, validates the result against the milestone's DoD/Verify, and reports in milestone format. The develop playbook picks this agent up through userland config (external-agent wiring per `documentation/integrating-external-agents.md`), with zero edits to core claude-booping files.

## Clarifications and Decisions

- Old `~/.claude/agents/pi-developer.md` is unused anywhere — replace outright (user).
- Model: `Qwen3-Coder-Next` on the llama-swap box `10.0.0.106:8080` (user; exact model id to be verified against the box's API during research).
- All artifacts of this change live outside the claude-booping repo: `~/.claude/agents/`, `~/.bin/`, userland booping config — never `src/`, `playbooks/`, `agents/` in the plugin (user, explicit).
- Wiring is userland: the develop playbook's worker agent is overridden via config tiers, not by touching core (user, explicit).
- Config tier: start with the vault config (`vault/config.yaml`); promote to global `~/.config/booping/config.yaml` later if it works well (user).
- `pi-developer` is a **proxy agent**: its own body stays compact — its job is to pass everything to `~/.bin/pi-developer`. The pi worker's prompt = rendered booping developer agent body + inputs (milestone file, plan index, etc.) (user).
- Agent registration `good_for`: "use for all development tasks instead of booping developer" — effectively the default develop worker via description (user).
- No post-implementation reshape milestone (user).
