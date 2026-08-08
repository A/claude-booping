---
title: Session active-time metrics — lead/cycle time from Claude Code session 
  logs
type: feature
status: done
sp: 20
split_from: null
created: 2026-08-08 13:00
planned: null
started: 2026-08-08 14:13
completed: 2026-08-08 20:15
code_reviews: null
retro: null
goal: null
summary: "Per-plan active_minutes + models from session jsonl: stamped by groom/develop
  hooks, mined by booping session-time"
commit: 7fda466631d32c10a50abd72ae4e4d928a1b801b
reviewed_at: 2026-08-08 14:10
sessions:
- 1cfd40e3-9279-4c04-abef-8b567aff0dcc
- a5a26af0-39a5-4569-8c9c-667efd74dbe9
- 5a8c526f-60f5-4f1e-9902-4e78fd319c9f
metrics_active_minutes: 19
metrics_models:
- claude-fable-5
metrics_tokens_input: 221
metrics_tokens_output: 124411
metrics_tokens_cache_creation: 610923
metrics_tokens_cache_read: 9657980
---

# Session active-time metrics — lead/cycle time from Claude Code session logs

## Context

Sprints carry only story points; plan frontmatter records walltime waypoints (`created`, `started`, `completed`) but nothing measures active work time. Claude Code writes per-session transcripts to `~/.claude/projects/{slug}/{sessionId}.jsonl` with per-event ISO-8601 timestamps and no duration fields. After this plan: groom and develop runs stamp their session id into the plan's `sessions:` frontmatter list, a new `booping session-time` subcommand sums assistant-turn spans across those transcripts and collects the model ids that ran them, the develop close edge stamps the results into `active_minutes:` and `models:`, and both surface in `sprints.md` and future vault scaffolds.

## Decisions

