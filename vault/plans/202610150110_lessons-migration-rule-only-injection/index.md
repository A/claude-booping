---
title: "Lessons become rules — migration 004 and rule-only injection"
type: "feature"
status: in-progress
sp: 35
related_to: null
created: 2026-10-15 01:10
planned: null
started: 2026-10-15 01:31
completed: null
code_reviews: []
sessions:
- bdaa9426-d742-41ed-aff2-33570ac9d2e5
- 0d329ff6-0279-4360-80b1-d3bcef7dd462
retro: null
summary: Migration 004 turns lessons into rules; render surfaces inject rules 
  only; --no-lessons and the _lessons scaffold go
commit: 632d7e11fbd2d014fa7c6bfb07b29fc2aa9f21b0
tracker_provider: null
tracker_request: null
tracker_issue: null
return_to: null
agents:
  research-codebase: ad7f4b43df8f31faf
  cross-review: acdf9a7240042e122
reviewed_at: 2026-10-15 01:30
---

# Lessons become rules — migration 004 and rule-only injection

## Context

After plan 202610142150, `learn` writes rule records, but every render surface still injects two carriers of learnt guidance: targeted lesson files from `{home_dir}/_lessons/` and `{vault}/_lessons/` (full bodies under `## Lessons`) and targeted rules from the three specs tiers (brief + link under `## Rules`). Booping's own vault holds a rule duplicate of every lesson, so its renders inject the same guidance twice. After this plan: rules are the one targeted carrier — `render-playbook`, agent and skill bodies and learn's target space inject `## Rules` only, `--no-lessons` is gone, a new vault gets no `_lessons/`, and migration 004 (through `/playbook migrate`, which every render surface already demands of a vault behind the watermark) converts any remaining lessons into rule records or drops them as duplicates. Booping's own vault is migrated: its eleven lessons drop as duplicates. The legacy untargeted `{vault}/lessons/` set read by the retro, code-review and groom cross-checks is parked (C3). Autonomous-run defaults: `clarifications.md` C1–C12.

## Decisions

- **Split** (C1, C3): targeted lessons here; the legacy `{vault}/lessons/` cross-check set parked — this slice ships alone at 35 SP.
- **`--no-lessons`**: removed, not aliased (202610142150 C2).
- **Target parsing** (C10): `specs/targets.py` — `Target`, `TargetRejection`, `parse_target`; "a target", not "a lesson target", in user-facing wording.
- **Notices** (C11): the lesson notices retire; the migration gate stands in for them.
- **Migration 004** (C4–C7): global pass then project pass; duplicates (accepted or retired) dropped; a same-tier duplicate gains the lesson's targets, another tier's never is edited — booping's rule/0013 and rule/0015 stay untargeted ([rule/0018](../../specs/rule/0018-project-specifics-stay-out-of-core.md)); references rewritten by an embedded script ([rule/0025](../../specs/rule/0025-mechanics-run-as-code.md)); report lines locked in C7 ([rule/0010](../../specs/rule/0010-output-content-locked-in-grooming.md)).
- **Testing the migration** (C8): a committed fixture and `check.sh` beside it, applied by the worker; `{home_dir}` never touched (C2).
- **Own vault** (C9): migrated in the milestone that ships 004 — the watermark gate leaves no gap between them.
- **Snapshots** (C12): drift accepted only in `learn`, `develop`, `setup` reports, under the owner's standing policy for this feature.

## Architecture

```
specs/targets.py ── parse_target ──┬── specs/rules.py ── load_targeted_rules (core → global → project, first tier wins per path)
                                   ├── specs/check.py (targets error)
                                   └── commands/render_playbook.py ── ## Rules (composed, --step, inline)
_targeted_rules.j2 ── agent / skill bodies        target_space.md ── learn
context/lesson.py ── Lesson.load_all ── {vault}/lessons/ ── _lessons.j2 ── retro / code-review / cross-review   (parked)

/playbook migrate ── apply-migration ── migrations/004_lessons_to_rules/migration.md
    global pass: {home_dir}/_lessons/ ── specs init --tier global ── judge vs core/global rules ── convert | drop ── rewrite refs ── rm
    project pass: {vault}/_lessons/  ── specs init --tier project ── judge vs core/global/project ── convert | drop ── rewrite refs ── rm
```

