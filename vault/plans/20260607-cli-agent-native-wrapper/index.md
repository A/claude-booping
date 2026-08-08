---
title: CLI agents as native wrapper agents + /compile skill
type: feature
status: done
sp: 17
split_from: null
created: 2026-06-07 00:00
planned: 20260607 18:43
commit: 8456745d866bbd285594df4bb6874bec14d6a47e
started: 20260607 18:46
completed: null
retro: null
goal: null
summary: "cli agents become generated native wrapper agents (booping compile + /compile skill) replacing the run-agent Bash call"
---

# CLI agents as native wrapper agents + /compile skill

## Context

Today a `type: cli` agent is invoked by the skill running `booping run-agent <id>` via the **Bash** tool — `_available_agents.j2` renders a Bash branch for cli entries, distinct from the `Agent`-tool branch used by native agents. The skill owns the orchestration: piping the briefing, deciding background-vs-foreground, reading output. cli delegation is wired only into `/develop`.

After this change, each `type: cli` agent is fronted by a **native wrapper agent** generated into repo-local `<repo>/.claude/agents/cli_agent_<id>.md`. Skills invoke it like any native agent (`subagent_type="cli_agent_<id>"`); the Bash branch is deleted. The wrapper (a native Claude sub-agent) encapsulates: call `booping run-agent <id>` (the unchanged mechanical floor), validate output against the briefing's DoD, retry with correction, report in the standard format.

Because the Claude Code agent registry is **scanned once at startup and frozen in AppState** (no file-watcher over agent dirs; `SessionStart` hook fires *after* the scan — confirmed from CC source `main.tsx:2029` load vs `:2437` hook, `loadAgentsDir.ts:296` memoize), generated agents only become invokable after a **restart**. A new `/booping:compile` skill regenerates the wrappers on demand and tells the user to restart to apply. cli-delegating skills get a fallback line: if a cli agent is missing from the registry, run `/booping:compile` and restart.

`/booping:compile` is intentionally the general **static-generation entrypoint** — today it syncs cli wrappers; future static updates land under the same command.

## Decisions

- **Native wrapper per cli agent, not one generic runner** — each cli id gets its own `subagent_type`, so the macro renders a clean bare-id invocation and there is no failure-prone "pass the target id through free-text briefing" step.
- **Wrapper runs `model: opus`, `effort: low`** — the wrapper only orchestrates (call run-agent, validate, one retry, report); low effort suffices, opus for reliable judgment. Set in the wrapper template frontmatter.
- **Full-bake at compile time, not load-time self-render** — `booping compile` runs per-project with the vault present, so it renders the *complete* wrapper body (project context already folded in) into the generated file. No `!`render`` self-call at agent load → no extra tool round-trip / rethink per delegation. (Internal native agents are **out of scope** — they keep their committed thin-shell + load-time self-render and the `booping:` prefix.)
- **Validation + retry policy = fixed prose in the wrapper template**, not config. Per-worker task semantics already arrive via the `_booping/agent_<id>.md` soul (run-agent prepends) and the briefing DoD. No new config schema. **Retry count is fixed at one corrective retry** (call → validate → on failure, one re-call with correction → validate → report) — baked literally into the template, not a `{{ N }}` placeholder.
- **`run-agent` stays unchanged** as the mechanical floor (prompt composition, subprocess exec, git-diff, logging). The wrapper calls it via the **existing** `--briefing-file` flag (`run_agent.py:28`) — no new flag, no `run-agent` modification.
- **Prefixed real files, no symlinks/cache/manifest** — compile writes each wrapper as a real file `<repo>/.claude/agents/cli_agent_<id>.md` (registry name / `subagent_type` = `cli_agent_<id>`). Flush = glob-delete every `cli_agent_*.md` in `.claude/agents/`, then regenerate. The `cli_agent_` prefix is the unambiguous booping-managed marker — it never collides with hand-authored agents (which carry no prefix), so prune is a one-line glob and needs no cache dir, no symlink, no manifest. Eliminates the "does the CC loader read symlinks" risk entirely (these are plain files).
- **Trigger = manual `/booping:compile` + restart**, not a pre-launch wrapper or `SessionStart` hook. A hook cannot give single-restart freshness (no hook runs before the boot-time registry scan); the explicit skill keeps the model simple and reusable for future static updates.
- **`render-cli-agent <id>` is a thin renderer subcommand** that `compile` calls per id; also usable standalone for inspection/debug.

