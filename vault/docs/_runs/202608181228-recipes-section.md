---
title: Recipes section
status: researching
started: 2026-08-18 12:30
commit: 999e07f2b6c9c58c760e7c47491cf06bf395f6f1
scope_reviewed_at: 2026-08-18 14:11
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

- In scope: `plans/202608102115_pi-developer-userland-wiring/index.md` and `plans/202608141156_benchmark-scoring/index.md`, read as source for two user-dictated recipes.
- Deliverable: a new **recipes** section on the public docs site (`documentation/`), two guides: (1) wiring external agents (codex, pi-developer, …) — the agent proxy pattern; (2) benchmarks — how they work at a high level, how to set up and run one, and the orchestrate-vs-loop-vs-direct insight (direct wins).
- Recipes are not a delivered-work surface: their content is dictated by the user, blogpost-like. Docs sweeps may review an existing recipe during `update`, but never generate or extend one from the change table.
- Out of scope: the other 8 undocumented items — they stay outside the ledger and resurface at the next survey.
- Spec files: none flagged for refresh; `_specs/targets.md` gains the recipes surface via research → sync-specs.
