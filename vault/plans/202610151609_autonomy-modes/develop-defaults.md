# Develop defaults — autonomous run, 2026-10-15

Decisions the runner took without the owner, per the run's AUTONOMOUS RUN instruction.

## D1 — develop/provision — branch

**Asked:** Confirm the sprint branch name (provision gate, normally through `AskUserQuestion`).

**Default:** no new branch; the sprint commits on the existing `feat/specs` in the worktree `/home/anton/Dev/@A/claude-booping-specs`.

**Why:** the invocation forbids switching branches; it names `feat/specs` as the run's branch.

## D2 — develop/provision — milestone groups

**Asked:** none (internal to the step).

**Default:** G1 = M01–M04 (13 SP), G2 = M05–M06 (5 SP), greedy under the 15 SP cap.

**Why:** the provision packing rule; recorded for traceability.

## D3 — develop/develop-loop — commit message format

**Asked:** develop's `<agent>: <plan title> <message>` format vs rule/0022 (Conventional Commits with scope).

**Default:** Conventional Commits with scope (`feat(booping): …`), as every earlier sprint on this branch did.

**Why:** rule/0022 is the project's rule; a choice contradicting a rule is wrong per the run instruction.

## D4 — develop/wrap-up — snapshot acceptance

**Asked:** rule/0013 says the runner never runs `just snapshots-accept`.

**Default:** accept drift only when every hunk is one the plan describes (M04 specs, M05 migrate), per the owner's standing permission for this feature (2026-10-14) restated in the invocation and in the plan's Departures; each accepted report is listed below.

**Why:** the owner's explicit, scoped permission; any other drift stops the run.

## D5 — develop/develop-loop — accepted report: playbooks/specs/_reports/output.md

**Asked:** accept the specs report drift (rule/0013 departure, per D4).

**Default:** accepted with M04's commit `3b684ae`.

**Why:** the drift was exactly two hunks, both M04's: the `Autonomy:` preamble line and the replaced `Next:` sentence (Supervised/Autonomous lines), matching the plan's output contract.
