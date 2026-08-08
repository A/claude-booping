---
title: Retire cli-agent wrapper subsystem; adopt the plannotator global-agent 
  pattern
type: refactoring
status: done
sp: 10
split_from: null
created: 2026-06-10 00:00
planned: 20260610 16:04
commit: cb75d7eae7a038e4e345b2516e579a76e399d4be
started: 20260610 16:09
completed: 2026-06-10 20:02
retro: retrospectives/20260722-seven-plan-retro.md
goal: success|partial|fail
summary: "Retire the cli-agent wrapper subsystem; adopt Plannotator's global-agent + vault-config pattern for pi-developer"
---

# Retire cli-agent wrapper subsystem; adopt the plannotator global-agent pattern

# Plan Body

## Context

Two recent plans built today's external-CLI path inside the plugin: `20260519-cli-agent-delegation` (the `booping run-agent` mechanical floor + `type: cli`/`command` config) and `20260607-cli-agent-native-wrapper` (per-id wrappers via `booping compile` + the `/compile` skill + a Claude Code restart). To delegate `/develop` to an external CLI today you declare a `type: cli` agent, run `/compile` to materialize `<repo>/.claude/agents/cli_agent_<id>.md`, restart Claude Code, then invoke `subagent_type="cli_agent_<id>"` whose generated wrapper drives `booping run-agent <id>`.

`20260608-plannotator-code-review-surface` (in-progress) then integrated a *different* external worker — the browser review tool — and proved the wrapper subsystem is **unnecessary**. Plannotator's surface ships with **zero plugin-repo footprint**: a self-contained global agent (`~/.claude/agents/plannotator-reviewer.md`) drives the tool itself, and the project attaches it through two **pre-existing** booping extension points — vault `config.yaml` (`skills.<name>.agents.<id>`, no `type`/`internal`) which `_available_agents.j2` already renders as `subagent_type="<id>"`, plus the vault `_booping/skill_<name>.md` extension injected at the end of the rendered skill body. No `/compile`, no generated wrapper, no restart, no `run-agent`.

**After this change**, external-CLI delegation uses that same pattern, and the now-redundant wrapper subsystem is removed from the plugin. A concrete `pi-developer` global agent (authored in `~/.claude/agents/`, like plannotator-reviewer) drives the `pi` CLI itself and attaches to `/develop` purely through vault config + extra instructions. The plugin ships **no** cli-specific machinery; `pi-developer` and `plannotator-reviewer` become two instances of one documented pattern.

**All milestones are `/develop`-executable.** M1's artifacts (the `pi-developer` global agent + vault wiring) live **outside** the plugin repo (`~/.claude/` + `~/Claude/claude-booping/`); this plan deliberately authorizes the `/develop` worker to write those paths, lifting booping's usual "agents touch only the attached repo, never the vault" convention for the named files. That limit is self-imposed, not a tool constraint — the worker has the filesystem access. M1 still produces **no plugin-repo diff**; M2–M3 are ordinary tracked-repo diffs.

## Decisions

