# Develop defaults

Autonomous develop run on 2026-10-15: the owner was unavailable, so every point below was settled by the run with a default. Each stays reviewable ([value/0009](../../specs/value/0009-adjustable-control.md)).

## D1 — branch

The plan's type `feature` picks `feat/`; the invocation fixed the branch: the existing `feat/specs`, reused, never switched. No branch created.

## D2 — commit message format

develop's step text says `<agent>: <plan title> <message>`; [rule/0022](../../specs/rule/0022-conventional-commits-with-scope.md) requires Conventional Commits with a scope, and the run brief says a choice contradicting a rule is wrong. Default applied: repo commits use `feat(specs): {message}` (or the fitting type/scope), with the worker agent and plan title carried in the commit body.

## D3 — snapshot baselines

[rule/0013](../../specs/rule/0013-snapshot-baselines-accepted-by-user.md) forbids a run accepting baselines. The owner's standing permission for this feature (2026-10-14, restated in the run brief) overrides it for this run only: `just snapshots-accept` may run when every drifted hunk is a change the plan describes. Each accepted report is listed below.

## D4 — milestone groups

Cap 15 SP, greedy in id order: G1 M01–M04 (13 SP), G2 M05–M08 (14 SP), G3 M09–M10 (7 SP).

## D5 — commit drift at intake

Plan `commit: 984e172` vs HEAD `1e9a8f6`: the three commits between are groom's own vault commits on this plan's files; no plan-named code changed. No drift.

## D6 — standalone per-instance machine

M01's worker found the engine rejects the groomed `open_item` machine: a state with `{instance}` in `artifact` must be referenced by a subgraph (`bad_state`, STOP on render), and an unreferenced state raises `orphan_state`. Options: reshape the guide into a per-item subgraph (contradicts C2/adr/0024) or let a machine declare itself CLI-moved. Default applied: an opt-in `standalone: true` key on a `states:` entry exempts it from both checks; `open_item` sets it. Added to M01 as task 1.3; the checks stay intact for every unkeyed state.

## D7 — reopen clears plan to null

The Architecture table says `frontmatter-update plan=''`; the item shape wants `plan: null`. Default applied: `plan=null`.

## D8 — one commit for M02–M04, case counts

M02–M04 share `commands/specs.py` and `specs/open_items.py`; path staging cannot split one file across milestones, so M02–M04 land as one commit (`bc387db`), M01 as its own (`956b528`). M03 ships 3 list cases (plan said 2) and M04 8 (plan said 7): a txtar case runs one command, so two-command behaviours split in two — a superset of the named behaviours, accepted.

## Accepted snapshot reports

{filled in as accepted}
