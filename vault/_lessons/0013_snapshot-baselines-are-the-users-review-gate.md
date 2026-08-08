---
title: Snapshot baselines are the user's review gate
targets:
  - develop
---

Never run `just snapshots-accept` and never write `playbooks/*/_reports/output.md` — not from the orchestrator and not from a worker briefing. The committed snapshot reports are a review gate: accepting them from inside a run silently passes playbook-source changes through the gate the baseline exists to enforce.

When sprint work touches playbook sources (manifests, step `prompt.md`, shared partials, `src/templates/`), the committed reports will drift. At wrap-up, run the read-only `just snapshots`, present the drift to the user, and ask them to review and accept the baseline themselves (`just snapshots-accept`) before the closing commit. No drift → nothing to ask.
