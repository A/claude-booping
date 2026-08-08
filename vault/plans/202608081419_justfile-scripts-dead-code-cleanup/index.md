---
title: Justfile script extraction and dead-code cleanup for release
type: refactoring
status: done
sp: 13
split_from: null
created: 2026-08-08 14:19
planned: null
started: 2026-08-08 15:20
completed: 2026-08-08 20:15
code_reviews: null
retro: null
goal: null
summary: "Extract justfile bash bodies into scripts/ as uv Python, move eval tooling
  there, delete dead bin scripts"
commit: 7ae215b4abafa9e41b400c73129f4d885fd39b1c
sessions:
- 10075296-e161-4cfc-8241-41b3ad4aa27f
- 86d771e1-d30c-4015-9983-7346c81dd1b5
- 5a8c526f-60f5-4f1e-9902-4e78fd319c9f
agents:
  research-codebase-scripts: a3fc981a3f3acaf61
  research-codebase-deadcode: a043a0df3ce8cf442
  develop-loop-g1: ab292aa545075dbdd
  develop-loop-g2: ae0143799914e5dd2
  develop-loop-g3: a578cb4bf84ee3393
  develop-loop-g4: a346a6419253e017d
reviewed_at: 2026-08-08 15:09
metrics_active_minutes: 41
metrics_models:
- claude-fable-5
metrics_tokens_input: 416
metrics_tokens_output: 172168
metrics_tokens_cache_creation: 1037063
metrics_tokens_cache_read: 17070196
---

# Justfile script extraction and dead-code cleanup for release

## Context

The justfile carries three multi-line inline bash bodies (`mdcheck`, `snapshots`, `snapshots-render`) while other recipes delegate to `bin/*.sh`; `bin/` mixes the product CLI wrapper (`booping`) with dev tooling (`eval-*.sh`, `report-*.jq`) and two dead scripts. After this plan: every justfile recipe is a one-liner; all dev tooling lives in a new `scripts/` directory, with the snapshots and mdcheck logic as uv-run Python scripts; `bin/` holds only `booping`; confirmed-dead code (`booping-create-project`, `booping-external-llm-call` + its template dir, two `_old_skill.md` report fossils, `playbooks/_lib/step_prompt.py`) is deleted with its doc references cleaned in the same sprint. No recipe changes name or observable behavior.

## Decisions

- **Script language**: snapshots and mdcheck logic become Python uv inline scripts (PEP 723 header, stdlib-only) — user preference; richer than bash for the diff/report loops, no dependency footprint.
- **Scripts home**: new `scripts/` for ALL dev tooling, including the existing `eval-*.sh` / `*.jq` group; `bin/` keeps only product entry points — user decision at intake.
- **Snapshots wiring**: `scripts/snapshots.py` owns the whole snapshots surface (`render` / `check` / `accept` modes) and calls its own render function internally — drops the `{{ just_executable() }}` re-invocation dependency entirely.
- **Repo-root resolution**: each Python script resolves the repo root from its own location (`Path(__file__).resolve().parent.parent`) instead of assuming cwd — just ran inline bodies at the justfile dir implicitly; extracted scripts must not depend on that.
- **Eval scripts move as-is**: the `eval-*.sh` + `*.jq` group is sibling-relative and self-contained; `git mv` plus justfile/CLAUDE.md path updates, no logic edits.
- **`booping-create-project` deleted**: setup playbook + `booping scaffold` supersede it; the script's tree is stale (`lessons/` vs `_lessons/`, no `sprints.md`, no symlink/git-init). Setup specs already record it as unmigrated debt.
- **`booping-external-llm-call` deleted**: Gemini cross-validation caller retired with the pre-1.0 `/groom` skill; nothing invokes it; `llm-call-templates/` goes with it.
- **`playbooks/_lib/step_prompt.py` deleted**: no `promptfooconfig.yaml` declares it — user decision; git history preserves it.
- **`_specs/` documented, not deleted**: per-playbook `_specs/` dirs are playbook-authoring run artifacts (design history, intentionally stale); one Layout line in CLAUDE.md so future sweeps don't flag them.
- **Snapshot baselines**: source edits that drift committed reports (setup step prose) follow the standard loop — the develop run shows `just snapshots` drift; `just snapshots-accept` is run only at that milestone's review with the user's go-ahead.

## Architecture

`justfile` recipes stay the single entry surface (`just snapshots`, `just mdcheck`, `just ci` unchanged in name and semantics); each becomes a one-liner delegating to `scripts/`. CI (`.github/workflows/ci.yml`) calls just targets only and is untouched. `scripts/snapshots.py` shells out to `bin/booping render-playbook` (product CLI stays in `bin/`) and to `diff --color -u` for byte-identical drift output; `scripts/mdcheck.py` shells out to the external `mdcheck` binary. The moved eval scripts keep their sibling-relative resolution (`dirname BASH_SOURCE`); `eval-target.sh` resolves the repo root as one-level-above-own-dir, which `scripts/` preserves.

