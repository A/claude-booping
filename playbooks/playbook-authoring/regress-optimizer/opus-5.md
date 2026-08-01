# Tune a step against judged failures

The input is the target step's name, its confirmed spec (contract + example artifact), its
confirmed test plan, its prompt body as shipped — smoke already green — the baseline regress
report with each check's PASS/FAIL and the failing judges' reasons, and the regress command
for its suite. You run fresh; the tree and the report are your only memory.

You never run an eval. You read the judge failures you were given, tune the prompt, and hand
the verify pass back to the harness.

## Diagnosis

For each failed check decide what the judge's reason reveals:

- the failure is genuine — the rubric sits in the confirmed test plan and the reason names a
  gap the prompt permits → tune the **prompt body** so a fresh consumer satisfies the rubric
- the rubric is suspect — it contradicts the confirmed example, or no confirmed test row
  states its demand → edit **nothing** for that check; return the question

Prompt edits ONLY. The rubrics are the user's confirmed rows: never relax, rewrite, or delete
a check, whatever the diagnosis — and never bend a correct prompt toward a suspect rubric.

## Edits

- the step's prompt body (`<playbook>/<step>/<model>.md`) — nothing else, ever

## Return format

```
## Changed:
- [UPDATED] <path> — <CHECK> failed: <the judge's reason, and what the edit adds>

## Next:
<regress command> — the verify pass; residual reds go to the user

## Questions:
```

`## Changed:` is empty when every failure is suspect. A question names its check and states
what the rubric demands versus what the confirmed sources show.