- **Adopt the plannotator pattern wholesale; delete the wrapper subsystem.** External workers attach as self-contained global agents via vault config + `_booping/skill_<name>.md`, riding the existing `_available_agents.j2` plain-agent rendering. Remove `compile`, `render-cli-agent`, `run-agent`, `_cli_wrapper.md.j2`, the `/compile` skill, the `type: cli`/`command` config branch, and the cli branch in `_available_agents.j2`. — One pattern for all external workers; no build step, no restart, no generated files. The plannotator surface already demonstrates it end-to-end.
- **pi-developer is a self-contained global agent, no mechanical script.** Unlike plannotator (HTTP server + browser + background-process lifecycle, which needed `~/.claude/bin/booping-plannotator-review`), `pi-agent` is a one-shot headless command: the agent writes the briefing to a temp file, runs `pi-agent --print …` via its own Bash, reads stdout + `git status` to find changed files, validates against the briefing DoD/Verify, retries once, and reports. No transport layer. — Match the tool's actual complexity (lesson 0004 hierarchy); don't port machinery pi doesn't need.
- **Per-project worker behavior reaches pi via the briefing, not a baked soul.** With `run-agent` gone there is no `_booping/agent_<id>.md` injection. Project stack details reach the worker through the briefing `/develop` constructs, shaped by vault `_booping/skill_develop.md` — exactly how `_booping/skill_code-review.md` shapes the plannotator briefing. The global `pi-developer` agent itself stays project-agnostic.
- **`disable_internal_agents` is kept.** Not cli-specific; a project may still hide `booping-developer` so only `pi-developer` shows in `/develop`'s Available Agents table.
- **Integration guide lives in the plugin repo, the specific agents do not.** A public `documentation/` page documents booping's *extension mechanism* (global agent + vault config + extra instructions) with plannotator and pi-developer as worked examples. This is booping's own documentation; it does not embed either tool's specific artifacts (those stay global/vault), so the plannotator separation invariant holds.
- **`/develop` writes the global + vault artifacts directly.** booping's convention that worker agents touch only the attached repo is treated as artificial for this plan: M1's developer task writes `~/.claude/agents/pi-developer.md` and the two vault files, briefed with their exact paths + content shape. No manual main-session step. — Keeps the whole change inside one `/develop` run; the constraint was self-imposed, not a tool limit.
- **Branch: continue on the existing `feat/cli-agent-native-wrapper` release branch.** This plan reverses/supersedes that branch's wrapper subsystem, so it lands on the same branch rather than a new `refactor/` branch — the release's net diff collapses to the simpler end state (wrapper added then removed). Overrides the default type→branch mapping; `/develop` does not cut a new branch.
- **CLI invocation (confirmed):** `pi-agent --print --provider ollama-cloud --model kimi-k2.6`, with the briefing passed as the prompt. Sourced from the vault's previously-commented example. The binary is `pi-agent`; the global Claude agent fronting it is named `pi-developer` (distinct names — agent ≠ binary).

## Architecture

**Plugin extension points the pattern rides (unchanged, pre-existing):**

- `config.skills["<skill>"].agents.<id>` (vault `config.yaml` deep-merge) → `_available_agents.j2` renders it in the skill's Available Agents table as `subagent_type="<id>"` when it carries no `type`/`internal`.
- `_booping/skill_<skill>.md` (vault) → injected at the end of the rendered skill body via the existing `_extra_instructions` hook; this is where the per-project "how to brief the worker" guidance lives.

**Plugin core the refactor removes:** the `type == "cli"` branch + `ns.has_cli` footer in `_available_agents.j2`; the `booping` subcommands `compile`/`render-cli-agent`/`run-agent` and their modules + tests (`resolve_agent` is used only by these three); `_cli_wrapper.md.j2`; the `/compile` skill; `skills.compile` (config) + `compile` effort (config_files); the `.claude/agents/cli_agent_*` gitignore line; `docs/cli_agent_delegation.md`; `documentation/compile.md`.

`/develop`'s skill body is unchanged — it delegates generically through the Available Agents table; removing the cli branch from `_available_agents.j2` fully covers it (a configured plain `pi-developer` then renders identically to `plannotator-reviewer`).

Runtime flow after the change (external-CLI path):

```
/develop intake → grouping → per-milestone briefing                # unchanged booping core
  └─ vault _booping/skill_develop.md extension shapes the briefing:
       if `pi-developer` is in the agent table (vault config) and chosen for the group:
         brief subagent_type="pi-developer" with request + related files + DoD + Verify
       else: delegate to booping-developer (or other configured agent) as today

pi-developer agent (~/.claude/agents/pi-developer.md):              # global, self-contained
  write briefing → mktemp; run `pi-agent --print --provider ollama-cloud --model kimi-k2.6 …` (own Bash); capture stdout + `git status`
  validate changed files + output against the briefing DoD/Verify; retry once on shortfall
  report in the standard milestone format (Agent-tool result the orchestrator reads)
```

## Milestones

### M1: pi-developer global agent + vault wiring — 3 SP | pending

**Goal**: a self-contained `~/.claude/agents/pi-developer.md` global agent drives `pi` and is attached to booping's own `/develop` via vault config + extension — with **no plugin-repo diff**.

**`/develop`-executable** — the worker writes the global + vault files directly (this plan authorizes writes outside the repo for the named artifacts). Invocation is pinned (`pi-agent --print --provider ollama-cloud --model kimi-k2.6`); live verification needs the real binary present.