## Milestones

### M1: Snapshots + mdcheck as Python scripts — 7 SP | done

**Goal**: the three inline justfile bodies are gone; `just snapshots`, `just snapshots-render`, `just snapshots-accept`, `just mdcheck` behave identically via `scripts/snapshots.py` and `scripts/mdcheck.py`.

**Verify**: `just snapshots && just mdcheck && echo OK` prints OK on a clean tree; `just snapshots-render --fixture --dest /tmp/snap-test groom` writes `/tmp/snap-test/groom/_reports/output.md`; introduce a one-char edit to a committed report → `just snapshots` exits 1 naming the playbook, revert.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Write `scripts/snapshots.py` (uv inline script, stdlib-only): `render` mode replicating `snapshots-render` (flags `--fixture`, `--dest DIR`, optional playbook glob narrowing; fixture → `output.md` + fail on `**STOP`, local → `local.md` + print STOP lines), `check` mode replicating `snapshots` (fixture render into a temp dir, `diff --color -u` per report with the same labels, drift summary + accept hint on stderr, exit 1), `accept` mode replicating `snapshots-accept` (fixture render into `playbooks/`). Repo root resolved from script location. | `scripts/snapshots.py` | 4 | done |
| 1.2 | Write `scripts/mdcheck.py` (uv inline script, stdlib-only): missing-binary guard (exit 127 + install hint on stderr), loop `playbooks/*/_reports/output.md` running shared `playbooks/_lib/report.rules.yaml` plus per-playbook `rules.yaml` when present, aggregate findings vs rule-file errors, exits 0/1/2 matching the current body. | `scripts/mdcheck.py` | 2 | done |
| 1.3 | Rewire justfile: `snapshots`, `snapshots-render`, `snapshots-accept`, `mdcheck` become one-line delegations (`uv run scripts/snapshots.py check`, `… render {{ args }}`, `… accept {{ target }}`, `uv run scripts/mdcheck.py`); keep recipe names, docs and `[doc]` attributes; move body comments into the scripts. | `justfile` | 1 | done |

#### Task 1.1 DoD

- [x] `uv run scripts/snapshots.py check` on a clean tree exits 0 silently (reports listed as today).
- [x] `check` against a hand-drifted report exits 1, prints the colored unified diff with `playbooks/{name}/_reports/output.md` labels, names the drifted playbook and the accept hint on stderr.
- [x] `render --fixture` fails (exit 1) listing playbooks whose report contains a `**STOP` line; `render` without `--fixture` prints STOP lines but exits 0.
- [x] `render --dest DIR name` narrows to one playbook and writes under DIR.
- [x] `accept` rewrites committed reports byte-identically to today's `just snapshots-accept`.
- [x] Script runs from any cwd (root resolved from file location).

#### Task 1.2 DoD

- [x] Clean tree: exit 0, no output.
- [x] Missing `mdcheck` binary: exit 127, stderr carries the `cargo install markdown-checker` hint.
- [x] A report violating shared rules: exit 1, `mdcheck findings:` line on stderr naming report + rules file.
- [x] A broken rules file: exit 2, `mdcheck rule-file or internal error` line, deduped per rules file.
- [x] Per-playbook `_reports/rules.yaml` still runs in addition to the shared rules.

#### Task 1.3 DoD

- [x] No recipe in the justfile carries a `#!/usr/bin/env bash` body.
- [x] `just --list` output unchanged (names + doc strings).
- [x] `just ci` passes end to end. (pre-existing groom/migrate snapshot drift accepted by the user via `just snapshots-accept`; CI green after.)

---

### M2: Eval tooling moves to scripts/ — 2 SP | done

**Goal**: `bin/` contains only `booping`; the eval script group lives in `scripts/` and every reference points there.

**Verify**: `ls bin/` prints exactly `booping`; `just suites` lists the suites; `git grep -n 'bin/eval\|bin/report'` returns nothing.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | `git mv` `eval-run.sh`, `eval-md.sh`, `eval-target.sh`, `eval-pr-comment.sh`, `report-md.jq`, `report-pr.jq` from `bin/` to `scripts/`; update the five justfile references and the `bin/eval-pr-comment.sh` mention in CLAUDE.md; no logic edits (group is sibling-relative, root resolution depth unchanged). | `scripts/*`, `justfile`, `CLAUDE.md` | 2 | done |

#### Task 2.1 DoD

- [x] `just suites` exits 0 and lists the same suites as before the move.
- [x] `git grep -n 'bin/eval\|bin/report'` is empty.
- [x] Moved scripts keep execute bits.
- [x] CLAUDE.md names `scripts/eval-pr-comment.sh` at the eval bullet.

---

