---
id: "09"
title: "CLAUDE.md, internal docs and specs records drop lessons"
sp: 4
status: done
plan: "vault/plans/202610150110_lessons-migration-rule-only-injection/index.md"
---

# M09: CLAUDE.md, internal docs and specs records drop lessons

`CLAUDE.md`, the plugin-internal docs and booping's own specs records describe rules as the one carrier: lessons appear only as the history migration 004 closed.

**Scope**: `CLAUDE.md` — `## Rendering pipeline` ("config merge, vault, rules, playbooks"), `## Playbooks` (delete the **Lessons** bullet; the **Rules** bullet loses "right before `## Lessons`" / "wherever lessons inject" and names its surfaces itself), `## Vault` (drop `_lessons/ (targeted)`), `## Principles` agent wiring ("a targeted rule (`agent:{id}`, `skill:{name}`)"); `## Lifecycle` and `## Commands` unchanged unless they name lessons. `docs/development_quality_checks.md:9` — a targeted rule, not a lesson. `docs/how_to_initialize_project.md:23` — the example list drops `lessons/`. `docs/plan_templates/claude_skill.md` — Final Verification "Targeted rules (`skill:{name}`, `agent:{id}`) still inline"; hygiene items name rules / the project specs tier, not `_lessons/` or "lessons". `vault/_playbooks/docs/targeting/opus-5.md:70` — the `documentation/vault.md` row no longer describes `_lessons/`. Specs records under `vault/specs/`: `story/0004-targeted-lessons.md` rewritten as the targeted-rules story and renamed `0004-targeted-rules.md` with every link to it repointed; `reference/0002-glossary.md` drops the `_lessons/` and "Targeted lesson" entries for a "Targeted rule" one; `rule/0018` names the project specs tier and `CLAUDE.md` as learn's two destinations, no "today `_lessons/`"; `rule/0020` drops "today the record is a targeted lesson"; `adr/0001` Consequences — `_lessons/` was converted and removed by migration 004; `vault/specs/README.md:19-20` — the deprecation note goes; `idea/0002` `[clarify]` proposal counts rules in `vault/specs/rule/` instead of `vault/_lessons/`. Every edited record's `updated_at` → the run date. Out of scope: `docs/retrospective_template.md`, `docs/retro_summary_format.md` — the legacy cross-check, parked (C3).

Tests: `just specs-check` is the record check; links resolve.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 9.1 | `CLAUDE.md` and the internal docs. | `CLAUDE.md`, `docs/development_quality_checks.md`, `docs/how_to_initialize_project.md`, `docs/plan_templates/claude_skill.md`, `vault/_playbooks/docs/targeting/opus-5.md` | 2 | done |
| 9.2 | Specs records, including the story rename and its inbound links. | `vault/specs/story/0004-targeted-lessons.md` → `vault/specs/story/0004-targeted-rules.md`, `vault/specs/reference/0002-glossary.md`, `vault/specs/rule/0018-project-specifics-stay-out-of-core.md`, `vault/specs/rule/0020-agent-shaping-is-targeted.md`, `vault/specs/adr/0001-specs-tiers.md`, `vault/specs/README.md`, `vault/specs/idea/0002-learn-prefers-guidance-over-validators.md` | 2 | done |

## Definition of Done

### Task 9.1

- [x] `rg -n -i '_lessons|targeted lesson|## Lessons|no-lessons' CLAUDE.md docs vault/_playbooks` prints only `docs/retrospective_template.md` / `docs/retro_summary_format.md` lines, if any.
- [x] `CLAUDE.md`'s Rules bullet still links `documentation/playbook.md#rules`.

### Task 9.2

- [x] `rg -n 'targeted-lessons' . --glob '!vault/plans/**' --glob '!vault/retrospectives/**' --glob '!vault/codereviews/**'` prints nothing.
- [x] `rg -n -i 'lesson' vault/specs` hits only rule/0001's own subject ("a lesson is a rule"), migration-004 history lines, and plain-English retro wording.
- [x] No record's `targets:` changed.

Return: the list of changed files, nothing else.

## References

- `vault/specs/story/0019-learn.md` — story record shape.
- `src/specs/README.md` — record format and the `updated_at` convention.

## Verify

`just specs-check`
