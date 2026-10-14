# Develop run defaults

Autonomous develop run on 2026-10-14: the owner was unavailable, so every gate was auto-confirmed and every open point settled by the run with the default below.

- **D1 — branch**: no new branch; the sprint commits on the existing `feat/specs`, as the owner's run instruction requires. Provision's branch-confirmation gate is taken as answered by that instruction.
- **D2 — commit messages**: Conventional Commits with a scope (`fix(specs): …`, `fix(playbooks): …`, `fix(code-review): …`) per [rule/0022](../../specs/rule/0022-conventional-commits-with-scope.md), over develop's `<agent>: <plan title> <message>` format, which contradicts the accepted rule. Vault commits keep develop's `develop: {slug} → {status}` hook shape.
- **D3 — intake drift**: plan `commit:` 7183ceb differs from HEAD 1fc8682 only by groom's own commit of this plan's files; no plan-touched file changed, drift none, nothing patched.
- **D4 — milestone groups**: one milestone per briefing (ceiling 1), three groups in id order.
- **D5 — snapshot baselines**: [rule/0013](../../specs/rule/0013-snapshot-baselines-accepted-by-user.md) and lesson 0013 reserve `just snapshots-accept` for the owner; the owner's run instruction (standing permission for this feature, 2026-10-14) overrides it for this run: accept only when every drifted hunk is a change the plan describes. Accepted reports are listed below.