**Verify**: `git -C /home/anton/Dev/@A/claude-booping status --porcelain` shows no plugin-repo change; `bin/booping render src/templates/skills/develop.md.j2` (reading the vault override) shows `pi-developer` in the Available Agents table as `subagent_type="pi-developer"` with the extension text appended; one real `pi-agent` run from the agent on a trivial briefing produces the expected file change and a milestone-format report.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Author the global agent: frontmatter (`name: pi-developer`, `tools: Read, Bash`, description) + body that writes the briefing to a `mktemp`, runs `pi-agent --print --provider ollama-cloud --model kimi-k2.6` with the briefing as the prompt via Bash, reads stdout + `git status --porcelain` for changed files, validates against the briefing's DoD/Verify, retries exactly once on shortfall, and reports in the standard milestone format. No `booping run-agent`/transport script. | `~/.claude/agents/pi-developer.md` (new, global) | 2 | pending |
| 1.2 | Wire it into booping's vault: register `skills.develop.agents.pi-developer` (plain — no `type`/`command`/`internal`) with `good_for`/`bad_for` (optionally `disable_internal_agents: true`) in vault `config.yaml`; add a `_booping/skill_develop.md` extension describing how `/develop` briefs `pi-developer` (request + related files + DoD + Verify + project stack context) and the fallback to `booping-developer`. Replace the stale commented `pi-agent` `type: cli` block. | `~/Claude/claude-booping/config.yaml`, `~/Claude/claude-booping/_booping/skill_develop.md` | 1 | pending |

#### Task 1.1 DoD

- [ ] `~/.claude/agents/pi-developer.md` is a valid global agent, invokable as `subagent_type="pi-developer"`, self-contained (drives `pi-agent` with its own Bash; no `booping run-agent`/`compile`/`type: cli`).
- [ ] Baked invocation is `pi-agent --print --provider ollama-cloud --model kimi-k2.6` with the briefing as prompt.
- [ ] Validate-against-DoD, single corrective retry, and milestone report format all present; one live run produces the expected change + report.

#### Task 1.2 DoD

- [ ] Vault `config.yaml` registers `pi-developer` under `skills.develop.agents` with `good_for`/`bad_for`, no `type`/`command`/`internal`; the stale commented `pi-agent` `type: cli` block is gone.
- [ ] `_booping/skill_develop.md` shapes the pi-developer briefing + names the booping-developer fallback.
- [ ] Rendered `/develop` shows `subagent_type="pi-developer"` + the extension text; `git -C <plugin repo> status --porcelain` is empty.

---

### M2: Delete the cli-agent wrapper subsystem from the plugin — 4 SP | pending

**Goal**: the plugin exposes no `compile`/`render-cli-agent`/`run-agent`, no `/compile` skill, and no cli branch in `_available_agents.j2`; a configured plain external agent renders as `subagent_type="<id>"`; build/lint/typecheck/test are green.

**Plugin-repo refactor** (`/develop`-automatable). **Verify**: `booping --help` lists none of the three subcommands; `just build` then `git diff -- skills/ agents/` shows only the `compile` skill removed; `bin/booping render src/templates/skills/develop.md.j2` renders external agents as plain `subagent_type=` lines with no cli/restart prose; `just lint && just typecheck && just test` green.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Remove the `type == "cli"` branch and the `ns.has_cli` namespace/footer from `_available_agents.j2` so every non-internal agent renders as `subagent_type="{{ agent }}"`; update `test_available_agents.py` to drop cli-branch assertions and assert the plain rendering. | `src/templates/_partials/_available_agents.j2`, `booping-python/tests/templates/test_available_agents.py` | 1 | pending |
| 2.2 | Delete the `/compile` skill (thin shell, runtime template, build artifact); remove `skills.compile` from `src/config.yaml` and `compile: { effort: low }` from `src/config_files.yaml`; run `just build`. | `src/files/skills/compile/` (dir), `src/templates/skills/compile.md.j2`, `skills/compile/` (dir), `src/config.yaml`, `src/config_files.yaml` | 1 | pending |
| 2.3 | Drop the `compile`/`render-cli-agent`/`run-agent` imports + registrations from `cli.py`; delete the three command modules, the wrapper template, and the three command tests; remove the `.claude/agents/cli_agent_*` gitignore line + comment and any generated `cli_agent_*.md`. Run lint/typecheck/test. | `booping-python/src/booping/cli.py`, `booping-python/src/booping/commands/compile.py`, `booping-python/src/booping/commands/render_cli_agent.py`, `booping-python/src/booping/commands/run_agent.py`, `src/templates/agents/_cli_wrapper.md.j2`, `booping-python/tests/commands/{compile,render_cli_agent,run_agent}_test.py`, `.gitignore` | 2 | pending |

