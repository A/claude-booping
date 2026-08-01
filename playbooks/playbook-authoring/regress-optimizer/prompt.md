---
summary: Read the baseline judge failures and tune the prompt toward the confirmed rubrics — prompt edits only; the harness runs baseline and verify.
agent: opus:medium
review_gate: "None on green — bounded to baseline → edits → one verify run; residual reds ship only by explicit user acceptance; a suspected-wrong rubric goes to the user"
inputs:
  - what: the target step name
  - what: the target step's confirmed contract and example
  - what: the step's confirmed test plan
  - what: the step's prompt body as shipped, smoke already green
  - from: runner
    what: the baseline regress report — per check PASS/FAIL with the failing judges' reasons
  - from: runner
    what: the regress command for the step's suite
outputs:
  - prompt-body edits, each naming the failed check it answers — or none on a green baseline
  - the regress verify command under `## Next:`
  - questions only for a rubric suspected wrong or a contract decision
---

{% include "opus-5.md" %}

{% include "_lib/return-contract.md" %}
