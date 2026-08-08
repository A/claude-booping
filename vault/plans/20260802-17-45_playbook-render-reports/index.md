---
status: done
title: Justfile recipe rendering core playbooks into committed report files
type: feature
created: 2026-08-02 17:45
plan_status: ready-for-dev
sp: '10'
summary: Justfile recipe renders core playbooks to committed _reports/output.md 
  deterministically via --set config overrides
agents:
  cross-review: aa90516b3b4db9c7a
  develop-loop: a3eff576c327fc0dd
  verify: ab3e518b54f77c509
reviewed_at: 20260802 11:04
started: 20260802 11:06
commit: 585aa7cd7d8f26b827a9f0a414c90bb0ed77ca38
completed: 2026-08-02 11:26
sessions:
- 6e123186-f50f-4426-9495-00037a51d682
- c1305580-f7b3-4844-9efb-0699e82003df
metrics_active_minutes: 31
metrics_models:
- claude-fable-5
metrics_tokens_input: 353
metrics_tokens_output: 162978
metrics_tokens_cache_creation: 816395
metrics_tokens_cache_read: 16335685
---

# Justfile recipe rendering core playbooks into committed report files

## Context

Affects the `booping render-playbook` subcommand and the repo `justfile`. Today the composed render of a core playbook (`develop`, `groom`, `playbook-authoring`) is visible only by running the CLI locally; PRs touching playbook sources show template diffs, not the rendered procedure. Additionally every render is nondeterministic: the Jinja `now()` global stamps the current time, and groom's intake body renders a `## Latest Plans` table from live vault state.

After this plan: `just playbook-reports` renders every core playbook deterministically into `playbooks/{name}/_reports/output.md`, and CLAUDE.md instructs running it after playbook edits — so rendered output is part of every playbook PR diff, with no diff when nothing real changed.

## Decisions

