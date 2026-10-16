---
title: "Groom one-pass draft and booping plan split"
type: "feature"
status: in-progress
sp: 26
related_to: null
created: 2026-10-16 13:20
planned: null
started: 2026-10-16 13:34
completed: null
code_reviews: []
sessions:
- bd1b4f77-6235-4b78-ae72-ccbe54f0c63a
- 9133c28e-b7c8-45c8-9714-09ab884414ba
retro: null
summary: Groom drafts one file in a research-then-draft pass; booping plan split
  cuts it into milestone files, plan check enforces the contract
commit: 5eec81700bb72c353fe05fe2378443f176555715
tracker_provider: null
tracker_request: null
tracker_issue: null
return_to: null
agents: '{"research-codebase": "a0622793ee9abd955", "cross-review": "abde18f33b0a3cdbe"}'
reviewed_at: 2026-10-16 13:33
---

# Groom one-pass draft and booping plan split

## Context

**Current state.** Groom (`playbooks/groom/`) runs intake → research-codebase → research-web → draft-plan → cross-review → present. `draft-plan` designs with the user, then writes `index.md` and seeds and writes one milestone file at a time (`booping scaffold core.groom_playbook.milestone_scaffold`), under ~45 prompt rules spread over the step body, `playbooks/_partials/milestone_contract.md`, `_partials/plan_templates.md` (which orders a Quality Checklist walk before returning) and the five `docs/plan_templates/*.md`. A run costs 13–23 min and $4.25–5.62 (adr/0030).

**Motivation.** The groom benchmark (`booping-benchmarks/groom`) found V3a — the template plus a research stage, then the draft, one file, no self-review — matches V3's quality at about half V0's time and 60% of its cost; the ablation found 16 rules the model follows unprompted and 9 milestone-shape rules it misses even when told (adr/0030). The split benchmark found a script cutting the one-file draft on its headings exact and free on 12/12 plans (adr/0031). Both ADRs were accepted by the owner on 2026-10-16.

**Scope.** This plan: `booping plan split` (port of `booping-benchmarks/groom/split/heading_cut.py` + `cut.py`) and `booping plan check` (the milestone contract as code) in booping-python with unit tests and e2e cases on four benchmark plans; groom rewritten around one `draft-plan` step that drafts `draft.md`, splits, checks and loops; the five core plan templates trimmed; groom's snapshot report accepted; docs. **Not** in scope: renaming the milestone file to `milestones/M{nn}-*/index.md`; a light path for small requests; develop reading `## Groups` instead of packing its own.

**Outcome after shipping.** A groom run is faster and cheaper at V3a quality, and the plan's text reaches the milestone files unchanged; develop, its hooks and the worker agents read exactly the layout they read today.

## Decisions

Every default this autonomous run settled is recorded as an answered question in [clarifications.md](clarifications.md) (C1–C13); the main ones:

- **Draft file**: `{plan-dir}/draft.md`, body only, kept as groom's drafting source; split writes `index.md`'s body and the milestone files from it — a failing check or a change request needs a draft to return to, and `index.md`'s frontmatter stays with the scaffold and the hooks (C1).
- **Steps**: graph `intake → draft-plan → cross-review → present`; `research-codebase` and `research-web` are deleted, the research stage over the code lives in `draft-plan`; `cross-review` stays — it is the config-gated second model (adr/0016), not a self-review (C2, C3).
- **State machine**: statuses, edges and hooks identical; only the `when`/`gates` prose of `researching → drafting` and `drafting → cross-reviewing` changes (C4).
- **Two verbs, not one**: `booping plan split` and `booping plan check` — check runs on any plan directory, re-runs after a fix without re-splitting, and keeps split a pure cut.
- **Port, tolerant**: split keeps the prototype's tolerant heading detection (path headings, embedded `# M1 —`, metadata tables) because that is what passed 12/12; the draft prompt fixes one format, the parser forgives the rest — the alternative, a strict parser, would send every off-format draft to the paid fallback.
- **Milestone files through the scaffold**: split renders each milestone's frontmatter, H1 and the four section headings from `core.groom_playbook.milestone_scaffold` in-process (`booping.context.scaffold.load` + the scaffold command's render/write path), then writes each section's lines under its heading — one definition of the file shape (value/0003).
- **Table**: split writes the `## Milestones` table in exactly the format `playbooks/develop/_scripts/refresh-milestone-table` writes (`core.plans.milestones.table_columns`, title linked to the file), so develop's first refresh is a no-op, and restamps `sp:` with the sum.
- **Groups**: develop's rule — contiguous in `id` order, sum ≤ `core.sprint.max_sp`, a lone milestone always valid, `max_sp: null` → one each; a `depends_on` naming a later milestone is a flag (C6).
- **Exit codes**: split 0 / 1 usage-config / 2 refused-or-IO / 3 no milestone headings / 4 written with flags; check 0 / 1 findings / 2 nothing to check (C5).
- **Contract check**: `verify` (exactly one command), `files` (Tasks names a path), `dod` (DoD checkboxes ≥ tasks), `sp` (set and < `core.sprint.redecompose_threshold`) — the last moves an existing prose gate into code (value/0015) (C8).
- **Fallback**: a flagged or headingless draft goes to `core.groom_playbook.split_fallback_agent` (`sonnet:medium`), which rewrites the draft into the fixed format at a `/tmp` path and writes nothing in the vault; the driver copies it over `draft.md` and re-splits. Departure from adr/0031's "Sonnet writes the files", taken to keep rule/0019 (driver owns the vault) (C7).
- **Format stated once**: the one-file milestone format is in `draft-plan`'s body, its four sub-heading names rendered from new `core.groom_playbook.split.sections`, which split also writes from; core templates keep only per-surface milestone content (C11, rule/0017).
- **Rules cut**: the 16 ablation "cut" rules (`ctx_current_state`, `decisions_justified`, `research_facts`, `arch_concrete_refs`, `arch_diagram`, `ms_index_table`, `sp_per_milestone`, `no_two_ways`, `no_tbd`, `no_similar_to`, `no_either_or`, `no_vague_tasks`, `req_coverage`, `ext_verified`, `names_consistent`, `persistence_rollback`), the anti-pattern lists and the milestone-shape items now checked by code leave all five templates and the step body; template sections stay; the Quality Checklist stays as a section but is no longer walked as a pass (C10).

