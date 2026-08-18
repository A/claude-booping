---
title: Recipes section
status: updating
started: 2026-08-18 12:30
commit: 999e07f2b6c9c58c760e7c47491cf06bf395f6f1
scope_reviewed_at: 2026-08-18 14:11
changes_reviewed_at: 2026-08-18 14:24
targeting_reviewed_at: 2026-08-18 14:29
---

# Recipes section

## Spec set

| File | State | Gap |
| --- | --- | --- |
| `_specs/index.md` | present | — |
| `_specs/roles.md` | present | — |
| `_specs/targets.md` | present | — |
| `_specs/features.md` | present | — |

4 of 4 usable — `index.md` carries What it is / Who it serves / Where it is heading, `roles.md` one section per audience (Users, Advanced users, Contributors) each with Who / Comes for / Depth / Tone / Withhold / Reads, `targets.md` the surface table plus its Not surfaces exclusions, `features.md` the Framework and Core playbook set group tables plus NFRs and Not features; all four are complete and none needs a spec wave.

## Undocumented work

| Work item | Status | Landed | Headline |
| --- | --- | --- | --- |
| `plans/202608101646_milestone-files-for-dev-agents/index.md` | done | 2026-08-10 | Per-milestone plan files handed straight to dev agents |
| `plans/202608102115_pi-developer-userland-wiring/index.md` | done | 2026-08-11 | Userland pi-developer wiring — develop milestones via a local pi worker |
| `plans/202608111422_e2e-contract-corpus-pilot/index.md` | done | 2026-08-11 | E2E contract-corpus pilot — convert one command's tests |
| `plans/202608121206_txtar-runner-extraction/index.md` | done | 2026-08-12 | Extract the txtar contract runner into a standalone reusable module |
| `plans/202608121417_frontmatter-update-e2e-migration/index.md` | done | 2026-08-12 | Migrate frontmatter-update tests from units to the txtar e2e corpus |
| `plans/202608130839_cli-tests-to-e2e-corpus/index.md` | done | 2026-08-13 | Migrate config-get, marker-set and query tests to the txtar e2e corpus |
| `plans/202608131129_remaining-cli-tests-to-e2e/index.md` | done | 2026-08-13 | Migrate render-playbook and playbook-transition tests to the txtar e2e corpus |
| `plans/202608131522_final-cli-commands-to-e2e/index.md` | done | 2026-08-13 | Migrate the last CLI commands to the txtar e2e corpus |
| `plans/202608132333_task-tracker-driver-linear/index.md` | done | 2026-08-14 | Task-tracker driver layer and Linear-driven plan track |
| `plans/202608141156_benchmark-scoring/index.md` | done | 2026-08-14 | Benchmark scoring — per-model scorecard for the fixed develop-sprint benchmark |

10 items outside the ledger, landing 2026-08-10 → 2026-08-14; the ledger holds 58 rows, its most recent `plans/202608091310_scaffold-seeded-plan-creation/index.md` (documented by `_runs/202608101223-docs-refresh.md`).

## Scope

Confirmed 2026-08-18: narrow — only the recipes ask.

- In scope: `plans/202608141156_benchmark-scoring/index.md`, plus the user's own ask — the recipes section itself.
- Deliverable: a new **`documentation/recipes/`** directory — each recipe a blogpost-like guide on doing something non-trivial with booping, linked from the README. Two initial recipes: (1) wiring external agents (codex, pi-developer, …) — the agent proxy pattern; (2) benchmarks — how they work at a high level, how to set up and run one, and the orchestrate-vs-loop-vs-direct insight (direct wins).
- Recipes are not a delivered-work surface: their content is dictated by the user, blogpost-like. Docs sweeps may review an existing recipe during `update`, but never generate or extend one from the change table.
- Out of scope: `plans/202608102115_pi-developer-userland-wiring/index.md` (not a feature — its wiring only serves as material for recipe 1) and the other 8 undocumented items — all stay outside the ledger and resurface at the next survey.
- Spec files: none flagged for refresh; `_specs/targets.md` gains the recipes surface via research → sync-specs.

## Changes

| # | Work item | Type | What changed | Audience | Target files | Spec-set effect |
| --- | --- | --- | --- | --- | --- | --- |
| C1 | User ask (this run) — the recipes section | new feature | The docs site gains `documentation/recipes/` — each recipe a blogpost-like guide on doing something non-trivial with booping, its content dictated by the user, linked from the README. Two initial recipes: wiring external agents (codex, pi-developer, …) via the agent-proxy pattern — a thin `~/.claude/agents/` agent relays the work, vault config points a playbook's agent slot at it — and the model benchmarks guide. | Advanced users | `documentation/` (recipes), `README.md`, `docs/_specs/` | `targets.md`: the surface table gains `documentation/recipes/` — user-dictated guides, reviewed on update sweeps but never generated from the change table |
| C2 | Benchmark scoring — per-model scorecard for the fixed develop-sprint benchmark | new feature | Model benchmarking runs as a user playbook — prepare / run / measure / publish — with a `bench-score` script computing gates, corpus quality, mutation kill-rate, process cost and review scores, appending one comparable scorecard row plus a per-run detail report. Insight to carry: direct orchestration beats `/orchestrate` and `/loop` — `/loop` earned nothing for its overhead and is retired. The user dictates the recipe: how benchmarks work, how to set up and run one, and that insight. | Contributors | `documentation/` (recipes), `docs/_specs/` | none beyond C1's `targets.md` edit — benchmark machinery is vault content exercising the plugin, not a plugin feature |

2 rows — 1 in-scope work item plus the run's own ask; 2 new feature; spec-set effect: `targets.md` (one edit, the recipes surface row).

## Targeting plan

| Destination | Roles | Changes | Must say | Progress |
| --- | --- | --- | --- | --- |
| `documentation/recipes/external-agents.md` | Advanced users | C1 | The agent-proxy pattern as a blogpost-like walkthrough: any external agent — codex, a headless pi session, anything with a CLI — joins a playbook through a thin `~/.claude/agents/` proxy agent that relays the work and returns the report, with vault config pointing the playbook's agent slot at it. Worked examples: codex (relay to `codex exec`) and pi-developer (milestone handed to a headless pi session). Links `../integrating-external-agents.md` for the dry mechanics rather than restating them. | pending |
| `documentation/recipes/benchmarks.md` | Contributors | C1, C2 | The benchmarks recipe: how the fixed develop-sprint benchmark works at a high level (throwaway workspace, autonomous sprint on its own branch, `bench-score` computing gates, corpus quality, mutation kill-rate, process cost and review scores into one comparable scorecard row plus a detail report); how to set one up and run it in your own vault; the insight — direct orchestration beats `/orchestrate` and `/loop`, `/loop` retired as pure overhead. | pending |
| `README.md` | Users | C1 | One short pointer to the recipes section on the docs site — guides for non-trivial uses of booping — beside the existing docs-site links; no recipe content inlined. | pending |

## Not targeted

- *(none — both confirmed changes are assigned)*

Runner note: `mkdocs.yml` (not markdown, outside the loop) needs a `Recipes` nav section for the two new pages — `strict: true` fails the build otherwise; the runner edits it beside the loop.
