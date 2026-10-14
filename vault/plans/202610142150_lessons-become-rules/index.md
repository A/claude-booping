---
title: "Learn writes rules — specs init, learn on rule records, setup provisions tiers"
type: "feature"
status: ready-for-dev
sp: null
related_to: null
created: 2026-10-14 21:51
planned: null
started: null
completed: null
code_reviews: []
sessions:
- 9b11eed5-034e-486d-9c23-2799aaaad265
retro: null
summary: learn writes rule records in the project specs tier; booping specs init
  creates tiers; setup provisions tiers and namespace
commit: de5276323965a1166bb1d062ad86ab1d20881b62
tracker_provider: null
tracker_request: null
tracker_issue: null
return_to: null
agents:
  research-codebase: a3bf4d40f592c8d55
  cross-review: afec65a15af3fcf4f
reviewed_at: 2026-10-14 22:07
---

# Learn writes rules — specs init, learn on rule records, setup provisions tiers

## Context

`learn` writes lesson files into `{vault}/_lessons/`, while [rule/0001](../../specs/rule/0001-lessons-are-rules.md) and [adr/0001](../../specs/adr/0001-specs-tiers.md) say a learning is a rule record in a specs tier, injected as brief plus link. No surface creates a specs tier today, and the global tier's namespace is only ever `$USER` from code. After this plan: every learning `learn` writes is a rule record in the project tier (created on demand by a new `booping specs init`), its review table carries the rule's targets and brief, `setup` leaves a project with both tiers and the global namespace stored, and rule/0001 is injected into `learn` again. Existing lessons keep injecting until the parked migration plan converts them. Autonomous-run defaults: `clarifications.md` C1–C12.

## Decisions

- **Split** (C1): learn + setup + `specs init` first; the lessons migration and rule-only injection are parked — this slice ships alone, the parked one needs it.
- **Tier creation is code** (C3, C4): `booping specs init --tier {global|project}`, idempotent, prints the tier root; learn, setup and the parked migration call it ([rule/0025](../../specs/rule/0025-mechanics-run-as-code.md)).
- **Learnt rule shape** (C5): per `src/specs/README.md`, `created_by: claude`, no `reviewed`, `sources` only when the retro resolves from the repo root.
- **Tier reach** (C6): learn writes only the project tier; core/global coverage is `covered` and never written; a lesson duplicate is converted to a rule and the lesson deleted.
- **Commit** (C7): closing hook stages `_lessons` and `specs`.
- **Namespace** (C8): `core.specs.tiers.global.namespace` in the global config, asked once by setup.
- **`--no-lessons`** (C2, for the parked plan): removed, not aliased.
- **Review table** (C12): `#`, `Target`, `Type`, `Targets`, `Brief`, `Rule`, `Example`.

## Architecture

```
setup-booping ── namespace → global config ── specs init --tier global ──┐
setup-project ───────────────────────────── specs init --tier project ──┤→ tiers.py (root resolution)
learn/write ─── specs init --tier project → specs next rule → record ──┘
learn preamble ── target_space.md ── context.targeted_rules + targeted_lessons
learn/dedup-sweep ── specs ls --tier core|global|project --type rule + _lessons + CLAUDE.md
```

Milestones run in id order; M04 and M06 call the verb M01 adds. `tiers.py` stays the only place that knows where a tier lives; every playbook asks the CLI.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | booping specs init creates a tier | 6 | pending |
| 02 | Learn preamble and target space on rules | 4 | pending |
| 03 | Learn dedup sweep and review table over rules | 4 | pending |
| 04 | Learn writes rule records | 4 | pending |
| 05 | Learn eval suites on rules | 3 | pending |
| 06 | Setup provisions the specs tiers and namespace | 3 | pending |
| 07 | Docs for rule-writing learn, specs init and setup | 3 | pending |

## Final Verification

- [ ] `just ci` green.
- [ ] `just snapshots` drift limited to `playbooks/learn/_reports/output.md` and `playbooks/setup/_reports/output.md`, every hunk a change M02–M04 / M06 describe; accepted under the run's snapshot policy and listed in `develop-defaults.md`.
- [ ] `bin/booping render-playbook learn` reviewed: no `_lessons/` destination, rule/0001 under `## Rules`, no `{{placeholder}}` leaks.
- [ ] `bin/booping render-playbook setup` reviewed: both steps call `specs init`, the namespace question present.
- [ ] Targeted rules and lessons (`skill:playbook`, `agent:{id}`) still inline into rendered bodies.

## Out of scope

- **Parked sibling — lessons migration and rule-only injection** (stub, groom in its own run): migration 004 turning `{vault}/_lessons/` and `{home_dir}/_lessons/` into rule records (calls `specs init`; duplicates of existing rules dropped; rule `sources`/links pointing at removed lessons rewritten), lesson injection removed from every render surface, `--no-lessons` removed (C2), the shared target parsing moved out of `context/lesson.py`, an e2e case for core and project tiers on one directory, the vault scaffold's `_lessons:` entry dropped, booping's own vault migrated (all eleven lessons have a rule duplicate in the core or global tier; rule/0013 and rule/0015 are booping-specific and must not gain core targets — [rule/0018](../../specs/rule/0018-project-specifics-stay-out-of-core.md)), and the lesson-injection docs (`documentation/playbook.md`, CLAUDE.md `## Playbooks`/`## Vault`) rewritten. ≈ 25 SP.
- Running the `regress` eval tier (C10).
- An exported global tier (adr/0001 `[clarify]`).

## CLAUDE.md impact

`## Commands`: the `specs` verb list gains `init` (M01 task 1.3). Lessons bullets stay true until the parked plan.
