# Framing brief

## Request

> Routing matrix row "Skill extra instructions" is outdated. Take lesson-target-toc, rename it as learn-targets, add a lesson targets section and a global section (never update global CLAUDE.md; if a reason of behavior comes from the project CLAUDE.md it must be fixed there). Decisions: 1. `_extra_instructions.j2` — it might be alive, but it will be dropped within this release. 2. Delete skill code-review. 3. extra-instructions — drop, we remove it. 4. `skill:playbook` lesson target — ok. 5. Don't run evals.

## Task type

`feature` — the change set alters user-visible capability: the `/code-review` skill is removed, the `_booping/skill_*` / `agent_*` extension channel is retired, and a new `skill:playbook` lesson target form is added to the engine. `bug` is ruled out — nothing diverges from expected behavior today. `refactoring` is ruled out — behavior visibly changes (a shipped skill disappears, a config-facing channel dies, a new target syntax appears), failing the no-user-visible-change test.

## Problem

Today learn routes accepted candidates to four destinations via a routing matrix (`playbooks/learn/_partials/_learn_targets.j2`): lessons, skill extra instructions (`_booping/skill_{skill}.md`), agent extra instructions (`_booping/agent_{id}.md`), and the repo `CLAUDE.md`. Two of the four are redundant or dying: agent extras duplicate what `agent:{id}` lessons already deliver, and skill extras serve a skill surface that shrinks to `/playbook` alone once the `/code-review` skill (superseded by the `code-review` playbook) is deleted. The `_extra_instructions.j2` channel itself is to be removed this release. Lessons cannot yet target the `/playbook` skill (the driver), so a new `skill:playbook` target form is needed in `lesson.parse_target` plus an injection point in the skill body. The learn target surface consolidates into one partial — `lesson_target_toc.md` renamed to the learn-targets doc — carrying the lesson target forms, the repo-CLAUDE.md case, and the global rule (never write `~/.claude/CLAUDE.md`; a behavior caused by the project `CLAUDE.md` is fixed there).

## Clarifications and Decisions

- `_extra_instructions.j2` channel: dropped entirely this release (template, all four `tools.render` call sites, docs).
- `/code-review` skill: deleted (`skills/code-review/`, `src/files/skills/code-review/`, `src/templates/skills/code-review.md.j2`); the `code-review` playbook stays.
- `skill:playbook` lesson target: approved; prefixed syntax matching `agent:{id}` convention.
- Evals: suites are not run in this sprint; prompt/fixture text is still kept consistent.
- Parser form: generic `skill:{name}`, not a pinned literal.
- `core.code_review_playbook.queries.review_candidates`: dropped with the skill; `scope_candidates` stays.
- Migration 004: converts vault `_booping/skill_*.md` / `agent_booping-*.md` extension files into `_lessons/` files with proper `targets:`.
- Invocation log moves from `{vault}/_booping/.booping.log` to `{vault}/.booping.log`; the `_booping/` dir leaves the scaffold tree and old dirs are deleted manually (no migration for the dir itself).
- Post-implementation prose-shape reshape expected: yes — encode as the plan's final milestone (lesson 0009).
