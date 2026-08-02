---
reviewed_at: 20260802 09:52
---

[← index](../../index.md)

# intake — Tests

## Fixtures

| Fixture              | Requirements                                                                                                                                                                                                                                                                                                                                                                                                             |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ready-for-dev-drift  | `plans/20260728-09-15_playbook-run-state/index.md` at `status: ready-for-dev`, `commit: a1f3c02`, three milestones with task rows, per-task file lists, DoD checkboxes and Verify commands; the repo's own conventions; the cheap summary supplied verbatim — HEAD `7d9e4b1`, 6 commits, 11 files, +240/−58, the changed-name list and log subjects, one plan-named file among them (`booping-python/src/booping/context/playbook.py`); the user's in-step answers: revalidate yes, patch approved; and the plan-named slice of the diff showing `load_all` gained a `home_dir` argument |
| approved-then-halt   | the same plan at `status: awaiting-plan-review`, the user's approval in their own words ("looks good") carried in the input; baseline `a1f3c02`, the same cheap summary, and the revalidated plan-named slice showing 4 of the 5 plan-named files rewritten and the module M3 targets deleted                                                                                                                              |
| legacy-no-baseline   | the same plan at `status: ready-for-dev` with no `commit:` key at all; repo HEAD `7d9e4b1` and the repo's conventions; the researcher's file-shape spot-check return supplied inline — the harness spawns nothing — reporting the 4 plan-named files still match the plan's assumptions                                                                                                                                   |

## Tests

| Fixture             | Tier    | Title             | Check logic                                                                                                                                     |
| ------------------- | ------- | ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| ready-for-dev-drift | smoke   | ONLY-PLAN-TOUCHED | `plans/20260728-09-15_playbook-run-state/index.md` is the only file written — no run note, no second plan, no branch artefact                    |
| ready-for-dev-drift | smoke   | FRONTMATTER-INTACT| the written index still reads `status: ready-for-dev` and `commit: a1f3c02`; no `started`, no re-snapshot, no key added or removed               |
| ready-for-dev-drift | smoke   | PATCH-SCOPED      | the only changed line is M2's task row naming `load_all`; every other task row, DoD checkbox, Verify command and milestone row byte-identical    |
| ready-for-dev-drift | smoke   | PATCH-VALUE       | the patched row reads `load_all(vault, home_dir, plugin_root)`; the stale two-argument form appears nowhere in the file                          |
| ready-for-dev-drift | smoke   | RETURN-SHAPE      | `## Changed:` is one `[UPDATED]` entry for that path annotated with the trivial-drift patch; `## Questions:` empty; no `## Next:`                |
| ready-for-dev-drift | smoke   | NOTES-FACTS       | Notes carries entry status `ready-for-dev` named a valid entry transition, verdict `trivial drift patched`, and `6 commits / 11 files since baseline a1f3c02, 1 of them plan-touched` |
| ready-for-dev-drift | regress | DRIFT-PER-FILE    | every plan-named file carries a changed/unchanged verdict against the baseline, and the 10 changed files no plan task names are not reported as drift |
| ready-for-dev-drift | regress | TRIVIAL-JUDGED    | the trivial call rests on the signature change against the plan's own assumption — no milestone, DoD line or Verify command invalidated — not on the commit or file counts |
| ready-for-dev-drift | regress | CHEAP-FIRST       | the plan-named slice is used only after the user's revalidate answer; nothing in the reply rests on diff hunks outside the plan-named files      |
| ready-for-dev-drift | regress | NO-SCOPE-CREEP    | nothing beyond the drift is done: no re-estimation, no milestone added or reordered, no branch, no groups, no worker briefed                     |
| approved-then-halt  | smoke   | NOTHING-WRITTEN   | no file in the manifest and `## Changed:` empty — the plan is left exactly as it arrived                                                         |
| approved-then-halt  | smoke   | HALT-VERBATIM     | the reply carries the halt sentence verbatim, plan path filled in: *"The drift is significant — re-shape the plan with `/groom plans/20260728-09-15_playbook-run-state/index.md` before continuing."* |
| approved-then-halt  | smoke   | RETURN-NEXT       | `## Next:` holds `/groom plans/20260728-09-15_playbook-run-state/index.md`; `## Questions:` empty                                                |
| approved-then-halt  | smoke   | NOTES-HALT        | Notes names entry status `awaiting-plan-review` with approval captured, `non-trivial drift — run halted, no transition taken`, and the plan-touched headline |
| approved-then-halt  | regress | APPROVAL-QUOTED   | approval is credited to the user's own words in the input; the plan sitting at `awaiting-plan-review` is never itself treated as approval        |
| approved-then-halt  | regress | HALT-GROUNDED     | the non-trivial verdict names M3's deleted target module and the 4 rewritten plan-named files, not the commit count                              |
| approved-then-halt  | regress | NO-SALVAGE        | nothing is patched, re-scoped or re-planned around the halt — no partial adoption, no "start M1 meanwhile", no rewritten milestone               |
| legacy-no-baseline  | smoke   | NOTHING-WRITTEN   | no file written; `## Changed:` and `## Questions:` both empty and no `## Next:` — the in-sync path writes nothing                                |
| legacy-no-baseline  | smoke   | NOTES-IN-SYNC     | Notes names entry status `ready-for-dev`, verdict `in sync`, and a headline stating there is no `commit:` baseline and the file-shape spot-check stood in for it |
| legacy-no-baseline  | regress | SPOT-CHECK-USED   | the verdict rests on the returned file shapes against the plan's assumptions; no commit-range or "since baseline" claim is made where no baseline exists |
| legacy-no-baseline  | regress | SPOT-CHECK-THIN   | only mismatches are reported — here none — and the researcher's file-by-file material is not replayed into the report                            |
