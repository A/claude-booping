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

`feature` — a new user-facing capability: a CLI verb (`booping correction add`), a new run-artefact sidecar, a core rule steering three playbooks, and a new input to retro. Not `bug`: nothing today diverges from expected behaviour — retro mining transcripts is the documented current design. Not `refactoring`: user-visible behaviour changes (agents log, retro reads a new feed).

## Problem

Parts 1 and 2 shipped in [plans/202610151409_specs-playbook-open-items](../202610151409_specs-playbook-open-items/index.md); its `## Out of scope` parks part 3 (corrections, adr/0026) and part 4 (autonomy modes, adr/0027). This plan grooms part 3.

Today retro digs the moments the user corrected the model out of whole session transcripts — expensive in tokens and lossy over long sessions. Nothing records a correction when it happens. After this plan: when the user corrects the model in groom, develop or code-review, the agent runs `booping correction add`, which appends one entry (step, did, said verbatim, why, dialogue link = session id + message position) to `corrections.md` beside the run artefact; a core rule targeted at those three playbooks tells the agent to do so; retro reads the sidecar as its feed. A correction touching a spec also files an open item (adr/0026 Consequences).

## Clarifications and Decisions

- Scope: part 3 only; part 4 (autonomy modes) stays parked as a stub — C1.
- All further calls settled by default in drafting and recorded in `clarifications.md` (autonomous run).
