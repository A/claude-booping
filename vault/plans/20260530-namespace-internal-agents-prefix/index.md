---
title: "Namespace internal agents with booping: prefix in delegation table"
type: bug
status: done
sp: 2
split_from: null
created: 2026-05-30 00:00
planned: 20260530 16:22
commit: 4945eb457bb68ea662c10fad43178890b1d1f9e7
started: 20260530 16:43
completed: 2026-06-10 12:14
retro: retrospectives/20260610-cli-logging-and-agent-namespacing.md
goal: success
summary: "Prefix internal native agents' subagent_type with booping: in the delegation table so Agent-tool calls resolve first try"
---

# Namespace internal agents with booping: prefix in delegation table

## Context

The **Available Agents** table rendered into `/groom`, `/develop`, `/retro`, and
`/code-review` is produced at skill-load time by the `_available_agents.j2`
macro. For native (`type: agent`) entries it renders:

> Invoke via the `Agent` tool with `subagent_type="booping-researcher"`.

But the Claude Code harness namespaces plugin-provided agents by plugin name:
the booping plugin's agents are exposed only as `booping:booping-developer` and
`booping:booping-researcher` (confirmed against the live agent registry and
`.claude-plugin/plugin.json` / `marketplace.json`, both `name: booping`). The
bare name the macro emits is not a registered `subagent_type`.

**Observed:** the orchestrator intermittently reports it cannot see the agent on
first delegation, then "finds" it after a recheck (it re-reads the live agent
list and uses the namespaced form). **Expected:** the invocation string the skill
hands the model is the exact registered name, so delegation succeeds on the
first try, deterministically.

After this change, internal native agents render
`subagent_type="booping:<name>"`; user-supplied native agents and all cli
(`type: cli`) entries are unchanged.

## Triage

- **Root cause (obvious on inspection):** `src/templates/_partials/_available_agents.j2`
  line 16 renders `subagent_type="{{ agent }}"` — the bare config key — for every
  native entry. The harness registers plugin agents under the `booping:` namespace,
  so the bare key never matches.
- **Why intermittent:** when the first delegation fails, the model lists agents,
  sees `booping:booping-researcher`, and retries with the namespaced name — so a
  "recheck" succeeds. The skill text, not the agent, is wrong.
- **Repro:** load any skill that renders the agents table (e.g.
  `bin/booping render src/templates/skills/groom.md.j2`), observe the bare
  `subagent_type="booping-researcher"` line; attempt `Agent(subagent_type="booping-researcher")`
  → not found; `Agent(subagent_type="booping:booping-researcher")` → found.

## Decisions

- **Prefix source**: hardcode the literal `booping:` in the partial, gated on the
  entry being `internal: true` and `type: agent` — *not* sourced from
  `plugin.json` into Context. One-line-class template change, no Python plumbing.
  Trade-off: drifts only if the plugin is ever renamed, which is rare and would
  already require touching `plugin.json` + `marketplace.json` together.
- **Gate on `internal`, not on `type` alone**: only the plugin's own agents are
  namespaced by the harness. A user who adds their own native agent under
  `skills.<name>.agents.<id>` (no `internal` flag) registers it bare, so those
  must keep rendering the bare `subagent_type`. The existing
  override-to-cli test already drops the `internal` flag on the merged entry, so
  an overridden entry correctly loses the prefix.
- **cli (`type: cli`) entries unchanged**: they render `booping run-agent <id>`,
  where `<id>` is the config key, not a `subagent_type`. No namespace applies.
- **Test strategy**: existing automated check. `test_available_agents.py`
  currently asserts the *bare* names — it codified the bug. Updating those
  assertions to the namespaced form (plus a new assertion that a non-internal
  native entry stays bare) is the regression guard; it fails before the fix and
  passes after.

## Architecture

Single rendering site. The macro `render(skill)` in
`src/templates/_partials/_available_agents.j2` is imported `with context` by
every skill template that lists agents; the table is rendered live at
skill-load (the on-disk `skills/<name>/SKILL.md` are thin shells whose body is a
single `!`booping render ...`` line, so they contain no agent strings). One
edit to the partial fixes all four consuming skills at once. **No `just build`**
is required — the partial is runtime-rendered, not a `src/files/` build input.

## Milestones

