---
title: "Docs playbook on specs records — retire vault/docs/_specs"
type: "refactoring"
status: done
sp: 35
related_to: null
created: 2026-10-14 22:51
planned: null
started: 2026-10-14 22:59
completed: 2026-10-14 23:19
code_reviews: []
sessions:
- e46d0ff7-edb0-438e-96f5-d7315b54c5cc
- 95e3e021-3f47-4205-baa8-77d443b36758
retro: null
summary: Docs playbook reads and edits specs records; feature index rendered 
  from stories; vault/docs/_specs deleted
commit: 10e82bb3e3f164db3d3da3e6cdf96d514ae5526c
tracker_provider: null
tracker_request: null
tracker_issue: null
return_to: null
agents: '{"cross-review": "a12cfe89d62b28a3c", "develop-loop/M01": "a8a70eef3f292022a",
  "develop-loop/M02": "adc4479b1412ed1af", "develop-loop/M03": "a7e903cea9d61b2e6",
  "develop-loop/M04": "ac6bd4506b5c5d5eb", "develop-loop/M05": "a1f9b87087ca6f1e0",
  "develop-loop/M06": "a50beac9f9bbc7743", "verify": "ad8a57abb3020c12d"}'
reviewed_at: 2026-10-14 22:58
metrics_active_minutes: 32
metrics_models:
- claude-opus-5-5
metrics_tokens_input: 158
metrics_tokens_output: 62250
metrics_tokens_cache_creation: 294190
metrics_tokens_cache_read: 8581962
---

# Docs playbook on specs records — retire vault/docs/_specs

## Context

The project-local `docs` playbook (`vault/_playbooks/docs/`) keeps its own model of the project in `vault/docs/_specs/` — briefing, roles, targets, feature index, glossary and the `documented.md` ledger — and stamps `reviewed_at` on those files at its gates. The same facts now live as typed records in `vault/specs/` (value records, reference/0001 audience, reference/0002 glossary, reference/0003 surfaces, story records), and adr/0001 deprecated the old set until this switch. After this plan, every docs step reads the records, `roles` / `targets` / `sync-specs` edit them (marking what their source does not settle, rule/0002), the feature index is rendered from the story records, review stamps land on the run record, and `vault/docs/_specs/` is gone with every pointer to it.

Goal ([value/0003](../../specs/value/0003-single-source.md)): one model of the project, no parallel copy to drift. The documentation the playbook produces is unchanged — same surfaces, run record, changelog entry and ledger. Request and defaults: [request.md](request.md), [clarifications.md](clarifications.md).

## Decisions

- **Ledger**: `vault/docs/documented.md`, moved with history; `close-documented` writes it — C1.
- **Briefing**: a `## Briefing` section of the run record, built from the value records (query spec) and reference/0001; vision shift against the previous run record's briefing — C2.
- **Review stamps**: `briefing_reviewed_at`, `specs_reviewed_at` on the run record; a record's `reviewed` is the owner's alone, a step bumps `updated_at` — C3.
- **Feature index**: the `feature-index` step and its gate go; `core.docs_playbook.queries.features` over the story records renders into `research` and `targeting`; groups dropped, placement by story — C4.
- **sync-specs fold**: row type → record action table; values never rewritten, only `[clarify]`-marked; ends with `booping specs check` — C5.
- **Sources**: 32 `sources:` entries repoint to a `gh/master` permalink pinned at `c7e43b4` — C6.
- **Survey**: judges records with `booping specs check` plus open-mark counts; spec waves when reference/0001 or 0003 is not present — C7.
- **Commits**: `commit-docs` commits `{vault}/docs` and `{vault}/specs` — C8.
- **Report**: regenerated with a stubbed date; no evals exist beside the docs steps — C9.

## Architecture

```
survey ──► briefing ──► roles ──┐            (spec waves, skipped when records are present)
  │  specs check   │ values q   ├─► research ──► sync-specs ──► targeting ──► update × N ──► changelog ──► record
  │  ledger        ▼ run record │   features q    records +       features q                                 close-documented
  ▼                 ## Briefing  targets          [clarify]/[unknown]                                         → docs/documented.md
 run record      ref/0001, ref/0003                specs check
```

Load-time inputs: `core.docs_playbook.queries.values` and `.features` (vault `config.yaml`) rendered with `| query` into `briefing`, `research`, `targeting`. Records under `vault/specs/` are read by path; the run record under `vault/docs/_runs/` carries the briefing and every review stamp. `commit-docs` scopes its pathspec to `vault/docs` and `vault/specs`.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [Ledger move, hook scripts and story/value query specs](milestones/M01-ledger-scripts-queries/M01-ledger-scripts-queries.md) | 4 | done |
| 02 | [Manifest and guidance on records — feature-index step and its gate removed](milestones/M02-manifest-and-guidance/M02-manifest-and-guidance.md) | 5 | done |
| 03 | [Survey judges records, briefing reads values into the run record](milestones/M03-survey-and-briefing/M03-survey-and-briefing.md) | 6 | done |
| 04 | [Roles and targets refresh reference/0001 and reference/0003](milestones/M04-roles-and-targets-on-records/M04-roles-and-targets-on-records.md) | 4 | done |
| 05 | [Research, sync-specs and targeting work on records](milestones/M05-change-set-steps-on-records/M05-change-set-steps-on-records.md) | 10 | done |
| 06 | [Retire vault/docs/_specs — sources, deprecation notes, report](milestones/M06-retire-docs-specs/M06-retire-docs-specs.md) | 6 | done |

## Final Verification

- [ ] `just ci` green (lint, typecheck, pytest, snapshots, mdcheck, specs-check, e2e) — `just snapshots` is expected clean: no core playbook source changes.
- [ ] `bin/booping render-playbook docs` renders with no STOP notice; the committed `vault/_playbooks/docs/_reports/output.md` equals a fresh `--stub-macro core.macros.date=2026-10-14` render.
- [ ] Every docs step body (`--step` for survey, briefing, roles, targets, research, sync-specs, targeting, write, compact, verify, changelog, record) renders and names no `_specs/` path.
- [ ] `git grep -n 'docs/_specs'` outside history paths and the pinned permalinks finds nothing.
- [ ] Rendered bodies reviewed: no stale status names (`awaiting-features-confirm`), no restated query globs, no `{{placeholder}}` leaks.

## Out of scope

- The specs format itself — no new story fields (groups), no schema change.
- `vault/_lessons/` and its deprecation notes — lesson injection still reads it.
- History: `vault/docs/_runs/`, plans, retrospectives, researches, and the playbook-authoring design history in `vault/_playbooks/docs/_specs/` and `playbooks/*/_specs/`.
- Core playbooks, `src/`, `booping-python/` — nothing outside the docs playbook, its config, the records and `CLAUDE.md`.
- Running the docs playbook end to end; promptfoo evals for docs steps (none exist).

## CLAUDE.md impact

Vault section: the `docs/_specs/` sentences are replaced by one naming the records the `docs` playbook reads and keeps current — owned by M06 task 6.2.
