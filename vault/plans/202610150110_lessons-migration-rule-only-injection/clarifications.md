# Clarifications

Autonomous groom run on 2026-10-15: the owner was unavailable, so every question below was settled by the run with the default marked "default applied". Each stays reviewable and amendable before develop starts ([value/0009](../../specs/value/0009-adjustable-control.md), [rule/0002](../../specs/rule/0002-unknown-is-marked.md)).

## C1 — split — answered

**Asked:** 2026-10-15 — intake

**Question:** The parked stub was estimated at ≈ 25 SP. Split again?

**Options:**

- One plan, as the stub was parked (default applied)
- Split migration 004 from rule-only injection

**Answer:** One plan — default applied, unless the estimate passes the 35 SP threshold at draft. Removing lesson injection before a migration exists strands any vault still holding lessons (its guidance would inject nowhere); shipping the migration while lessons still inject leaves two carriers. The two halves ship together or the intermediate state is broken.

## C2 — the owner's `{home_dir}` — answered

**Asked:** 2026-10-15 — intake

**Question:** Migration 004 converts `{home_dir}/_lessons/` too. Is it run on this machine's `{home_dir}`?

**Answer:** No — the request forbids it. The global half is shipped and exercised on fixtures only. On this machine `{home_dir}/_lessons/` does not exist (checked 2026-10-15) and the global tier already holds anton:rule/0001–0004, so a later `/playbook migrate` from another vault finds nothing global to convert.

## C3 — split at the legacy `{vault}/lessons/` seam — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** Research found a third lesson carrier the stub did not name: the untargeted legacy `{vault}/lessons/` directory (`Context.lessons`, `Lesson.load_all`), rendered by `_lessons.j2` into the cross-checks of retro `prepare`, code-review `review` and groom `cross-review`. It is live — 13 of the owner's vaults carry one (checked 2026-10-15). Folding its retirement in puts the plan at ≈ 41 SP, past the 35 SP threshold. Where is the seam?

**Options:**

- This plan: targeted lessons (`{vault}/_lessons/`, `{home_dir}/_lessons/`) — migration 004, rule-only injection, `--no-lessons`, target parsing, scaffold, booping's own vault, docs. Parked: the legacy cross-check set — a rules digest replacing `_lessons.j2` in the three cross-checks, migration 005 converting `{vault}/lessons/`, `Context.lessons` and its docs (default applied)
- One plan over the threshold

**Answer:** First option — default applied. This plan ships alone: the legacy cross-check keeps reading `{vault}/lessons/` until the parked plan, and nothing this plan removes is read by it, so every doc this plan leaves describing the cross-check stays true ([rule/0007](../../specs/rule/0007-stale-references-cleaned-in-sprint.md) holds per sprint). The parked plan is independent of this one but reuses its target module and its migration as the shape for 005. Parked stub: `index.md` `## Out of scope`. The request's "every render surface" is met for targeted lessons; the cross-check set is named as the remaining carrier there.

## C4 — what counts as a duplicate, and what is never edited — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** Migration 004 drops a lesson that duplicates an existing rule. Which rules count, and what happens to a lesson's targets the duplicate lacks?

**Answer:** Default applied:

