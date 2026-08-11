---
id: "02"
title: "Wire pi-developer into develop via vault config"
sp: 2
status: pending
plan: "vault/plans/202608102115_pi-developer-userland-wiring/index.md"
---

# M02: Wire pi-developer into develop via vault config

**Goal**: the develop playbook's Available Agents table lists `pi-developer` with steering that makes it the worker for all development tasks — via the vault config tier only.

**Scope**: only `{vault}/config.yaml` (`/home/anton/Dev/@A/claude-booping/vault/config.yaml` — repo-local vault, so this milestone commits normally). Existing keys (`core.sprint.max_milestones_per_agent`, `core.code_review_playbook.agents.plannotator-reviewer`) must survive the merge untouched. No core file changes.

**Tests**: none — config surface; verification is the rendered develop playbook's agents table.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Add `core.develop_playbook.agents.pi-developer` with `good_for:` bullets ("all development tasks — milestone implementation from a develop briefing; use instead of booping-developer") and `bad_for:` bullets (vault writes; research/read-only investigation — that stays `booping:booping-researcher`). Shape: copy the structure of the existing `core.develop_playbook.agents.booping-developer` entry in `src/config.yaml` (`good_for:` and `bad_for:` are YAML string lists), omitting `internal:` — read that entry first, never guess the nesting. Do not add `disable_internal_agents`, do not touch `fallback_agent`. | `/home/anton/Dev/@A/claude-booping/vault/config.yaml` | 2 | pending |

## Definition of Done

### Task 2.1

- [ ] `booping render-playbook develop` shows `pi-developer` (bare, unprefixed) in the Available Agents table with the authored `good_for`/`bad_for`.
- [ ] `booping:booping-developer` and `booping:booping-researcher` still render in the table (internal agents not disabled).
- [ ] Pre-existing vault config keys are byte-identical in the merged view (`booping config-get core.sprint.max_milestones_per_agent` unchanged).
- [ ] `git status` in the plugin repo shows only `vault/` paths changed.

## Verify

- `cd /home/anton/Dev/@A/claude-booping && bin/booping render-playbook develop | grep -A3 'pi-developer'` — the entry renders with its steering text.
- `cd /home/anton/Dev/@A/claude-booping && bin/booping config-get core.develop_playbook.agents.pi-developer` — prints the authored mapping.