M01 first (every later code milestone imports the new module); M02–M03 take template consumers off `targeted_lessons` before M04 removes the field; M07 ships 004 and migrates booping's vault in one milestone; M08–M09 last, describing the end state.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [Target parsing lives in specs/targets.py](milestones/M01-target-parsing-in-specs/M01-target-parsing-in-specs.md) | 3 | done |
| 02 | [Agent, skill and step bodies inject rules only](milestones/M02-bodies-drop-lesson-partials/M02-bodies-drop-lesson-partials.md) | 3 | done |
| 03 | [Learn stops reading and staging _lessons](milestones/M03-learn-without-lessons/M03-learn-without-lessons.md) | 3 | pending |
| 04 | [render-playbook and the context load rules only; --no-lessons removed](milestones/M04-render-playbook-rules-only/M04-render-playbook-rules-only.md) | 5 | pending |
| 05 | [One directory as core and project tier injects each rule once](milestones/M05-shared-tier-directory-case/M05-shared-tier-directory-case.md) | 2 | pending |
| 06 | [The vault scaffold drops _lessons](milestones/M06-scaffold-drops-lessons/M06-scaffold-drops-lessons.md) | 2 | pending |
| 07 | [Migration 004 converts lessons into rules; booping's vault migrated](milestones/M07-migration-004/M07-migration-004.md) | 9 | pending |
| 08 | [Public docs describe rules as the one carrier](milestones/M08-public-docs/M08-public-docs.md) | 4 | pending |
| 09 | [CLAUDE.md, internal docs and specs records drop lessons](milestones/M09-internal-docs-and-records/M09-internal-docs-and-records.md) | 4 | pending |

## Final Verification

- [ ] `just ci` green.
- [ ] `just snapshots` drift limited to `playbooks/{learn,develop,setup}/_reports/output.md`, every hunk a change M02, M03 or M06 describes; accepted under the run's snapshot policy and listed in `develop-defaults.md`.
- [ ] `bin/booping render-playbook groom` and `bin/booping render src/templates/agents/booping-researcher.md.j2` reviewed: `## Rules` present, no `## Lessons`, no lesson notice, no `{{placeholder}}` leaks.
- [ ] Targeted rules (`skill:playbook`, `agent:{id}`) still inline into rendered bodies.
- [ ] `vault/_lessons/` gone, `.booping` at `latest_migration: 4`, `{home_dir}` untouched.
- [ ] `rg -n -i '_lessons|targeted lesson|no-lessons' --glob '!vault/plans/**' --glob '!vault/retrospectives/**' --glob '!vault/codereviews/**' --glob '!playbooks/*/_specs/**'` — every hit is migration history (`migrations/`, migration-004 lines in records and docs), the M04 regression case's fixture, or a parked cross-check surface.

## Out of scope

- **Parked sibling — legacy cross-check set** (stub, groom in its own run): the untargeted `{vault}/lessons/` set (`Context.lessons`, `Lesson.load_all`, `_lessons.j2`) read by retro `prepare` (with `_plan_lesson_check.j2`, `_session_log_extraction.j2`), code-review `review` and groom `cross-review` — replaced by a digest of the accepted rules targeting the reviewed playbooks; migration 005 converting `{vault}/lessons/` into rule records (targets judged per file, as migration 002 Part 2 did); `context/lesson.py` and `debug-context`'s `lessons` key deleted; `documentation/retro.md`, `docs/retrospective_template.md`, `docs/retro_summary_format.md`, code-review's "lesson compliance" wording rewritten. ≈ 12 SP.
- The three global rules anton:rule/0001–0003 whose `sources` name booping's removed lessons — the owner's `{home_dir}`, fixed by hand (C5).
- `migrate`'s worked-example receipts naming `_lessons/` — illustrations of a past migration (C12).
- Running the `regress` eval tier.

## CLAUDE.md impact

`## Rendering pipeline`, `## Playbooks` (Lessons bullet deleted, Rules bullet standalone), `## Vault` (`_lessons/` dropped), `## Principles` (agent wiring by targeted rule) — M09 task 9.1.