### M1: Namespace internal native agents in the delegation macro — 2 SP | done

**Goal**: native internal agents render `subagent_type="booping:<name>"`; user
native agents and cli entries render unchanged.

**Verify**:
- `bin/booping render src/templates/skills/groom.md.j2` shows
  `subagent_type="booping:booping-researcher"` and no bare
  `subagent_type="booping-researcher"`.
- `cd booping-python && uv run pytest tests/templates/test_available_agents.py`
- `just lint && just typecheck && just test`

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | In the native (`type == "agent"`) branch of `render`, split on `spec.get("internal", False)`: internal → `subagent_type="booping:{{ agent }}"`; else keep bare `subagent_type="{{ agent }}"`. cli branch untouched. | `src/templates/_partials/_available_agents.j2` | 1 | done |
| 1.2 | Update `test_default_config_renders_native_invocation_lines` to assert the `booping:`-prefixed strings for both internal agents and assert the bare forms are absent. Add a case (new fixture or extend an existing vault fixture) proving a **non-internal** native agent renders the bare `subagent_type`. Update the sibling-agent assertion in `test_booping_developer_overridden_to_cli_replaces_wholesale` to the namespaced researcher string. | `booping-python/tests/templates/test_available_agents.py`, test fixtures under `booping-python/tests/__fixtures__/` | 1 | done |

#### Task 1.1 DoD

- [x] Rendered groom/develop/retro/code-review agents table shows `subagent_type="booping:booping-developer"` / `"booping:booping-researcher"` for internal entries.
- [x] No bare `subagent_type="booping-developer"` / `"booping-researcher"` remains in any rendered skill body.
- [x] cli entries still render `booping run-agent <id>` (no `subagent_type` line, no `booping:` prefix).
- [x] The override-to-cli path renders no `subagent_type` line for the overridden id (internal flag dropped → no prefix branch reached).

#### Task 1.2 DoD

- [x] `test_available_agents.py` asserts the `booping:`-prefixed invocation lines for both internal agents and asserts the bare strings are absent.
- [x] A test proves a non-internal native agent (no `internal` flag) renders a bare `subagent_type` with no `booping:` prefix.
- [x] `cd booping-python && uv run pytest tests/templates/test_available_agents.py` passes.

---

## Final Verification

- [x] `bin/booping render src/templates/skills/groom.md.j2` (and `develop`) produces clean output with the namespaced invocation lines; no `{{placeholder}}` leaks.
- [x] No `just build` needed (no `src/files/` change); `git diff -- skills/ agents/` is empty after the change.
- [x] `just lint && just typecheck && just test` green.

## Implementation note

- Implement on the **current branch** (`feat/log-booping-cli-calls`) — do **not** cut a new branch for this fix.

## Out of scope

- No change to cli (`type: cli`) delegation or `booping run-agent`.
- No change to agent `.md` files, agent `name:` frontmatter, or config keys.
- No Context / Python plumbing of the plugin name (decision: hardcode `booping:`).
- No change to vault extension channels (`_booping/agent_<id>.md`) — keyed by bare id, untouched.

## CLAUDE.md impact

No CLAUDE.md changes required — the partial's rendered output string changes, but
no config schema, partial API, or rendered-artifact path changes. The
`_available_agents.j2` description in CLAUDE.md remains accurate.

---

# Quality Checklist

## Frontmatter
- [x] Frontmatter matches the plan frontmatter shape.
- [x] `sp` (2) equals the sum of per-task SP (1 + 1).

## Content
- [x] Context names the visible change in rendered skills (invocation string).
- [x] DoD bullets verifiable by reading rendered output / running the test.
- [x] Every task lists exact paths.
- [x] Every task DoD uses checkboxes.
- [x] Milestone has a Verify step.
- [x] Milestone executable from a fresh session with only the plan.

## Skill-design hygiene
- [x] No structured facts moved into prose; change is in the macro template only.
- [x] No stack-specific details.
- [x] No restated flow / transitions.

## Anti-patterns (must be absent)
- [x] No TBD/TODO.
- [x] No task spanning unrelated concerns.
- [x] No prose duplicating a rendered table.
- [x] No stale state names.

## External references validated
- [x] `src/templates/_partials/_available_agents.j2` exists.
- [x] `booping-python/tests/templates/test_available_agents.py` exists.