## Architecture

```
skill (/develop, …) ──Agent tool──▶ cli_agent_<id> (native, generated) ──Bash──▶ booping run-agent <id> ──▶ cli subprocess
                                        │ validate output vs briefing DoD
                                        │ retry (re-call run-agent + correction)
                                        └ report (standard milestone format)

/booping:compile ──Bash──▶ booping compile
    booping compile: Context.assemble() → scan merged config skills.*.agents[type==cli]
                     → glob-delete .claude/agents/cli_agent_*.md
                     → render-cli-agent <id> → write .claude/agents/cli_agent_<id>.md
                     → print diff + "restart Claude Code to apply"
```

- `_available_agents.j2`: cli agents render as native invocations (`subagent_type="cli_agent_<id>"`), plus a one-line "if missing from the registry, run `/booping:compile` and restart" note rendered once when any cli agent is present.
- Generated `cli_agent_*.md` are gitignored by prefix; hand-authored agents (no prefix) commit naturally — no `!`-whitelist needed.

## Milestones

### M1: Wrapper template + `render-cli-agent` — 3 SP | done

**Goal**: `booping render-cli-agent <id>` prints a complete, generic native-wrapper body for a configured cli agent.

**Verify**: `bin/booping render-cli-agent <a cli id from a fixture/config>` prints a clean wrapper body with the id baked into the `run-agent` call; `just test` green for the new command.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Author wrapper template: generic orchestration prose — write briefing to a temp file, call `booping run-agent <id> --briefing-file <path>` (existing flag), validate changed-files + output against the briefing DoD, **one** corrective retry on failure, report in the standard milestone format. `<id>` and `good_for`/`bad_for` come from config by `agent_id`. | `src/templates/agents/_cli_wrapper.md.j2` | 2 | done |
| 1.2 | Add `render-cli-agent <id>` subcommand: resolve `<id>` in merged config (reuse `run_agent.resolve_agent`), error if not `type: cli`, render the template with `agent_id` + agent spec into context, print to stdout. Register in `cli.py`. Unit tests. | `booping-python/src/booping/commands/render_cli_agent.py`, `booping-python/src/booping/cli.py`, `booping-python/tests/test_render_cli_agent.py` | 1 | done |

#### Task 1.1 DoD
- [x] Wrapper body instructs: temp-file the briefing → `booping run-agent <id> --briefing-file <path>` (existing flag; no `run-agent` change).
- [x] Validation + retry are fixed prose (no per-agent config keys); retry is exactly one corrective re-call (no `N` placeholder).
- [x] `<id>` is baked literally into the rendered `run-agent` call (no runtime id-passing).
- [x] Report format matches the milestone-report shape used by the internal developer agent.

#### Task 1.2 DoD
- [x] `booping render-cli-agent <id>` prints the rendered body; non-cli or unknown id exits non-zero with a clear message.
- [x] Frontmatter of the printed body sets `tools: Read, Bash` (+ `Bash(booping:*)` allowance), `name: cli_agent_<id>`, `description` from config, `model: opus`, `effort: low`.
- [x] Tests cover: cli id renders; unknown id errors; non-cli (`type: agent`/internal) errors.

---

### M2: `booping compile` — prefixed-file generation + prune — 3 SP | done

**Goal**: `booping compile` materializes a current native wrapper (`cli_agent_<id>.md`) for every `type: cli` agent and removes wrappers for ids no longer in config.

**Verify**: in a fixture project with a cli agent configured, `booping compile` writes `.claude/agents/cli_agent_<id>.md`; removing the agent from config and re-running deletes it; `just test` green.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Implement `compile`: `Context.assemble()`; resolve `<repo>` from `context.project.repo_directory`; **mkdir -p** `<repo>/.claude/agents/`; **glob-delete** every existing `cli_agent_*.md` (full flush); scan `skills.*.agents` for `type: cli` (dedupe ids); for each id write `render-cli-agent <id>` output to `.claude/agents/cli_agent_<id>.md`. Register in `cli.py`. | `booping-python/src/booping/commands/compile.py`, `booping-python/src/booping/cli.py` | 2 | done |
| 2.2 | Output + tests: print a per-id created/removed diff and a final `Restart Claude Code to apply.` line. Tests: create, update (changed config → fresh file), prune (id removed → file gone), idempotent re-run, no-cli-agents no-op, hand-authored non-prefixed agent untouched. | `booping-python/src/booping/commands/compile.py`, `booping-python/tests/test_compile.py` | 1 | done |