**Values in play** (rule/0030): value/0012 quality at a rational cost (V3a over V3, script over Sonnet), value/0015 deterministic where it can be (split, groups, contract check and the sp gate as code), value/0003 single source (scaffold renders the file shape, config holds the section names, one grouping rule), value/0010 proven to work (e2e on real benchmark plans), value/0002 minimal effective context (rules the model follows unprompted leave the prompt). **Departures**: rule/0013 (runs never accept snapshots) — overridden for this plan by the owner's standing permission of 2026-10-14 (C12); adr/0031's "Sonnet writes the files" — narrowed to "Sonnet rewrites the draft outside the vault" for rule/0019 (C7).

## Architecture

```
intake ──► draft-plan (runner) ─────────────────────────────────────────► cross-review ──► present
             1 research stage: read the code, note facts with paths          (config-gated)    (gate)
             2 draft: template → {plan-dir}/draft.md (### M{nn} — … blocks)
             3 booping plan split draft.md --replace
                 exit 3 / exit 4 ──► split_fallback_agent rewrites draft → /tmp → driver cp → 3
             4 booping plan check {plan-dir}
                 exit 1 ──► fix the milestone in draft.md → 3   (≤ 3 rounds, then findings go to present)
```

- `booping-python/src/booping/plan/split.py` (new) — pure: draft text → `Cut` (plan lines, overview lines, milestones with title/slug/sp/depends_on/sections, groups, flags, demoted-heading count). Ported from `heading_cut.py` (detection, owners, fields) and `cut.py` (section collection, `demote`, `block`); no line-map JSON, no `.meta/`.
- `booping-python/src/booping/plan/check.py` (new) — pure: milestone file text → findings.
- `booping-python/src/booping/commands/plan.py` (new) — the `plan` group, `split` and `check` verbs, mirroring `commands/items.py`; writes through the scaffold machinery in `commands/scaffold.py` (`_plan`/`_apply`, or a small public helper extracted from them) and `context/scaffold.py:load`; table rows through `booping/query.py`.
- `booping-python/src/booping/cli.py` — registers `plan_cmd.add_parser(sub)`.
- `src/config.yaml` — `core.groom_playbook.split.sections`, `core.groom_playbook.split_fallback_agent`.
- `playbooks/groom/` — `playbook.yaml` graph and edge prose, `draft-plan/opus-5.md` rewritten, `research-codebase/` and `research-web/` deleted; `playbooks/_partials/milestone_contract.md` deleted, `plan_templates.md` trimmed.
- Develop, `refresh-milestone-table`, `budget.py`, `pi-developer`, `booping-developer`, `develop-pi`: untouched — they read the same `index.md` + `milestones/M{nn}-{kebab}/M{nn}-{kebab}.md`.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [Draft parser and cut](milestones/M01-draft-parser-and-cut/M01-draft-parser-and-cut.md) | 4 | done |
| 02 | [booping plan split command](milestones/M02-plan-split-command/M02-plan-split-command.md) | 4 | done |
| 03 | [plan split e2e cases on benchmark plans](milestones/M03-plan-split-e2e-cases/M03-plan-split-e2e-cases.md) | 3 | done |
| 04 | [booping plan check — the milestone contract as code](milestones/M04-plan-check-command/M04-plan-check-command.md) | 4 | done |
| 05 | [Groom rewritten around one drafting step](milestones/M05-groom-one-drafting-step/M05-groom-one-drafting-step.md) | 3 | done |
| 06 | [Groom partials, present check and snapshot](milestones/M06-groom-partials-present-and-snapshot/M06-groom-partials-present-and-snapshot.md) | 2 | done |
| 07 | [Plan templates trimmed to the one-file format](milestones/M07-plan-templates-trimmed/M07-plan-templates-trimmed.md) | 3 | done |
| 08 | [Docs for one-pass groom and the plan commands](milestones/M08-docs/M08-docs.md) | 3 | done |

