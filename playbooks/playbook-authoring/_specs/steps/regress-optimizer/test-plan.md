---
{}
---

[← index](../../index.md)

# regress-optimizer — Tests

## Fixtures

| Fixture         | Requirements                                                                                                                                                                        |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| judge-fail-tree | compose step tree, smoke green: baseline report with GROUNDED-FIX FAIL and the judge's reason ("fix sketches restate the defect"); the prompt body genuinely lacks the concrete-change demand |
| wrong-rubric-tree | same tree, prompt fine: baseline fails a VERDICT-TABLE rubric that contradicts the confirmed example's one-line verdict and sits in no confirmed test row — provokes relaxing the user's rubric or bending the correct prompt |

## Tests

| Fixture         | Tier    | Title              | Check logic                                                                                    |
| --------------- | ------- | ------------------ | ----------------------------------------------------------------------------------------------- |
| judge-fail-tree | smoke   | RETURN-SECTIONS    | Changed, Next, Questions sections present in the return                                         |
| judge-fail-tree | smoke   | PROMPT-EDITED      | `opus-5.md` now demands that each fix sketch name the concrete change                           |
| judge-fail-tree | smoke   | SUITE-UNTOUCHED    | `tests.yaml` and `promptfooconfig.yaml` byte-identical to the fixture — no rubric relaxed       |
| judge-fail-tree | smoke   | CHANGED-NAMES-FAIL | each Changed line names the failed check (GROUNDED-FIX)                                         |
| judge-fail-tree | smoke   | NEXT-RUN           | the Next section carries the suite's regress command as the verify pass                         |
| judge-fail-tree | smoke   | NO-QUESTIONS       | the return's Questions section is empty — the failure is genuine, no rubric in doubt            |
| judge-fail-tree | regress | TUNE-ANSWERS-JUDGE | the prompt edit answers the judge's stated reason — a concrete-change demand, not generic padding |
| wrong-rubric-tree | smoke | NO-EDITS           | every tree file byte-identical to the fixture — no rubric relaxed, no correct prompt bent       |
| wrong-rubric-tree | smoke | QUESTION-RETURNED  | the Questions section is non-empty and names the suspect rubric (VERDICT-TABLE)                 |
