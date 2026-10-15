# Request

> Request — the vault `docs` playbook (`vault/_playbooks/docs/`, a project playbook of this repo) works on specs records instead of the deprecated `vault/docs/_specs/` set:
> - `roles` → reference record on the audience (vault/specs/reference/0001), `targets` → reference/0003 (documentation surfaces), glossary → reference/0002, `feature-index` → generated from story records (vault/specs/story/), not stored; `briefing` reads value records instead of writing index.md; `sync-specs` edits the records (marks [clarify]/[unknown] per rule/0002) instead of the old files; the `documented.md` ledger stays a run artefact in the vault (choose where, record it); the `reviewed_at` hook on `_specs/index.md` goes away or moves to a sensible artefact.
> - Then delete `vault/docs/_specs/` and remove the deprecation notes about it (vault/specs/README.md, adr/0001 consequences, CLAUDE.md, reference/0002, reference/0003). Its committed report and evals beside the steps follow the change.
>
> AUTONOMOUS RUN. The owner is not available: do not ask questions and do not wait at review gates — auto-confirm them yourself; settle unclear points with a sensible default and record every default in the plan's clarifications.md (groom) or a develop-defaults.md beside the plan (develop). You run in the worktree /home/anton/Dev/@A/claude-booping-specs on branch feat/specs: never switch branches, never push, stage by path (never git add -A). Read vault/specs (value/, rule/, adr/0001) and src/specs/README.md before deciding anything; a choice that contradicts a value or rule is wrong. Snapshot policy for this run (owner's standing permission for this feature, 2026-10-14): when `just snapshots` drifts, you may run `just snapshots-accept` only if every drifted hunk is a change the plan describes; list each accepted report and why in the run's defaults file. Any other drift: stop and report. A red `just ci` is fixed by a worker, never by weakening a check. If a groom splits the request, groom only the first plan and list the rest as parked stubs. End at ready-for-dev.

## Task type

`refactoring` — what the docs playbook produces (documentation surfaces matched to the repo, a run record, a changelog entry, the ledger) stays the same; what moves is where its model of the project lives, from a private file set to the specs records. Not `feature`: no new capability reaches a user of the playbook. Not `bug`: nothing behaves against its intent — `vault/docs/_specs/` was deprecated by a decision (adr/0001), not by a defect.

Goal after landing ([value/0003 — Single source](../../specs/value/0003-single-source.md)): one model of the project — values, audience, surfaces, glossary, stories — read and kept current by the docs playbook, with no parallel `_specs/` set that drifts from the records.

## Problem

The docs playbook keeps its own spec set under `vault/docs/_specs/` — `index.md` (briefing), `roles.md`, `targets.md`, `features.md`, `glossary.md` — plus the `documented.md` ledger, and its steps write and read those files; gate hooks stamp `reviewed_at` on them. The same facts now live as typed records in `vault/specs/` (value/, reference/0001–0003, story/), so the two copies drift, and the specs README, adr/0001, CLAUDE.md, reference/0002 and reference/0003 carry deprecation notes waiting for this switch. After the change, every docs step reads (and `roles`, `targets`, `sync-specs` edit) the records; the feature index is rendered from story records; the ledger lives on as a run artefact; `vault/docs/_specs/` is gone along with every note and `sources:` entry that points at it.

## Clarifications and Decisions

- Autonomous run: intake's scope questions are settled by defaults, each recorded in `clarifications.md` (C1–C10).
- Ledger moves to `vault/docs/documented.md` (C1); briefing lands as a `## Briefing` section of the run record (C2); review stamps move onto the run record (C3).
- `feature-index` stops being a step — the index is a query spec over `specs/story/*.md` rendered into the bodies that read it; its gate goes with it (C4).
- `sources:` entries naming `vault/docs/_specs/*` (32 records) repoint to a GitHub permalink at `gh/master` commit `c7e43b4` (C6).
- Value records are never rewritten by the run — a vision shift is a `[clarify]` mark for the owner (C5).
