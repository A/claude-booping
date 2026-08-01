# Optimize a step to green smoke

The input is the target step's name, its confirmed spec (contract + example artifact), its
confirmed test plan, its prompt body and suite as shipped, the latest smoke run report with
the attempt number, and the smoke command for its suite. You run fresh each attempt; the tree
and the report are your only memory.

You never run an eval. You diagnose the report you were given, edit the guilty side, and hand
the run back to the harness.

## Diagnosis

The confirmed example IS the contract. For each red check decide which side drifted from it:

- the check demands something the example's own artifact would fail → the **check** is wrong;
  fix the rule so the example passes
- the prompt lets output drift from what the example shows → the **prompt** is wrong; fix the
  body so a fresh consumer produces the example's shape
- the example decides neither side → edit **nothing** for that check; return the question

The verdict comes from the example alone, and only for what it can witness. An example
convicts on structure it exhibits; a rule pinned to one fixture's own content — a count of
its seeded items — is witnessed only by an example on that same input, and an example of
another input decides shape, never counts. The spec's prose, the test plan's rows, and the
fixture are context for wording a fix, never grounds to convict.

Never bend the innocent side to make a run green: a relaxed correct check leaves the suite
vacuous; a correct prompt padded toward a wrong check ships the drift.

## Edits

- prompt guilty → the step's prompt body (`<playbook>/<step>/<model>.md`)
- check guilty → the step's `tests.yaml` or `promptfooconfig.yaml`

Touch only what a diagnosed red demands; every edit maps to a named red check.

## Return format

```
## Changed:
- [UPDATED] <path> — <CHECK> red: <the mismatch, and which side was wrong>

## Next:
<smoke command> — on red, re-invoke with the fresh report (this was attempt <n>)

## Questions:
```

Diagnosis prose belongs in the `## Changed:` entries or a question, nowhere else.
`## Changed:` is empty when every red is undecidable. A question names its check and states
both readings the example fails to decide.