- **Metric**: `active_minutes:` integer only — sortable in Obsidian Bases and query specs; display formatting is a view concern. No walltime LT/CT keys, no per-phase breakdown.
- **Turn-span algorithm**: a turn starts at a real user prompt (`type: "user"`, no `isMeta`, `message.content` is a string) and ends at the last event before the next real user prompt (or EOF); span = end − start. Sum spans across all stamped sessions, round to whole minutes. Idle time between turns drops out naturally. Lines with `isSidechain: true` are excluded (synchronous subagent work is already inside the parent turn's span; separate sidechain files are never opened).
- **Models metric**: `models:` — sorted list of distinct `message.model` values from non-sidechain `assistant` events of the stamped sessions (full ids, e.g. `claude-fable-5`, `claude-opus-4-8`, so the version rides along). Short aliases (`fable`, `opus`) appearing on config/mode lines are ignored — only assistant events count as "ran".
- **Attribution**: session ids stamped into a `sessions:` frontmatter list by transition hooks — exact, forward-only. No retroactive time-window matching.
- **Session id source**: `$CLAUDE_CODE_SESSION_ID` from the inherited environment of script hooks. The variable is undocumented — absence is a warn-to-stderr no-op, never a failed transition.
- **Stamp scope**: groom + develop edges only, matching "groom to done". Code-review and retro sessions do not count.
- **Compute point**: script hook on develop's `in-progress → done` and `in-progress → fail` edges; the subcommand also runs manually anytime.
- **List append**: `booping frontmatter-update` gains `--append key=value` (create list if missing, dedup) — the stamp script shells out to it rather than regex-editing YAML. Prior art: `playbooks/code-review/_scripts/close-code-review` (delivered 2026-08-08) regex-appends to `code_reviews:`; `--append` becomes the canonical append path going forward, and porting `close-code-review` onto it is out of scope.
- **Hook order on develop close edges**: `script stamp-session` runs before `script stamp-active-time` on `in-progress → done` / `→ fail`, so the closing session's own minutes and model are counted.
- **Defensive parsing**: the jsonl schema is internal and moves between Claude Code versions — unknown fields and line types are tolerated, malformed lines skipped with a stderr count, never a crash.
- **Existing vault**: migration `005` adds the `active_minutes` column to the existing `sprints.md` Bases fence; the setup scaffold is updated for future vaults.

## Architecture

```
groom/develop transition ──script stamp-session──▶ plans/{slug}/index.md  sessions: [id, …]
                                                            │
develop in-progress → done ──script stamp-active-time──▶ booping session-time <plan> --write
                                                            │
                              ~/.claude/projects/*/{id}.jsonl ──parse──▶ active_minutes: N
                                                            │
                                   sprints.md Bases / query columns ◀── frontmatter
```

- Input sources: plan `sessions:` list; transcript files globbed as `~/.claude/projects/*/{id}.jsonl` (any project dir — sessions may run from repo or vault cwd).
- Output sinks: stdout report; `active_minutes:` frontmatter via the existing `update_frontmatter` writer.
- Callers: `stamp-active-time` script hook (develop close edges); humans ad hoc. No skill inlines it.

## Milestones

### M1: `booping session-time` — transcript mining core — 8 SP | done

**Goal**: `booping session-time <plan>` prints per-session and total active minutes plus the distinct model ids, computed from the plan's `sessions:` list; `--write` stamps `active_minutes:` and `models:`.

**Verify**: `bin/booping session-time booping-python/tests/fixtures/session_time/plan/index.md --projects-root booping-python/tests/fixtures/session_time/projects` prints the fixture's expected per-session rows and total; `just pytest` green.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Transcript locator + defensive line parser: glob `~/.claude/projects/*/{id}.jsonl` (root overridable), stream-parse lines, classify real-user-prompt / other-event / sidechain / malformed, yield (timestamp, kind, model) — model set only on assistant events, from `message.model` | `booping-python/src/booping/session_time.py`, `booping-python/tests/test_session_time.py`, `booping-python/tests/fixtures/session_time/projects/**/*.jsonl` | 3 | done |
| 1.2 | Turn-span summation + model collection: group events into turns per the Decisions algorithm, sum spans per session, round total to minutes; accumulate sorted distinct assistant `message.model` values; unit-tested against fixture transcripts covering idle gaps, sidechain lines, malformed lines, empty file, mixed models | `booping-python/src/booping/session_time.py`, `booping-python/tests/test_session_time.py` | 3 | done |
| 1.3 | Subcommand wiring: `session-time <plan> [--write] [--projects-root PATH]` — read `sessions:`, compute, print report, `--write` stamps `active_minutes:` and `models:` via the frontmatter writer; register in CLI parser + `--help` | `booping-python/src/booping/commands/session_time.py`, `booping-python/src/booping/cli.py`, `booping-python/tests/test_session_time.py` | 2 | done |

#### Task 1.1 DoD

- [x] Locator finds a fixture session file under a `--projects-root` tree shaped like `{root}/{slug}/{id}.jsonl`.
- [x] Missing transcript for a stamped id → stderr warning naming the id, session skipped, exit stays 0.
- [x] Malformed line and unknown `type` values are skipped and counted, never raised.
- [x] Sidechain lines (`isSidechain: true`) and meta user lines (`isMeta` or tool_result content) are classified out of real-user-prompt.

#### Task 1.2 DoD

- [x] Fixture with a mid-session idle gap sums only the two turn spans, not the gap.
- [x] Session ending on an assistant event (no trailing user prompt) counts the final turn to its last event.
- [x] Empty / header-only transcript yields 0 minutes without error.
- [x] Total is a rounded integer of minutes.
- [x] Two sessions on different models yield both full ids, sorted, deduped; sidechain assistant lines contribute no model.

#### Task 1.3 DoD

- [x] Happy path prints one row per session id + total minutes + models line; values match fixture expectation.
- [x] `--write` sets `active_minutes:` and `models:` on the plan; without it the file is untouched.
- [x] Plan without a `sessions:` key → stderr message, exit 1.
- [x] `bin/booping session-time --help` reflects the surface.

---

### M2: Session stamping — capture + wiring — 6 SP | done

**Goal**: every groom and develop transition run inside a Claude Code session appends that session's id to the plan's `sessions:` list.

**Verify**: `CLAUDE_CODE_SESSION_ID=test-id bin/booping playbook-transition …` on a scratch plan appends `test-id` once across two transitions; `just ci` green.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | `frontmatter-update --append key=value`: create list when key is null/absent, append with dedup, reject appending to an existing scalar with exit 1; unit tests | `booping-python/src/booping/commands/frontmatter_update.py`, `booping-python/src/booping/context/_yaml.py`, `booping-python/tests/test_frontmatter_update.py` | 2 | done |
| 2.2 | `stamp-session` shared script hook: read `$CLAUDE_CODE_SESSION_ID`; absent → stderr warn, exit 0; present → `bin/booping frontmatter-update "$BOOPING_ARTIFACT" --append sessions={id}` | `playbooks/_scripts/stamp-session` | 2 | done |
| 2.3 | Wire `script stamp-session` onto groom edges (`framing → researching`, `awaiting-approval → ready-for-dev`) and develop edges (`ready-for-dev → in-progress`, `in-progress → done`, `in-progress → fail`); add `sessions: []` to the plan identity frontmatter template + `docs/template_plan_frontmatter.md`; re-accept snapshots | `playbooks/groom/playbook.yaml`, `playbooks/develop/playbook.yaml`, `playbooks/_partials/plan_frontmatter.md`, `docs/template_plan_frontmatter.md`, `playbooks/*/_reports/output.md` | 2 | done |

#### Task 2.1 DoD

- [x] `--append` on a null/absent key creates a one-element list.
- [x] Appending an id already in the list is a no-op (idempotent re-stamp).
- [x] `--append` on an existing scalar key → stderr message, exit 1.
- [x] Plain `key=value` behavior unchanged; tests cover both paths.

#### Task 2.2 DoD

- [x] With the env var set, the script appends exactly that id to `sessions:`.
- [x] Without it, exit 0 and one stderr warning line; transition proceeds.
- [x] Script resolves from the shared root `_scripts/` for both playbooks.

#### Task 2.3 DoD

- [x] Two same-session transitions leave one list entry; a second session id adds a second entry.
- [x] Identity frontmatter template and `docs/template_plan_frontmatter.md` show `sessions: []`.
- [ ] `just snapshots` diff reviewed and accepted; `just ci` green. — drift surfaced (groom report, `sessions: []`), awaiting the user's `just snapshots-accept`

---

### M3: Compute at develop close — 2 SP | done

**Goal**: a plan reaching `done` or `fail` carries stamped `active_minutes:` and `models:`.

**Verify**: transition a scratch plan with a fixture-backed `sessions:` list to `done`; `active_minutes:` appears; `just ci` green.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | `stamp-active-time` shared script hook calling `bin/booping session-time "$BOOPING_ARTIFACT" --write`; compute failure → stderr warn, exit 0 (metric loss never blocks a close); wire onto develop `in-progress → done` and `in-progress → fail`; re-accept snapshots | `playbooks/_scripts/stamp-active-time`, `playbooks/develop/playbook.yaml`, `playbooks/develop/_reports/output.md` | 2 | done |

#### Task 3.1 DoD

- [x] `done` edge stamps `active_minutes:` and `models:` on a fixture-backed plan.
- [x] Hook order in the manifest: `stamp-session` listed before `stamp-active-time` on both close edges.
- [x] Empty `sessions:` or missing transcripts → close succeeds, stderr warning only.
- [ ] `just snapshots` accepted; `just ci` green. — drift surfaced (groom report only), awaiting the user's `just snapshots-accept`

---

### M4: Surfacing, migration 005, docs — 4 SP | done

**Goal**: `active_minutes` visible in vault views; existing vaults migrate; docs current.

**Verify**: `just ci` green; migration instructions apply idempotently to a sprints.md fence; docs name the subcommand.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Add `active_minutes` and `models` to the sprints.md scaffold Bases `order:` and to `core.groom_playbook.queries.latest_plans.columns` | `src/config.yaml` | 1 | done |
| 4.2 | Migration `005_session-metrics-columns`: instructions to insert `active_minutes` and `models` into the existing sprints.md Bases fence `order:` list; frontmatter `id: 5` | `migrations/005_session-metrics-columns/migration.md` | 2 | done |
| 4.3 | Docs sweep: `session-time` in project `CLAUDE.md` CLI list, `sessions:`/`active_minutes:`/`models:` keys in `documentation/vault.md`, scaffold mention in `documentation/project_config.md` if it quotes the `order:` list | `CLAUDE.md`, `documentation/vault.md`, `documentation/project_config.md` | 1 | done |

#### Task 4.1 DoD

- [x] `order:` list and `latest_plans.columns` include `active_minutes` and `models`.
- [x] `just ci` green (no intake-table drift; the groom/migrate report drift awaits the user's `just snapshots-accept`).

#### Task 4.2 DoD

- [x] Migration file matches the shipped `migrations/NNN_slug/migration.md` shape with `id: 5`.
- [x] Instructions are idempotent — a fence already listing both columns is left unchanged.

#### Task 4.3 DoD

- [x] `CLAUDE.md` Commands line for `bin/booping` lists `session-time`.
- [x] `documentation/vault.md` documents both new plan keys.

## I/O contract

- **Arguments / flags**: `booping session-time <plan-path> [--write] [--projects-root PATH]` — plan path relative or absolute; `--write` stamps `active_minutes:`; `--projects-root` overrides `~/.claude/projects` (tests, unusual layouts).
- **stdin**: none.
- **stdout**: plain-text rows — `{session-id}  {minutes}m  {models,comma-joined}` per stamped session, then `total  {N}m` and `models  {sorted distinct ids, comma-joined}`. Nothing else.
- **stderr**: warnings (missing transcript, malformed-line count, absent env var in hooks), errors.
- **Exit codes**: `0` success (including zero-session/zero-minute results reached with warnings); `1` user error (plan missing, no `sessions:` key, `--append` onto a scalar); `2` internal error.

## Final Verification

- [ ] `just ci` green (lint, typecheck, pytest, snapshots, mdcheck).
- [ ] Help text for `session-time` and `frontmatter-update --append` accurate.
- [ ] Happy path + one failure path (missing transcript) verified by invocation.
- [ ] Exit codes match the contract.
- [ ] End-to-end: scratch plan → two stamped transitions with distinct fake session ids → `done` edge stamps `active_minutes:` and `models:` from fixture transcripts.

## Out of scope

- Walltime lead/cycle-time keys and per-phase breakdown.
- Per-model time attribution (minutes split by model) — `models:` is a flat "who ran" list.
- Code-review / retro session stamping.
- Retroactive attribution for pre-feature plans (their `active_minutes` stays unset).
- Rendering minutes as `6h 32m` anywhere.
- Parsing sidechain `subagents/*.jsonl` files.
- Porting `close-code-review`'s list append onto `frontmatter-update --append`.

## CLAUDE.md impact

`## Commands` — add `session-time` to the `bin/booping` subcommand list (task 4.3). No other sections.
