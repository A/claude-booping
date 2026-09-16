**Blocked (1/2)**: the return edges clear `return_to` to the string `'null'`, so DoD 5.2 line 1 is unmet.

## What was checked

- `dispatch_frontmatter_update` in `booping-python/src/booping/commands/playbook_transition.py` passes hook values to the writer raw; `coerce_scalar` is called only from `frontmatter_update.py:168`. Your diagnosis is correct.
- The proposed source fix was put to the user and **declined** — `booping-python/src/` stays out of this milestone, and the date-valued hooks in develop, code-review and playbook-authoring must not change how they land.

## What the next attempt must do

Clear the key with an **empty value** instead of `null`: the return edges' hooks become `frontmatter-update index.md return_to=''`.

This needs no source change. `coerce_scalar` returns blank input unchanged, so the hook path and the CLI path already agree on it — verified against a scratch artifact, `return_to: framing` → `return_to: ''`, cleared and falsy with no `'null'` string anywhere.

- Both return edges take the empty-value form; hook order and `script tracker-sync`-last are unchanged.
- Rebaseline `the-return-edge-off-a-parked-groom-run-clears-the-recorded-status.txtar` onto the new receipt, and rewrite its prose — it currently documents the `'null'` defect as intended behaviour, which is no longer true.
- The scaffold seed stays `return_to: null`. Seeded-null and cleared-empty are both falsy; the gate tests whether `return_to` matches the target status, and an empty value matches nothing.
- Leave DoD 5.2's wording alone. "Clears the key" is satisfied; the runner records the null-vs-empty deviation in its own report.

Everything else in the milestone was validated and stands — do not redo it.