#### Task 2.1 DoD

- [ ] `_available_agents.j2` has no `type`/`cli_agent_`/`ns.has_cli` logic; a configured plain agent renders as `subagent_type="<agent>"` (verified against `plannotator-reviewer` in `code-review`).
- [ ] `test_available_agents.py` passes and no longer asserts cli-wrapper behavior.

#### Task 2.2 DoD

- [ ] `just build` succeeds; `skills/compile/` no longer exists; `git diff -- skills/ agents/` shows only the compile-skill removal.
- [ ] No `compile` key remains in `src/config.yaml` or `src/config_files.yaml`.

#### Task 2.3 DoD

- [ ] `cli.py` registers only surviving subcommands; `booping --help` reflects that; no remaining import of `resolve_agent` or the deleted modules in `booping-python/src/`.
- [ ] The three command modules, `_cli_wrapper.md.j2`, and the three command tests are deleted; `just test` passes with no collection errors.
- [ ] `.gitignore` no longer carries the `cli_agent_*` line/comment; no generated `cli_agent_*.md` remain; `just lint` + `just typecheck` green.

---

### M3: Integration guide + reference cleanup — 2 SP | pending

**Goal**: a public guide documents the global-agent integration pattern with both worked examples; every stale reference to the removed subsystem is deleted or rewritten.

