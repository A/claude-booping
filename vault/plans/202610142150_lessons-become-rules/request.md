# Request

> Request — lessons become rules (rule/0001, adr/0001):
> 1. A vault migration (next id after migrations/003) that turns every lesson in `{vault}/_lessons/` into a rule record in the project tier (`core.specs` project path; create the tier and its README pointer if missing): `targets` from the lesson's targets, `brief` = a one-or-two-line self-sufficient brief (src/specs/README.md), body with `## Rule` and `## Follows from` linking the lesson source; lessons that duplicate an existing rule are dropped in favour of the rule (the owner already accepted rule duplicates of booping's own lessons: compare vault/specs/rule/0006-0015 with vault/_lessons). The global tier's `<home_dir>/_lessons/` likewise into `<home_dir>/_specs/rule/`. Lesson files are removed by the migration after their rule exists (one commit, reversible by git).
> 2. Lesson injection is removed once no lessons remain: render surfaces inject only rules (`## Rules`); `--no-lessons` becomes an alias of `--no-rules` or is removed — choose per values, record it.
> 3. `learn` writes rules instead of lessons (its two destinations become: a rule record in the project tier, and the repo's CLAUDE.md); its review table and write step change accordingly; rule/0001 gets its `targets: [learn]` and brief back with the exception removed.
> 4. `setup` creates the project specs tier (path per core.specs; symlink from the vault when the vault is outside the repo, per adr/0001) and asks/stores the global namespace id (default `$USER`) in the global config.
> 5. Run the migration on this repo's own vault as part of the plan (booping's vault/_lessons → its records), and update CLAUDE.md, documentation/ and docs/ that mention lessons.
>
> AUTONOMOUS RUN. The owner is not available: do not ask questions and do not wait at review gates — auto-confirm them yourself; settle unclear points with a sensible default and record every default in the plan's clarifications.md (groom) or a develop-defaults.md beside the plan (develop). You run in the worktree /home/anton/Dev/@A/claude-booping-specs on branch feat/specs: never switch branches, never push, stage by path (never git add -A). Read vault/specs (value/, rule/, adr/0001) and src/specs/README.md before deciding anything; a choice that contradicts a value or rule is wrong. Snapshot policy for this run (owner's standing permission for this feature, 2026-10-14): when `just snapshots` drifts, you may run `just snapshots-accept` only if every drifted hunk is a change the plan describes; list each accepted report and why in the run's defaults file. Any other drift: stop and report. A red `just ci` is fixed by a worker, never by weakening a check. If a groom splits the request, groom only the first plan and list the rest as parked stubs. End at ready-for-dev.

## Task type

`feature` — the user-visible behaviour changes: what `learn` writes, what render surfaces inject, what `setup` creates, and a new migration every vault meets. Not `refactoring`: the injected surface (`## Lessons` disappears, rules take over) and the learn/setup outputs change observably. Not `bug`: nothing diverges from a stated expectation; adr/0001 and rule/0001 schedule this as the next step.

## Problem

Today a project keeps two parallel carriers of learnt guidance: lesson files in `{vault}/_lessons/` and `<home_dir>/_lessons/` (injected as full bodies under `## Lessons`) and rule records in the three `core.specs` tiers (injected as brief + link under `## Rules`). `learn` still writes lessons, so every new lesson widens the duplication; booping's own vault already carries a rule duplicate of every lesson, so its renders inject the same guidance twice. adr/0001 deprecates `_lessons/` and rule/0001 says a lesson is a rule — what must change: existing lessons become rule records (migration), injection reads rules only, `learn` writes rule records, `setup` provisions the project specs tier and the global namespace, and the docs stop describing lessons.

## Clarifications and Decisions

Autonomous run — every default below is recorded in `clarifications.md` with its reasoning.

- Split (C1): this plan — `learn` writes rule records, a `booping specs init` verb, `setup` provisions the global and project tiers and the global namespace, rule/0001 regains `targets: [learn]`, plus the docs of those. Parked: the lessons migration (004), rule-only injection and `--no-lessons` removal (C2), and booping's own vault migration.
- Goal after this plan ships: every learning `learn` writes is a rule record in the project tier; a fresh `setup` leaves a project with both specs tiers in place and the global namespace stored.
- Tier creation is one CLI verb, not prose in three playbooks (C3, C4); learn's rule shape, tier reach and commit (C5–C7); setup's namespace storage (C8); rule/0001's new brief (C9); evals smoke-only (C10); docs scoped to what this plan changes (C11).