- A duplicate is an accepted **or retired** rule in the core, global or project tier stating the same constraint — the migrating agent judges substance, not wording. A retired duplicate drops the lesson too: the retirement stands, the lesson is not revived (lesson 0012 → retired rule/0012, per the request).
- A duplicate in the **same tier** the lesson converts into, lacking some of the lesson's targets, gains them (targets merged; a `brief` written when it had none; `updated_at` bumped) — the lesson's reach survives.
- A duplicate in **another tier** — core for any lesson, global for a project lesson — is never edited. The targets it lacks are listed in the migration report as not carried over. Where core and project tiers are one directory (booping's own repo) the record counts as core, the same first-tier-wins resolution rule injection uses (`specs/rules.py`). This is what keeps rule/0013 and rule/0015 free of core targets ([rule/0018](../../specs/rule/0018-project-specifics-stay-out-of-core.md)): booping's lessons 0013 and 0015 are dropped and their injection into `develop` / `code-review` ends. [clarify] The owner may want those two re-homed in a booping-only scope later; nothing in this plan provides one.
- Not a duplicate → converted: a new rule record in the lesson's tier, shape per plan 202610142150 C5 (`created_by: claude`, `status: accepted`, `targets` = the lesson's, a written `brief`, `## Rule` + `## Follows from`; `sources` = the lesson's `retro:` when it resolves against the tier anchor, else omitted). An untargeted lesson converts to a rule with neither `targets` nor `brief`.

## C5 — rewriting references to removed lessons — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** Rules carry `sources:` entries and body links pointing at the lesson files the migration deletes. Rewritten how?

**Answer:** Default applied, by an embedded script (deterministic, [rule/0025](../../specs/rule/0025-mechanics-run-as-code.md)), over every record of the tier root the pass writes:

- A `sources:` entry resolving (against the tier anchor) to a removed lesson → replaced by that lesson's `retro:` path re-expressed against the same anchor, when it has one, it exists, and it is not already listed; otherwise dropped. An emptied list drops the key.
- A relative body link resolving to a removed lesson → re-pointed at the lesson's retro when it has one, else replaced by the plain text `` `_lessons/{file}` (removed by migration 004) `` — the surrounding sentence stays as written.
- Records of **another** tier referencing a removed lesson are not edited; each is listed in the report as dangling. Known instance: anton:rule/0001–0003 cite `claude-booping/vault/_lessons/…`, resolved through `{home_dir}/claude-booping → ~/Dev/@A/claude-booping` (the main checkout); they dangle once this branch merges. [clarify] The owner fixes those three in `{home_dir}` by hand — this run never touches it (C2).

## C6 — migration order and idempotence — answered

**Asked:** 2026-10-15 — draft-plan

**Answer:** Default applied. Global pass first (`{home_dir}/_lessons/` → `{home_dir}/_specs/rule/`, `booping specs init --tier global` run only when a lesson file exists), then the project pass (`booping specs init --tier project`), so a project lesson can be judged against a rule the global pass just wrote. A pass with no lesson files does nothing and reports so; re-running on a migrated vault changes nothing. A second vault migrating later finds the global pass already done. An emptied `_lessons/` directory is removed. Lesson files are deleted only after their rule exists or their duplicate is named.

## C7 — migration report — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** [rule/0010](../../specs/rule/0010-output-content-locked-in-grooming.md): the exact lines the migration reports?

**Answer:** Default applied. One line per action, grouped under `global:` then `project:`, paths relative to the tier anchor:

```
dropped {lesson path} — duplicate of {ref}
converted {lesson path} → {rule path}
merged targets {targets} into {ref} from {lesson path}
not carried {lesson path} targets {targets} — {ref} is {tier}, never edited
rewrote {record path} — {sources|link} {lesson file} → {retro path|removed}
dangling {record path} → {lesson path} ({tier}, not edited)
nothing to convert
```

`{ref}` is namespaced across tiers (`booping:rule/0013`, `anton:rule/0001`), bare within the pass's tier. The `apply-migration` step wraps this in its own receipt as it does for every migration.

## C8 — testing the migration — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** Migrations have no automated test today, and the owner's `{home_dir}` is off limits. How is 004 tested?

**Answer:** Default applied: a committed fixture beside the migration — `migrations/004_lessons_to_rules/_fixtures/` with a `home/` (global config, `_lessons/` with one lesson duplicating a global rule and one new) and a `repo/` (marker at 3, in-repo vault with `_lessons/` covering: duplicate of a core rule lacking the lesson's targets, duplicate of a retired rule, duplicate of a project rule lacking a target, a new lesson with a retro, a new untargeted lesson without one; plus a project rule whose `sources` and body link name a lesson) — and a `check.sh {copy}` asserting the migrated end state (no lesson file left, the expected rule files and frontmatter, `booping specs check` clean on both fixture tiers, no reference to a removed lesson in the project tier). The worker copies the fixture to `/tmp`, applies `migration.md` to the copy as the migrating agent would, and runs `check.sh`. Not wired into `just ci`: applying a migration is an agent's work. The fixture ships with the plugin; the migrate query reads `migrations/*/migration.md` only, so it is never mistaken for a migration.

## C9 — who migrates booping's own vault — answered

**Asked:** 2026-10-15 — draft-plan

**Answer:** Default applied: the worker of the migration milestone, in the same milestone that ships migration 004. Once `migrations/004_*` exists every render in this repo STOPs until the marker reads 4, the develop runner's own step fetches included, so shipping and applying cannot straddle a milestone boundary. Booping's `vault/specs/` is the core tier — shipped plugin content — and the vault is inside the repo; plan 202610142150 set the precedent of a worker editing it. The hermetic fixture vault's marker (`playbooks/_fixtures/vault/.booping`) moves to 4 in the same task. Expected outcome, from the request: all eleven lessons dropped as duplicates, none converted.

## C10 — target parsing's new home — answered

**Asked:** 2026-10-15 — draft-plan

**Answer:** Default applied: `booping-python/src/booping/specs/targets.py`, names `Target`, `TargetRejection`, `parse_target` (`LessonTarget` renamed — the classifier has no lesson in it). Its importers are `specs/rules.py`, `specs/check.py`, `commands/render_playbook.py`. User-facing wording follows: `src/specs/README.md` and the `specs check` `targets` message say "a target", not "a lesson target".

## C11 — notices that retire with lessons — answered

**Asked:** 2026-10-15 — draft-plan

**Answer:** Default applied: the untargeted-lesson, unknown-step-lesson and legacy playbook-local `_lessons/` notices go with lesson injection, and `legacy_lesson_dirs` with them. A vault still holding `_lessons/` is not silently ignored: the migration gate STOPs every render until 004 is applied, and 004 removes the directory.

## C12 — snapshot drift this plan accepts — answered

**Asked:** 2026-10-15 — draft-plan

**Answer:** Under the owner's standing snapshot policy for this feature (request, 2026-10-14; it overrides [rule/0013](../../specs/rule/0013-snapshot-baselines-accepted-by-user.md) for this run only): expected drift is limited to `playbooks/{learn,develop,setup}/_reports/output.md`, each hunk a change a milestone names. `migrate`'s worked-example receipts (`_lessons/0003_gates.md`) illustrate a past migration and are left as they are, so `migrate` must not drift. Any other drift stops the run.
