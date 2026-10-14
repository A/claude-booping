# Develop run defaults

Autonomous develop run on 2026-10-14: the owner was unavailable, so every gate was auto-confirmed and every open point settled by the run with the default below.

- **D1 — branch**: no new branch; the sprint commits on the existing `feat/specs`, as the owner's run instruction requires. Provision's branch-confirmation gate is taken as answered by that instruction.
- **D2 — commit messages**: Conventional Commits with a scope (`feat(specs): …`, `test(specs): …`, `docs(specs): …`) per [rule/0022](../../specs/rule/0022-conventional-commits-with-scope.md), over develop's `<agent>: <plan title> <message>` format, which contradicts the accepted rule. Vault commits keep develop's `develop: {slug} → {status}` hook shape.
- **D3 — intake drift**: plan `commit:` fd1ffb6 differs from HEAD 4964ceb (parent plan's work). A researcher spot-check found every milestone's code assumption still holds — drift classified none, nothing patched.
- **D4 — milestone groups**: one milestone per briefing (ceiling 1), four groups in id order.
- **D5 — snapshot baselines**: the run never runs `just snapshots-accept` nor writes `_reports/` ([rule/0013](../../specs/rule/0013-snapshot-baselines-accepted-by-user.md)); the expected `## Rules` drift is left for the owner to review and accept, so `just snapshots` (and therefore `just ci`) stays red on that check until they do.