#### Task 2.1 DoD
- [x] `.claude/agents/` is created if missing (no `FileNotFoundError` on a fresh clone).
- [x] Every existing `cli_agent_*.md` is deleted before regen (full flush); files without the prefix are never touched.
- [x] `compile` writes `cli_agent_<id>.md` for every configured cli id.
- [x] Target repo resolved from `context.project.repo_directory`; absent project → clear error, non-zero exit.

#### Task 2.2 DoD
- [x] Removing a cli id from config and re-running deletes its `cli_agent_<id>.md`.
- [x] Re-running with unchanged config reproduces identical files (idempotent).
- [x] Hand-authored non-prefixed agents in `.claude/agents/` are never touched.
- [x] Output ends with an explicit restart instruction.
- [x] Tests cover create / update / prune / idempotent / no-op / non-prefixed-untouched.

---

### M3: Macro + delegation wiring — 2 SP | done

**Goal**: cli agents render as `subagent_type="cli_agent_<id>"` invocations with a registry-miss fallback note; the Bash branch is gone.

**Verify**: `bin/booping render src/templates/skills/develop.md.j2` shows the cli agent (if any configured) as an Agent-tool invocation with the fallback line, no `booping run-agent` Bash instruction.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Delete the `type == cli` Bash branch in `_available_agents.j2`; cli entries render a native invocation `subagent_type="cli_agent_<id>"` (the generated wrapper's registry name). Render the registry-miss fallback note **exactly once** at the bottom of the table, gated on "any cli agent present" (not per row): "If a cli agent above is missing, run `/booping:compile` and restart Claude Code." | `src/templates/_partials/_available_agents.j2` | 2 | done |

#### Task 3.1 DoD
- [x] No `booping run-agent` / Bash instruction remains in the rendered agent table for cli entries.
- [x] cli entries render `subagent_type="cli_agent_<id>"`; internal entries still render `booping:<id>`.
- [x] Registry-miss fallback line renders **once** at the table bottom, only when ≥1 cli agent is present (not duplicated per row).
- [x] Rendering a skill with no cli agents is unchanged (no fallback note).

---

### M4: `/booping:compile` skill — 3 SP | done

**Goal**: `/booping:compile` runs `booping compile`, reports the diff, and tells the user to restart.

**Verify**: `bin/booping render src/templates/skills/compile.md.j2` produces clean output; `just build` materializes `skills/compile/SKILL.md`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Config entry `skills.compile: {}`; effort key `skills.compile.effort`. | `src/config.yaml`, `src/config_files.yaml` | 1 | done |
| 4.2 | Author skill template: run `booping compile` and surface its output **verbatim** (the CLI already prints the diff + restart instruction — do not restate either in skill prose); one brief line that this is the static-generation entrypoint. Standard wiring (`_project_context`, lessons, `_extra_instructions` key `skill_compile`). | `src/templates/skills/compile.md.j2` | 1 | done |
| 4.3 | Thin shell + build: frontmatter (`user-invocable: true`, `allowed-tools: Bash(booping:*)`, `effort: {{ skills.compile.effort }}`), body = `!`booping render src/templates/skills/compile.md.j2``. Run `just build`. | `src/files/skills/compile/SKILL.md.j2`, `skills/compile/SKILL.md` (artifact) | 1 | done |

#### Task 4.1 DoD
- [x] `skills.compile` present in both config files; `_available_agents.j2` resolves it (empty agents block).

#### Task 4.2 DoD
- [x] Skill body runs `booping compile` and shows its output verbatim.
- [x] Restart-to-apply is **not** restated in skill prose — it comes from the CLI output (no duplication).
- [x] No duplicated flow/prose the rendered output already carries.

#### Task 4.3 DoD
- [x] `just build` produces `skills/compile/SKILL.md` with no drift (`git diff -- skills/` clean after rebuild).
- [x] `bin/booping render src/templates/skills/compile.md.j2` renders without `{{placeholder}}` leaks.

---

### M5: Docs, CLAUDE.md, gitignore, reference cleanup — 4 SP | done

**Goal**: every reference invalidated by this change is updated in-sprint (no follow-up sweep); the new command is documented.

**Verify**: `just docs` builds (strict) with the new page in nav; `grep` finds no stale "pipe the briefing on stdin to `booping run-agent`" guidance describing the *skill's* path.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | New documentation page for `/compile` + add to mkdocs nav under Commands. | `documentation/compile.md`, `mkdocs.yml` | 1 | done |
| 5.2 | Update `docs/cli_agent_delegation.md`: cli agents are now fronted by a generated native wrapper invoked via the Agent tool; document `booping compile` + the restart requirement; keep the `run-agent`/soul section (still the mechanical floor). | `docs/cli_agent_delegation.md` | 1 | done |
| 5.3 | Update `CLAUDE.md`: CLI section (add `compile`, `render-cli-agent`); Editing-conventions / Agent-wiring note that cli delegation now flows through generated native wrappers; mention `.claude/agents/` generation + `/compile`. | `CLAUDE.md` | 1 | done |
| 5.4 | `.gitignore`: add `.claude/agents/cli_agent_*.md` (generated wrappers only). Surgical by prefix — hand-authored non-prefixed agents under `.claude/agents/` stay tracked; no `!`-whitelist needed. | `.gitignore` | 1 | done |

#### Task 5.1 DoD
- [x] `/compile` page covers what it does, when to run it, and the restart step; appears in nav; `just docs` (strict) passes.

#### Task 5.2 DoD
- [x] Doc describes the native-wrapper invocation path and `booping compile`; no instruction telling a *skill* to Bash `run-agent`.

#### Task 5.3 DoD
- [x] CLI list includes `compile` + `render-cli-agent`; cli-delegation description matches the new flow.

#### Task 5.4 DoD
- [x] `.claude/agents/cli_agent_*.md` is ignored; `git status` is clean after `booping compile` in this repo.
- [x] Non-prefixed agents under `.claude/agents/` remain trackable (not ignored).

---

### M6: Reshape pause (review gate) — 2 SP | pending

**Goal**: rendered prose artefacts are handed back for manual shaping before the plan leaves the sprint.

**Verify**: user confirms the shaped artefacts read correctly; any IA fixes applied.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | `/develop` renders and presents for user prose-shaping: the wrapper body (`booping render-cli-agent <id>`), the `/compile` skill (`bin/booping render src/templates/skills/compile.md.j2`), and the cli slice of `_available_agents.j2`. **Pause for review**; apply requested edits before transitioning out. | `src/templates/agents/_cli_wrapper.md.j2`, `src/templates/skills/compile.md.j2`, `src/templates/_partials/_available_agents.j2` | 2 | pending |

#### Task 6.1 DoD
- [ ] Rendered wrapper, `/compile` skill, and cli agent-table slice presented to the user.
- [ ] User-requested prose/IA edits applied (or explicit "no changes").
- [ ] Plan does not transition past this milestone without user sign-off.

---

## Final Verification

- [ ] `just build` renders cleanly and `git diff -- skills/ agents/` is empty after rebuild.
- [ ] `bin/booping render src/templates/skills/compile.md.j2` and `bin/booping render-cli-agent <id>` produce clean output (no `{{placeholder}}` leaks).
- [ ] `just lint`, `just typecheck`, `just test` green.
- [ ] `just docs` (strict) builds with `/compile` in nav.
- [ ] In a fixture/dogfood project: `booping compile` generates `cli_agent_<id>.md` wrappers; after restart a cli agent is invokable via the Agent tool (`subagent_type="cli_agent_<id>"`) and completes a round-trip through `run-agent`.

## Out of scope

- Internal native agents (`booping-developer`, `booping-researcher`) — unchanged (thin shell + load-time self-render + `booping:` prefix).
- Pre-launch wrapper / `SessionStart`-hook auto-generation — explicitly rejected in favor of manual `/compile` + restart.
- Wiring cli delegation into skills beyond where it already exists (`/develop`).
- Per-agent validation/retry config schema.

## Risks

- The prefixed-real-file design (vs the earlier symlink/cache/manifest approach) removed the prior risk surface: no symlink-loading uncertainty, no relative-path resolution, no orphaned-state pruning. Prune correctness now reduces to a `cli_agent_*.md` glob — covered by M2.2 tests.
- Residual: a user who renames a generated file (dropping the prefix) orphans it. Acceptable — deliberate action, outside the managed namespace.

## CLAUDE.md impact

- CLI section: add `compile`, `render-cli-agent`.
- cli-agent-delegation description: now flows through generated native wrappers (Agent tool), not a skill-level Bash `run-agent` call.
- Note repo-local `.claude/agents/` generation + the `/compile` + restart requirement.
- (Owned by M5.3.)
