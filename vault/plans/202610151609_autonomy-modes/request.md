# Request

> Continue the specs workflow request below: groom the next part that the previous plans of this request (the latest done plans in vault/plans whose request names adr/0024-0027) left out of scope as a parked follow-up. If every part is already done, write NOTHING-LEFT as the last line and stop without creating a plan.
>
> Request — the specs workflow, as decided in booping's own records (read them first, they are the brief): vault/specs/adr/0024-specs-playbook-is-a-guide.md, 0025-open-items-are-an-index.md, 0026-corrections-log.md, 0027-autonomy-modes.md, specs/rule/0030-planning-shows-values-in-play.md, value/0015.
> Parts:
> 1. A core `specs` playbook that is a guide (adr/0024): an explanation of every record type and principle (reuse src/specs/README.md by reference, never restate it) plus the user's scenarios (init with the alignment guide, alignment, auto-review for internal conflicts, recording a decision/idea/rule, sync specs and code, retro-to-rules, working open items); the model decides from the dialogue. Its evals per the repo's playbook conventions (smoke tier at least).
> 2. Open items (adr/0025): `{vault}/open-items/OI-NNNN.md` with a state machine (open, planned, done, dropped), `booping specs open-items` (list = index of open ones, add, close), created when an ADR with a confirmation line lands and by sync/check; closing the plan closes the item.
> 3. Corrections (adr/0026): `booping correction add` writing a short entry with step, did, said (verbatim), why, and a dialogue link (session id + message position, the way session-stats finds the transcript) into the run artefact's `corrections.md` sidecar; a core rule injected into groom, develop and code-review telling the agent to log corrections; retro reads the sidecar as its feed.
> 4. Autonomy modes (adr/0027): a project config key `supervised` (default) | `autonomous`; the specs playbook's open-items scenario and a manager path honour it; uncommitted changes on a branch during a migration are always shown and asked about.
>
> AUTONOMOUS RUN. The owner is not available: do not ask questions and do not wait at review gates — auto-confirm them yourself; settle unclear points with a sensible default and record every default in the plan's clarifications.md (groom) or a develop-defaults.md beside the plan (develop). You run in the worktree /home/anton/Dev/@A/claude-booping-specs on branch feat/specs: never switch branches, never push, stage by path (never git add -A). Read vault/specs (value/, rule/, adr/0001) and src/specs/README.md before deciding anything; a choice that contradicts a value or rule is wrong. Snapshot policy for this run (owner's standing permission for this feature, 2026-10-14): when `just snapshots` drifts, you may run `just snapshots-accept` only if every drifted hunk is a change the plan describes; list each accepted report and why in the run's defaults file. Any other drift: stop and report. A red `just ci` is fixed by a worker, never by weakening a check. If a groom splits the request, groom only the first plan and list the rest as parked stubs. Do not end the run while a check is still running: wait for just ci to finish and report its result. End at ready-for-dev.

## Task type

`feature` — a new user-facing capability: a project config key that switches how every review gate behaves, an autonomous path that takes open items through groom and develop without stopping, and a new mandatory question in migrate. Not `bug`: nothing today diverges from expected behaviour — every run stopping at its gate is the documented design (adr/0015). Not `refactoring`: user-visible behaviour changes (gates auto-confirm in autonomous projects, migrate asks about a dirty branch).

## Problem

Parts 1–3 shipped in [plans/202610151409_specs-playbook-open-items](../202610151409_specs-playbook-open-items/index.md) and [plans/202610151532_corrections-log](../202610151532_corrections-log/index.md); the latter's `## Out of scope` parks part 4 (autonomy modes, adr/0027) as the last stub. This plan grooms it.

Today every run stops at its review gate, whatever the project — an autonomous run like this one exists only as hand-written prompt prose ("AUTONOMOUS RUN … auto-confirm gates … record every default"), restated per invocation. No config says which mode a project works in, so the specs playbook's open-items scenario cannot take items through groom and develop on its own, and migrate does not look at uncommitted changes on the current branch before it rewrites the vault. After this plan: a project config key chooses `supervised` (default — gates stop for the user, as today) or `autonomous` (gates auto-confirmed, every default recorded in a defaults sidecar); the specs playbook's open-items scenario honours it — autonomous takes ready items through groom and develop without stopping, supervised stops at the plan review; and migrate always shows uncommitted changes on the branch and asks about them, in either mode.

## Clarifications and Decisions

- Scope: part 4 only — the last parked part; the core `project-manager` playbook (adr/0028) is its own request and stays out — C1.
- All further calls settled by default in drafting and recorded in `clarifications.md` (autonomous run).
