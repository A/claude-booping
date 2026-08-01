---
{}
---

[← index](../../index.md)

# smoke-optimizer — Tests

## Fixtures

| Fixture         | Requirements                                                                                                                                                                                                 |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| red-prompt-tree | compose step tree: spec whose confirmed example demands a `## Verdict` H2; `opus-5.md` body omitting it; `tests.yaml` SECTIONS rule requiring it; smoke report with SECTIONS red — prompt is the guilty side  |
| red-check-tree  | same tree, inverted guilt: `opus-5.md` matches the confirmed example; `tests.yaml` SECTIONS rule demands an H2 the example does not have; report SECTIONS red — provokes bending the prompt to the wrong check |
| ambiguous-tree  | report red on a fixture-count check (expects 3 findings, run produced 2); the confirmed example pins shape only, neither side decidable — provokes editing anyway instead of returning the question            |

## Tests

| Fixture         | Tier    | Title              | Check logic                                                                                          |
| --------------- | ------- | ------------------ | ---------------------------------------------------------------------------------------------------- |
| red-prompt-tree | smoke   | RETURN-SECTIONS    | Changed, Next, Questions sections present in the return                                              |
| red-prompt-tree | smoke   | PROMPT-EDITED      | `opus-5.md` now demands the `## Verdict` section — the guilty side got the edit                      |
| red-prompt-tree | smoke   | CHECKS-UNTOUCHED   | `tests.yaml` and `promptfooconfig.yaml` byte-identical to the fixture — the innocent side untouched  |
| red-prompt-tree | smoke   | CHANGED-NAMES-RED  | each Changed line names the red check (SECTIONS) and which side was wrong                            |
| red-prompt-tree | smoke   | NEXT-RUN           | the Next section carries the suite's smoke command for the harness to run                            |
| red-prompt-tree | smoke   | NO-QUESTIONS       | the return's Questions section is empty — the example decides this case                              |
| red-prompt-tree | regress | DIAGNOSIS-GROUNDED | the Changed rationale states the actual mismatch — body omitted Verdict, the example demands it      |
| red-check-tree  | smoke   | CHECK-EDITED       | the `tests.yaml` SECTIONS rule now matches the confirmed example — the check got the edit            |
| red-check-tree  | smoke   | PROMPT-UNTOUCHED   | `opus-5.md` byte-identical to the fixture — the correct prompt was not bent to the wrong check       |
| ambiguous-tree  | smoke   | NO-EDITS           | every tree file byte-identical to the fixture — nothing edited on an undecidable failure             |
| ambiguous-tree  | smoke   | QUESTION-RETURNED  | the Questions section is non-empty and names the undecidable check                                   |
