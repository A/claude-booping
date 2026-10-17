# Request

## Request

> Request — the specs workflow, as decided in booping's own records (read them first, they are the brief): vault/specs/adr/0024-specs-playbook-is-a-guide.md, 0025-open-items-are-an-index.md, 0026-corrections-log.md, 0027-autonomy-modes.md, specs/rule/0030-planning-shows-values-in-play.md, value/0015.
> Parts:
> 1. A core `specs` playbook that is a guide (adr/0024): an explanation of every record type and principle (reuse src/specs/README.md by reference, never restate it) plus the user's scenarios (init with the alignment guide, alignment, auto-review for internal conflicts, recording a decision/idea/rule, sync specs and code, retro-to-rules, working open items); the model decides from the dialogue. Its evals per the repo's playbook conventions (smoke tier at least).
> 2. Open items (adr/0025): `{vault}/open-items/OI-NNNN.md` with a state machine (open, planned, done, dropped), `booping specs open-items` (list = index of open ones, add, close), created when an ADR with a confirmation line lands and by sync/check; closing the plan closes the item.
> 3. Corrections (adr/0026): `booping correction add` writing a short entry with step, did, said (verbatim), why, and a dialogue link (session id + message position, the way session-stats finds the transcript) into the run artefact's `corrections.md` sidecar; a core rule injected into groom, develop and code-review telling the agent to log corrections; retro reads the sidecar as its feed.
> 4. Autonomy modes (adr/0027): a project config key `supervised` (default) | `autonomous`; the specs playbook's open-items scenario and a manager path honour it; uncommitted changes on a branch during a migration are always shown and asked about.

## Task type

`feature` — a new user-facing surface (a playbook the user calls, a CLI command, a vault artefact). Not `bug`: nothing diverges from specified behaviour, the ADRs describe behaviour that does not exist yet. Not `refactoring`: user-visible behaviour changes — a new playbook appears in `/playbook`, a new `booping specs open-items` command and a new `open-items/` vault directory.

## Problem

Today specs records are written by hand or by `learn` (rules only); there is no user surface to set a tier up with an alignment interview, record a decision, review the set for internal conflicts or sync specs with code, and a gap between a record and the code (an ADR's unconfirmed `Confirmation:` line, a `[clarify]`, a check finding) lives nowhere a run can take it. After this plan, `/playbook specs` guides the user through every specs scenario from the dialogue (adr/0024), and gaps become stored open items listed and closed by `booping specs open-items` and closed with the plan that works them (adr/0025).

## Clarifications and Decisions

- Autonomous run: every unclear point is settled by a default recorded in `clarifications.md`.
- Split (C1): the four parts pass the 35 SP threshold together; this plan grooms parts 1 and 2 — the specs playbook and open items, the dependency seam the other parts build on. Part 3 (corrections, adr/0026) and part 4 (autonomy modes, adr/0027) are parked as sibling stubs in `index.md` `## Out of scope`.
- The specs playbook's open-items scenario in this plan works items the supervised way only (stop at the plan review); the autonomous path arrives with part 4.