**Plugin-repo refactor** (`/develop`-automatable). **Verify**: `just docs` builds with the new page in nav and no dead `/compile` entry / broken links; `grep -rn "cli_agent\|run-agent\|render-cli-agent\|booping compile\|type: cli" src/ booping-python/src/ docs/ documentation/ CLAUDE.md` returns nothing unintended.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Write `documentation/integrating-external-agents.md` as a **how-to-extend-the-booping-harness** guide: the pattern (self-contained global `~/.claude/agents/<id>.md` agent + vault `config.yaml` registration + `_booping/skill_<name>.md` extension, riding `_available_agents.j2`'s plain rendering — no `/compile`, no wrapper), then two worked examples — Case A `plannotator-reviewer` (bespoke browser agent + global transport script), Case B `pi-developer` (headless CLI worker, agent-only, with the install step into `~/.claude/agents/`). Add to mkdocs nav. Delete `docs/cli_agent_delegation.md`, `documentation/compile.md`, and the `/compile` nav entry. | `documentation/integrating-external-agents.md` (new), `mkdocs.yml`, `docs/cli_agent_delegation.md` (del), `documentation/compile.md` (del) | 1 | pending |
| 3.2 | Rewrite all CLAUDE.md references to the removed subsystem to describe the global-agent pattern: Status "Single CLI" subcommand list; Layout `.claude/agents/cli_agent_<id>.md` entry; Information-ownership "Delegate kind" bullet; Skill-design "Agent wiring" paragraph; Config-schema `type`/`command`/`disable_internal_agents` bullet (drop `type`/`command`, keep `disable_internal_agents`); CLI section `run-agent`/`render-cli-agent`/`compile` entries. Link the new guide. | `CLAUDE.md` | 1 | pending |

#### Task 3.1 DoD

- [ ] Guide presents the pattern + both cases, each as: (global agent) + (vault config block) + (extra-instructions channel); Case B documents the `~/.claude/agents/` install step.
- [ ] `docs/cli_agent_delegation.md` and `documentation/compile.md` are deleted; `mkdocs.yml` nav lists the new page and has no `/compile` entry; `just docs` build clean; links resolve.

#### Task 3.2 DoD

- [ ] No CLAUDE.md reference to `compile`, `render-cli-agent`, `run-agent`, `cli_agent_`, `type: cli`, a cli-agent `command:` key, "native wrapper", or the restart requirement remains except where intentionally framing the change.
- [ ] CLAUDE.md describes external-CLI delegation as: self-contained global agent + vault config (`good_for`/`bad_for`, optional `disable_internal_agents`) + `_booping/skill_<name>.md`, linking `documentation/integrating-external-agents.md`. `disable_internal_agents` stays documented; `type`/`command` do not.

---

### M4: Update the release PR — breaking-change note — 1 SP | pending

**Goal**: the open release PR for `feat/cli-agent-native-wrapper` reflects the final state: a breaking change removing `type: cli` support, with a pointer to the new integration approach.

**Plugin-repo refactor** (`/develop`-executable). Runs last — after M1–M3 are merged into the branch. **Verify**: `gh pr view` on the branch shows the updated body with the breaking-change callout and a resolvable doc link.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Find the open release PR for `feat/cli-agent-native-wrapper` (`gh pr view`) and update its description: add a **Breaking change** callout — `type: cli` agent support is removed (no `booping compile` / `run-agent` / `render-cli-agent`, no generated `cli_agent_*` wrappers, no `/compile`); state the new approach (external CLIs integrate as self-contained global agents wired via vault config + `_booping/skill_<name>.md` extra instructions); link the new guide `documentation/integrating-external-agents.md` (published page on the docs site + repo path). Overview of changes only — no test plan. | release PR body (no repo file) | 1 | pending |

#### Task 4.1 DoD

- [ ] PR body carries a clearly marked **Breaking change** note: `type: cli` support removed, naming the dropped surfaces (`compile`/`run-agent`/`render-cli-agent`/`/compile`/`cli_agent_*`).
- [ ] PR body states the replacement pattern and links `documentation/integrating-external-agents.md` (resolvable link to the published page).
- [ ] PR description is an overview of changes only — no test plan included.

---

## Final Verification

- [ ] `git -C /home/anton/Dev/@A/claude-booping status` confirms M1 produced no plugin-repo diff (global/vault only).
- [ ] `just build` clean; `git diff -- skills/ agents/` shows only the intended `compile`-skill removal.
- [ ] `just lint && just typecheck && just test` green.
- [ ] `just docs` builds with the integration guide in nav, no dead `/compile` entry, no broken links.
- [ ] `bin/booping render src/templates/skills/develop.md.j2` shows external agents as `subagent_type="<agent>"` with no cli/restart prose.
- [ ] `grep -rn "cli_agent\|run-agent\|render-cli-agent\|booping compile\|type: cli" src/ booping-python/src/ docs/ documentation/ CLAUDE.md` returns nothing unintended.
- [ ] Release PR body updated with the breaking-change note + a resolvable link to the new integration guide.

## Out of scope

- `/develop`, `/groom`, `/retro`, `/learn`, `/chat`, `/code-review`, `/install`, `/help` skill bodies — none reference the cli subsystem (verified); only `_available_agents.j2` + config change in the plugin.
- The plannotator surface (`20260608`, in-progress) — untouched; this plan only *documents* it as Case A.
- A persistent vault artifact / `/learn` feed for pi-developer runs — out of scope, as in the plannotator plan.

### Flagged (vault-owned — manual, outside plugin-repo write scope)

- `~/Claude/claude-booping/_booping/skill_code-review.md` tells the user to run `/booping:compile` and restart if `plannotator-reviewer` is missing — already incorrect (plannotator is never compiled) and `/compile` is being deleted. Update that vault extension to drop the `/compile`/restart guidance. (Code-review's vault file; flag, do not fold into M1.)

## CLAUDE.md impact

Covered by M3.2: Status (Single CLI list), Layout (`cli_agent_<id>` entry), Information ownership (Delegate kind), Skill design (Agent wiring paragraph), Config schema (`type`/`command` bullet — keep `disable_internal_agents`), CLI section (`run-agent`/`render-cli-agent`/`compile`).

# Quality Checklist

(Verification rubric — checked before leaving `in-spec`; not part of the executable body.)

- [ ] Frontmatter matches the plan frontmatter template; `sp` (10) = sum of task SP (2+1 + 1+1+2 + 1+1 + 1).
- [ ] Context names the observable change (external-CLI delegation moves to the global-agent pattern; wrapper subsystem removed) and that `/develop` writes the global/vault artifacts.
- [ ] M1 writes only global/vault paths (no plugin-repo file); the plan explicitly authorizes `/develop` to write outside the repo for those named artifacts.
- [ ] Every task lists exact paths; every milestone has a `Verify` with a rebuild/render; every DoD uses checkboxes.
- [ ] Stale-reference cleanup (CLAUDE.md, docs, gitignore, nav) is in-sprint (M2/M3), not a follow-up sweep (lesson 0005).
- [ ] `disable_internal_agents` retained; only cli-specific config (`type`/`command`) removed.
- [ ] No "TBD/TODO"; no task spanning unrelated concerns; the unresolved `pi` invocation is an explicit M1.1 step, not a silent assumption.
</content>
