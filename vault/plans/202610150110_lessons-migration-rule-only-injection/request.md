# Request

> Request — lessons migration and rule-only injection (the parked sibling named in plan 202610142150_lessons-become-rules, section "Out of scope" — read it, it is the brief): migration 004 turning `{vault}/_lessons/` and `{home_dir}/_lessons/` into rule records (calls `booping specs init`; lessons that duplicate an existing rule are dropped; rule `sources`/links pointing at removed lessons rewritten), lesson injection removed from every render surface, `--no-lessons` removed (that plan's C2), the shared target parsing moved out of `context/lesson.py`, an e2e case for core and project tiers on one directory, the vault scaffold's `_lessons:` entry dropped, booping's own vault migrated (all eleven lessons have a rule duplicate in the core or global tier; rule/0013 and rule/0015 are booping-specific and must not gain core targets — rule/0018), and the lesson-injection docs (documentation/playbook.md, CLAUDE.md `## Playbooks`/`## Vault`) rewritten. Lesson 0012 (Plannotator) maps to the retired rule/0012 and is dropped, not migrated into an accepted rule. Do NOT run the migration on `<home_dir>` (the owner's notes repo) — only ship it and test it on fixtures; booping's own vault is migrated in this repo.
>
> AUTONOMOUS RUN. The owner is not available: do not ask questions and do not wait at review gates — auto-confirm them yourself; settle unclear points with a sensible default and record every default in the plan's clarifications.md (groom) or a develop-defaults.md beside the plan (develop). You run in the worktree /home/anton/Dev/@A/claude-booping-specs on branch feat/specs: never switch branches, never push, stage by path (never git add -A). Read vault/specs (value/, rule/, adr/0001) and src/specs/README.md before deciding anything; a choice that contradicts a value or rule is wrong. Snapshot policy for this run (owner's standing permission for this feature, 2026-10-14): when `just snapshots` drifts, you may run `just snapshots-accept` only if every drifted hunk is a change the plan describes; list each accepted report and why in the run's defaults file. Any other drift: stop and report. A red `just ci` is fixed by a worker, never by weakening a check. If a groom splits the request, groom only the first plan and list the rest as parked stubs. End at ready-for-dev.

## Task type

`feature` — users see the change: `## Lessons` disappears from every rendered body, `--no-lessons` is gone from `render-playbook`, a new migration 004 meets every vault, and a fresh vault no longer gets `_lessons/`. Not `refactoring`: rendered output and the CLI surface change observably. Not `bug`: nothing diverges from a stated expectation — adr/0001 and rule/0001 schedule this step, and plan 202610142150 parked it.

## Problem

After plan 202610142150, `learn` writes rule records, but render surfaces still inject two carriers: lesson files from `{home_dir}/_lessons/` and `{vault}/_lessons/` (full bodies under `## Lessons`) and targeted rules from the three specs tiers (brief + link under `## Rules`). Booping's own vault carries a rule duplicate of every lesson, so its renders inject the same guidance twice. What must change: a shipped migration converts any remaining lessons into project/global rule records (dropping duplicates, rewriting references to removed lessons), every render surface injects rules only, `--no-lessons` and the vault scaffold's `_lessons:` go, target parsing leaves `context/lesson.py`, booping's own vault is migrated, and the docs stop describing lessons.

## Clarifications and Decisions

Autonomous run — every default is recorded in `clarifications.md` with its reasoning.

- Goal after this plan ships: rules are the one carrier of learnt guidance — no render surface reads `_lessons/`, any vault that still holds lessons is converted by `/playbook migrate`, and booping's own vault holds none.
- Scope is the parked stub as written; no split (C1). `--no-lessons` removed, not aliased (carried over from 202610142150 C2).
- `<home_dir>` is never migrated by this run; the global half of migration 004 is exercised on fixtures only (C2).
