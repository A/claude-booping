---
status: spec-ing
---

# smoke-optimizer

[← index](../../index.md)

## Contract

- **Needs** —
  - the target step name
  - the target step's confirmed contract and example
  - the step's confirmed test plan
  - the step's prompt body and suite as shipped
  - the latest smoke run report — the red checks with their reasons — and the attempt number
  - the smoke command for the step's suite
- **Value** — the best-effort guarantee that the step's contract is confirmed by its smoke
  tests. The step itself never runs an eval: it diagnoses the given red report and edits the
  guilty side; the harness runs the tier between invocations.
- **Output files** —
  - `[UPDATED] <name>/<step>/<model>.md` — when the prompt was the guilty side
  - `[UPDATED] <name>/<step>/tests.yaml` / `promptfooconfig.yaml` — when a check was
  Each edit traceable to a named red check.
- **Harness return** —
  - `## Changed:` list, each edit naming the red check and which side was wrong
  - `## Next:` the smoke command for the harness to run — on green the step is done, on red
    re-invoke this step with the fresh report and the attempt count
  - `## Questions:` only when blocked
- **Review gate** —
  - none on green: the contract is already confirmed and this step only adapts prompt and
    checks to it
  - the loop and its bound live in the harness: run → red → re-invoke with the fresh report;
    the same check red three attempts without progress → stop re-invoking, bring the step's
    questions to the user
  - the user is also pulled in when the example itself does not decide a failure — the step
    then edits nothing and returns the question

## Return Format

```markdown
## Changed:
- [UPDATED] mod-review/compose/opus-5.md — SECTIONS red: body never asked for a Verdict
  section; prompt was wrong, example demands it
- [UPDATED] mod-review/compose/tests.yaml — KNOWN-DEFECT red: rule required the finding under
  an H2 the example does not have; check was wrong

## Next:
just eval-smoke -c mod-review/compose/promptfooconfig.yaml — on red, re-invoke with the fresh
report (this was attempt 1)

## Questions:
(none)
```
