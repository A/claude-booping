---
summary: Implement the suite from the step's confirmed test plan — smoke rows as script asserts, regress rows as named rubrics.
agent: sonnet:medium
review_gate: "The user reviews the tree; the optimizer steps that follow take the suite to green"
inputs:
  - what: the target step name
  - what: the target step's confirmed contract and example
  - what: the step's confirmed test plan
  - what: the step's prompt body as shipped
  - what: one live suite as the pattern to follow
outputs:
  - <step>/promptfooconfig.yaml and <step>/tests.yaml
  - <step>/_fixtures/<case>.md per fixture row
  - proposed eval-smoke / eval-regress commands — proposed, never executed
---

{% include "opus-5.md" %}

{% include "_lib/return-contract.md" %}
