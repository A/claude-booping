# Develop defaults — 202610152053_project-manager-autonomous-extras

Autonomous run, 2026-10-15. Every gate or question the run settled itself.

- D1 — provision/branch: asked for a sprint branch name; default: reuse `feat/specs`, no new branch; why: the owner's run brief forbids switching branches.
- D2 — intake/drift: commit drift `5cdefb9..44b785b` touches only vault files (this plan's own files, idea/0003); default: proceed without revalidation; why: no plan-named code file changed.
- D3 — rule/0013 vs snapshot policy: rule/0013 forbids `just snapshots-accept`; default: accept only plan-described drift, listed below; why: the owner's standing permission for this feature (2026-10-14), recorded in the plan's Departures.
- D4 — develop-loop/M01–M04 commits: one commit per milestone; default: M01 and M02 share one commit (48a5df6), M03 07d664d, M04 778d6cf; why: M01 and M02 edit the same new module and config block, a hunk split would be artificial.
- D5 — develop-loop/M03 DoD "every existing run case passes unchanged": the worker added a fake `core.budget.probe` to `run/develop-autonomous-appends-the-preamble.txtar`'s fixture config; default: accepted; why: its expected stdout, record and log are unchanged, and without the fake the new launch gate would call the real `claude` probe.
