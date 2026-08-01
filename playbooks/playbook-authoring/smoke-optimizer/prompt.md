---
summary: Diagnose a red smoke report against the confirmed example and edit the guilty side — prompt or check; the harness runs the tier between invocations.
detached: opus:medium
review_gate: "None on green — the harness loops run → re-invoke; the same check red three attempts without progress, or a failure the example does not decide, goes to the user"
inputs:
  - what: the target step name
  - what: the target step's confirmed contract and example
  - what: the step's confirmed test plan
  - what: the step's prompt body and suite as shipped
  - from: runner
    what: the latest smoke run report — the red checks with their reasons — and the attempt number
  - from: runner
    what: the smoke command for the step's suite
outputs:
  - edits to the prompt body or the suite checks, each naming its red check and the guilty side
  - the smoke command under `## Next:` for the harness to run
  - questions only when blocked or when the example does not decide a failure
---

{% include "opus-5.md" %}

{% include "_lib/return-contract.md" %}