## Implementation Order

```
M01 ─► M02 ─► M03
         └──► M04 ─► M05 ─► M06 ─► M07 ─► M08
```

M03 (e2e for split) and M04 (check) both need M02 and may run in parallel; M05 needs both commands, M06 the step M05 rewrote (and accepts the snapshot once groom's renders are final), M07 the format M05 fixes, M08 the shipped surface.

## I/O contract

- **`booping plan split DRAFT [--out DIR] [--replace]`** — `DRAFT` the one-file plan; `--out` the plan directory to write (default: `DRAFT`'s directory); `--replace` removes existing milestone directories matching `core.plans.milestones.glob` under `DIR` before writing.
  - **stdin**: not read.
  - **stdout**: one line per milestone `M{nn}-{kebab} sp={n|null} sections=tasks:{lines},dod:{lines},references:{lines},verify:{lines}`, then one `group G{k}: M{nn}, … ({sum} SP)` line per group, then `demoted: {n}` when headings were demoted.
  - **stderr**: one `flag: {text}` line per flag; `error: {message}` on failure.
  - **Writes**: `DIR/milestones/M{nn}-{kebab}/M{nn}-{kebab}.md` per milestone; `DIR/index.md` — existing frontmatter kept (else the draft's own leading frontmatter, else none), `sp:` restamped when the key exists, body = the draft's plan lines in order with the generated `## Milestones` table and `## Groups` table where the draft's overview stood.
  - **Exit codes**: `0` written, no flags; `1` usage or config error; `2` refused (milestone files exist without `--replace`) or a write failed; `3` no milestone heading found — nothing written; `4` written, with flags.
- **`booping plan check PLAN_DIR`** — checks every milestone file under `PLAN_DIR` matching `core.plans.milestones.glob`.
  - **stdout**: one `{milestone dir}: {check}: {finding}` line per finding, `check` ∈ `verify`, `files`, `dod`, `sp`; nothing when clean.
  - **Exit codes**: `0` clean; `1` findings; `2` `PLAN_DIR` missing or holding no milestone file.

## Key Files Reference

| File | Role |
|------|------|
| `~/Dev/@A/booping-benchmarks/groom/split/heading_cut.py`, `cut.py`, `check.py` | prototype being ported (read-only, outside the repo) |
| `~/Dev/@A/booping-benchmarks/groom/variants/common.md`, `V3a-stages-no-review.md`, `V2-template.md` | the winning prompt, basis of draft-plan's body |
| `~/Dev/@A/booping-benchmarks/groom/ablation/report.md`, `rules.yaml` | the 16 cut rules with their text |
| `booping-python/src/booping/commands/items.py` | shape of a verb group |
| `booping-python/src/booping/commands/scaffold.py`, `context/scaffold.py` | scaffold render and write path split reuses |
| `playbooks/develop/_scripts/refresh-milestone-table` | the table format split must match |
| `playbooks/develop/provision/base.md` | develop's grouping rule split mirrors |
| `src/config.yaml` (`core.groom_playbook`, `core.sprint`, `core.plans`) | keys read and added |

## Final Verification

- [ ] `just ci` green (lint, typecheck, pytest, snapshots, mdcheck, specs-check, e2e).
- [ ] `bin/booping plan split --help` and `bin/booping plan check --help` describe the I/O contract above.
- [ ] Happy path: an e2e case splits a benchmark plan with exit 0; failure paths: exit 3 on a headingless draft, exit 4 with a `flag:` line on a draft missing `sp`, exit 2 on existing milestones without `--replace`, `plan check` exit 1 with a finding line.
- [ ] `bin/booping render-playbook groom` shows the graph `intake → draft-plan → cross-review → present` and no STOP notice.
- [ ] `just snapshots` clean after the accepted groom report; `develop-defaults.md` beside this plan lists the accepted report and why.

## Out of scope

- Renaming the milestone file to `milestones/M{nn}-*/index.md` — its own change with a migration (adr/0031).
- A light path for small, already-decided requests (idea/0003).
- Develop reading `## Groups` from `index.md` instead of packing its own groups.
- Migrating user-authored plan templates in project vaults — the draft format lives in the step body, so their old milestone section is overridden, not broken.
- Promptfoo eval suites for the new draft-plan body — groom carries none today.

## CLAUDE.md impact

| Section | Change | Owning task |
|---------|--------|-------------|
| `## Commands` — the `bin/booping <subcommand>` list | add `plan` (`split`, `check`) | M08 task 8.3 |
| `## Config` — `core.groom_playbook` is not listed today | no change — the new keys are documented in `documentation/project_config.md` | — |