- **Config override surface**: repeatable `--set dotted.key=value` flag on `render-playbook`, deep-merged as a final override tier after core → global → project — reuses the existing `Config.load` merge machinery; generic, not date-specific (user asked for kv-pairs overlapping existing config).
- **Date pin**: `now()` consults the resolved config key `now` — when present, returns its value verbatim (format argument ignored). Recipe passes `--set now=19700101-00-00`. Both injection points (`rendering.py`, `render_playbook.py`) get the config-aware closure so skill renders and playbook renders behave alike.
- **Vault determinism**: reports render with `--project playbooks/_fixtures/vault` — a dedicated committed minimal fixture vault (empty `plans/`, `config.yaml` mirroring the attached project's `cross_review.agent: codex` so the cross-review step renders in its real detached form). Dedicated rather than reusing `booping-python/tests/__fixtures__` so test edits never churn reports.
- **Report location**: `playbooks/{name}/_reports/output.md` — underscore prefix keeps step discovery from warning on a non-step dir.
- **Full render**: lessons included, no `--no-lessons` (user decision; with the fixture vault, vault-side lessons drop out naturally and only committed core-side lessons appear — churn only on real lesson changes).
- **Enumeration**: dynamic shell loop over `playbooks/*/playbook.md` — new core playbooks picked up automatically; `_`-prefixed dirs excluded by requiring `playbook.md`.
- **Recipe name**: `playbook-reports`.
- **Residual nondeterminism accepted**: absolute plugin-root paths in rendered tables (e.g. plan-template `Read from` column) are machine-dependent but stable for the single-dev repo. Out of scope to relativize.

## Architecture

`just playbook-reports` → for each `playbooks/<name>/playbook.md` → `bin/booping render-playbook <name> --project playbooks/_fixtures/vault --set now=19700101-00-00 --output playbooks/<name>/_reports/output.md`. The reports are committed artifacts; `git diff -- playbooks/*/_reports/` after the recipe is the drift signal, same pattern as `just build` for `skills/`/`agents/`. Consumers: human PR review only — no skill or agent reads `_reports/`.

`--set` merge point: `render_playbook._run` resolves context via `Context.assemble`; the flag's parsed pairs form an in-memory mapping deep-merged over the resolved config before the env is built. Dotted keys expand (`a.b=c` → `{a: {b: c}}`); values stay strings.

## Milestones

### M1: `--set` config override flag on render-playbook — 3 SP | done

**Goal**: `render-playbook` accepts repeatable `--set dotted.key=value` and the values win over every config tier.

**Verify**: `cd booping-python && uv run pytest -k "set_override"` green; after M2: `bin/booping render-playbook groom --project playbooks/_fixtures/vault --set now=19700101-00-00 | grep "19700101-00-00"`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Add repeatable `--set KEY=VALUE` to the `render-playbook` parser; parse dotted keys into a nested mapping (malformed pair without `=` → stderr + exit 1); deep-merge it as the final tier over the resolved config before env build. Tests: override wins over core value, dotted nesting, repeated pairs later-wins, malformed pair exits 1, no `--set` unchanged. | `booping-python/src/booping/commands/render_playbook.py`, `booping-python/src/booping/context/config.py`, `booping-python/tests/` | 3 | done |

#### Task 1.1 DoD

- [x] `--set a.b=c` visible as `config.a.b == "c"` in a rendered template.
- [x] `--set` repeatable; later pairs win over earlier.
- [x] Malformed pair (no `=`) → stderr message + exit 1.
- [x] `render-playbook --help` documents the flag.
- [x] Tests green: `just test`.

Agent return contract: list of changed files + one test summary line, nothing else.

---

### M2: pinnable `now()` — 2 SP | done

**Goal**: with config key `now` set, every `now(...)` call in any rendered body returns that value verbatim; unset → current behavior.

**Verify**: `bin/booping render-playbook groom --project playbooks/_fixtures/vault --set now=19700101-00-00` run twice, `diff` of the two outputs empty and both contain the sentinel.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Replace the bare `now` global with a config-aware closure at both injection points (`rendering.py` env build, `render_playbook.build_env`): config `now` present → return it verbatim ignoring `fmt`; absent → `datetime.now().strftime(fmt)`. Tests: pinned value returned for any fmt, unpinned output still time-shaped. | `booping-python/src/booping/rendering.py`, `booping-python/src/booping/commands/render_playbook.py`, `booping-python/tests/` | 2 | done |

#### Task 2.1 DoD

- [x] Pinned render contains the sentinel wherever `now()` is called, any format string.
- [x] Unpinned render unchanged (matches `%Y%m%d-%H-%M` shape).
- [x] Tests green: `just test`.

Agent return contract: list of changed files + one test summary line, nothing else.

---

### M3: committed fixture vault — 2 SP | done

**Goal**: `playbooks/_fixtures/vault/` renders every core playbook with `--project` cleanly and deterministically.

**Verify**: render groom twice against the fixture with the pin, `diff` empty; output has no STOP/Note notices; cross-review step renders detached naming `codex`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Create minimal fixture vault: whatever marker/config files `--project` resolution requires, empty `plans/`, `config.yaml` with `cross_review.agent: codex`; confirm all three core playbooks render against it without notices and with an empty Latest Plans table. | `playbooks/_fixtures/vault/**` | 2 | done |

#### Task 3.1 DoD

- [x] All three core playbooks render against the fixture with exit 0 and no STOP/Note notices.
- [x] Groom's Latest Plans table renders empty (fixture has no plans).
- [x] Cross-review step renders in detached form naming `codex`.
- [x] Back-to-back renders byte-identical (with M2's pin).

Agent return contract: fixture file list + the three render exit codes, nothing else.

---

### M4: `playbook-reports` recipe + first reports — 2 SP | done

**Goal**: `just playbook-reports` writes/refreshes all `playbooks/{name}/_reports/output.md`; stale ad-hoc output removed.

**Verify**: `just playbook-reports && git status --short playbooks/` shows only `_reports/output.md` files; second consecutive run leaves the tree unchanged; `playbooks/develop/output.md` gone.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Add `playbook-reports` recipe (comment above, matching justfile style): loop over `playbooks/*/playbook.md`, render each with `--project playbooks/_fixtures/vault --set now=19700101-00-00 --output playbooks/{name}/_reports/output.md`; any non-zero render exit fails the recipe. Generate and commit the three reports. Delete stale `playbooks/develop/output.md`. | `justfile`, `playbooks/*/_reports/output.md`, `playbooks/develop/output.md` (deleted) | 2 | done |

#### Task 4.1 DoD

- [x] `just playbook-reports` exits 0 and writes all three reports.
- [x] Second consecutive run produces no diff.
- [x] A failing render fails the recipe with non-zero exit.
- [x] `playbooks/develop/output.md` removed.

Agent return contract: list of changed files, nothing else.

---

### M5: CLAUDE.md instruction — 1 SP | done

**Goal**: the convention is documented where playbook edits are governed.

**Verify**: `grep -n "playbook-reports" CLAUDE.md` hits Editing conventions and the CLI coverage.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | CLAUDE.md: Editing conventions gains "after editing playbook sources (manifests, step prompts, `_lessons/`, shared partials they include), run `just playbook-reports`; `git diff -- playbooks/*/_reports/` is the drift signal"; CLI section documents `--set` on `render-playbook`; Layout's playbooks bullet mentions `_reports/` + `_fixtures/vault/`. | `CLAUDE.md` | 1 | done |

#### Task 5.1 DoD

- [x] Editing conventions instructs the render-after-edit step with the drift-signal command.
- [x] `--set` documented in the CLI section.
- [x] `_reports/` and `_fixtures/` named in Layout.

Agent return contract: list of changed files, nothing else.

---

## I/O contract

- **Arguments / flags**: `booping render-playbook <name> [--step NAME] [--project PATH] [--output PATH] [--no-lessons] [--inline-steps] [--set KEY=VALUE ...]` — `--set` repeatable; `KEY` dotted config path; `VALUE` string, wins over all config tiers; later repeats win.
- **stdin**: unused.
- **stdout**: rendered markdown (unchanged).
- **stderr**: malformed `--set` pair diagnostics; existing diagnostics unchanged.
- **Exit codes**: `0` success (including in-band STOP notices, unchanged); `1` user error (unknown playbook, malformed `--set`); `2` unreadable config (existing contract).
- **Recipe**: `just playbook-reports` — no args; exits non-zero when any render fails.

## Final Verification

- [ ] `render-playbook --help` shows `--set` accurately.
- [ ] Happy path: `just playbook-reports` twice → zero diff on second run.
- [ ] Failure path: malformed `--set x` → stderr + exit 1.
- [ ] `just lint && just typecheck && just test` green.

## Out of scope

- `--set` on other subcommands (`render`, `render-sprints`) — render-playbook only for now.
- Relativizing absolute plugin-root paths in rendered tables.
- CI enforcement (a workflow failing on report drift) — convention only in this plan.
- Reports for global/local (non-core) playbooks.

## CLAUDE.md impact

Covered by M5: Editing conventions (render-after-edit rule + drift signal), CLI section (`--set`), Layout (`_reports/`, `_fixtures/vault/`).
