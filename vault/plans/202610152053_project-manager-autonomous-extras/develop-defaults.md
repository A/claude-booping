# Develop defaults — 202610152053_project-manager-autonomous-extras

Autonomous run, 2026-10-15. Every gate or question the run settled itself.

- D1 — provision/branch: asked for a sprint branch name; default: reuse `feat/specs`, no new branch; why: the owner's run brief forbids switching branches.
- D2 — intake/drift: commit drift `5cdefb9..44b785b` touches only vault files (this plan's own files, idea/0003); default: proceed without revalidation; why: no plan-named code file changed.
- D3 — rule/0013 vs snapshot policy: rule/0013 forbids `just snapshots-accept`; default: accept only plan-described drift, listed below; why: the owner's standing permission for this feature (2026-10-14), recorded in the plan's Departures.
- D4 — develop-loop/M01–M04 commits: one commit per milestone; default: M01 and M02 share one commit (48a5df6), M03 07d664d, M04 778d6cf; why: M01 and M02 edit the same new module and config block, a hunk split would be artificial.
- D5 — develop-loop/M03 DoD "every existing run case passes unchanged": the worker added a fake `core.budget.probe` to `run/develop-autonomous-appends-the-preamble.txtar`'s fixture config; default: accepted; why: its expected stdout, record and log are unchanged, and without the fake the new launch gate would call the real `claude` probe.
- D6 — develop-loop/M05 batch case: the contract's example (cap 8 → `B1 (7 SP)` + `B2 (1 SP)`) contradicts its own packing rule (7 + 1 = 8 ≤ 8 joins B1); default: keep the rule, pin the case's vault to `max_sp: 7` so the example's expected lines hold; why: the I/O contract's rule is the spec, the example was an arithmetic slip.
- D7 — develop-loop/M05 rebaseline: besides the `items` cases, `status/detail-flag-prints-every-section`, `correction/add-record-keeps-the-namespace` and `correction/add-record-files-an-open-item-linked-from-the-entry` gained the `size` column / `size: null` scaffold line; default: accepted; why: every changed hunk is the column M05 adds, nothing else.
- D8 — wrap-up/snapshots: accepted `playbooks/develop/_reports/output.md` (develop-loop's new gate step 1 and renumbering, M06) and `playbooks/project-manager/_reports/output.md` (work step: tiny-fix sizing, `items batch` loop, paused/resume lines in Runs, `paused` report row, M06); commit b373951; why: every drifted hunk is a change the plan describes, under the owner's snapshot policy.
- D9 — wrap-up/docs: `documentation/vault.md`'s run-status list missed `paused`; default: the runner added it in the closing commit 7f94a26; why: the sprint invalidated that sentence, and `just docs` builds clean.
