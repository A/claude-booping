---
status: spec-ing
---

# regress-optimizer

[← index](../../index.md)

## Contract

- **Needs** —
  - the target step name
  - the target step's confirmed contract and example
  - the step's confirmed test plan
  - the step's prompt body as shipped, smoke already green
  - the baseline regress report — per check PASS/FAIL with the failing judges' reasons
  - the regress command for the step's suite
- **Value** — the best-effort guarantee that the step's semantic contract is confirmed by its
  judged eval tests — smoke pins the shape, this tier confirms the meaning. The step itself
  never runs an eval: it reads the given judge failures and tunes the prompt; the harness
  runs baseline and verify.
- **Output files** —
  - `[UPDATED] <name>/<step>/<model>.md` — or nothing, when the baseline is green
- **Harness return** —
  - `## Changed:` list (or `(none)`), each edit naming the failed check it answers
  - `## Next:` the regress command for the harness to run as the verify pass; residual reds
    after it go to the user, not back to this step
  - `## Questions:` only for a rubric suspected wrong or a failure that needs a contract
    decision
- **Review gate** —
  - none on green: the rubrics are already confirmed and this step only tunes the prompt
    toward them — prompt edits ONLY, a misjudging rubric is a question, never relaxed
  - the loop lives in the harness, bounded: baseline run → invoke this step → verify run;
    further tuning loops only when the user asks
  - residual reds after the verify run ship only by explicit user acceptance, each named
  - the run-or-skip decision is made once per playbook run; on skip the harness never invokes
    this step; the user can flip it manually

## Return Format

```markdown
## Changed:
- [UPDATED] mod-review/compose/opus-5.md — GROUNDED-FIX failed: fix sketches restated the
  defect; added the demand that each sketch name the concrete change

## Next:
just eval-regress -c mod-review/compose/promptfooconfig.yaml — the verify pass; residual reds
go to the user

## Questions:
(none)
```