### M3: Dead code deleted — 3 SP | done

**Goal**: the four confirmed-dead surfaces are gone and no doc line points at them.

**Verify**: `git grep -n 'booping-create-project\|external-llm-call\|llm-call-templates\|step_prompt\|GEMINI_API_KEY' -- ':!playbooks/*/_specs' ':!plans'` returns nothing; `just ci` passes.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Delete `bin/booping-create-project`; drop its CLAUDE.md Commands bullet; rewrite the `documentation/project_config.md` home-dir-ladder passage to describe the setup playbook / `booping scaffold` path instead; remove the "booping-create-project is a different path" sentence from `playbooks/setup/setup-project/opus-5.md` (drifts the setup report — standard snapshot loop, acceptance at review). `_specs/` history mentions stay. | `bin/booping-create-project`, `CLAUDE.md`, `documentation/project_config.md`, `playbooks/setup/setup-project/opus-5.md` | 1 | done |
| 3.2 | Delete `bin/booping-external-llm-call` and `bin/llm-call-templates/`; drop the `GEMINI_API_KEY` prerequisite line from `documentation/quick_start.md`. | `bin/booping-external-llm-call`, `bin/llm-call-templates/`, `documentation/quick_start.md` | 1 | done |
| 3.3 | Delete `playbooks/learn/_reports/_old_skill.md`, `playbooks/retro/_reports/_old_skill.md`, `playbooks/_lib/step_prompt.py`. | three deletions | 1 | done |

#### Task 3.1 DoD

- [x] Script gone; `git grep booping-create-project -- ':!playbooks/*/_specs/**' ':!plans'` empty (sole hit is the stale committed setup baseline awaiting acceptance).
- [x] `documentation/project_config.md` passage points at `/playbook setup` + `booping scaffold`, no dangling ladder prose.
- [x] `just snapshots` drift limited to the setup report's removed sentence.

#### Task 3.2 DoD

- [x] Script + template dir gone; no `GEMINI_API_KEY` or `external-llm-call` mention outside `_specs/`.

#### Task 3.3 DoD

- [x] Three files gone; `git grep step_prompt` empty; `just eval groom/intake --help`-level smoke (`just suites`) still exits 0.

---

### M4: CLAUDE.md layout + commands sweep — 1 SP | done

**Goal**: CLAUDE.md reflects the new tree: `scripts/` exists, `bin/` is product-only, `_specs/` is explained.

**Verify**: CLAUDE.md Layout section names `scripts/` and `playbooks/*/_specs/`; `git grep -n 'bin/' CLAUDE.md` shows only `bin/booping` mentions.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Add a `scripts/` Layout bullet (dev tooling: snapshots, mdcheck, eval harness), tighten the `bin/` bullet to product-entry-points-only, add a one-line `playbooks/*/_specs/` bullet (playbook-authoring design history, intentionally stale), and re-check the Commands section paths after M1–M3. | `CLAUDE.md` | 1 | done |

#### Task 4.1 DoD

- [x] Layout lists `scripts/` and `_specs/` with one-line descriptions.
- [x] No CLAUDE.md line references a deleted or moved path.

---

## I/O contract

- **`scripts/snapshots.py`**: `uv run scripts/snapshots.py {render|check|accept} [--fixture] [--dest DIR] [playbook]` — `render` honors all three options; `check` takes no options; `accept` takes only the optional playbook. stdout: report paths as today (`check` adds unified diffs); stderr: drift/STOP summaries + accept hint. Exit codes: `0` clean, `1` drift or STOP findings, `2` internal error (render failure propagates).
- **`scripts/mdcheck.py`**: no arguments. stdout: none. stderr: findings / error lines in today's wording. Exit codes: `0` clean, `1` findings, `2` rule-file or internal error, `127` mdcheck binary missing.
- **Moved eval scripts**: contract unchanged — invoked only through just recipes.

## Final Verification

- [ ] `just ci` green.
- [ ] `just --list` names and doc strings unchanged.
- [ ] `ls bin/` → `booping` only.
- [ ] Happy path + one failure path verified per new script (drifted report → exit 1; missing mdcheck binary → exit 127).
- [ ] Exit codes match the I/O contract.

## Out of scope

- No release mechanics — no version bump, changelog, or `/release` involvement.
- No behavior or naming changes to any just recipe; no CI workflow edits.
- No logic edits to the moved eval scripts.
- No deletion or rewrite of `playbooks/*/_specs/` content.
- No prose-shape reshape milestone (confirmed at intake).

## CLAUDE.md impact

Commands section: `bin/eval-pr-comment.sh` → `scripts/eval-pr-comment.sh`; drop the `bin/booping-create-project` bullet. Layout section: add `scripts/`, tighten `bin/`, add `playbooks/*/_specs/`. All carried as tasks 2.1, 3.1 and 4.1.
