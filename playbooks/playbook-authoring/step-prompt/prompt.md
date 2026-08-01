---
summary: Write one step's prompt body and Jinja wrapper from its confirmed spec — seed quality, refined later by the optimizers.
detached: opus:medium
review_gate: "The user reads the body and confirms the contract it states"
inputs:
  - what: the target step name
  - what: the target step's confirmed contract and example
  - what: the confirmed manifest
  - from: user
    what: the target model
outputs:
  - <step>/<model>.md — the prompt body
  - <step>/prompt.md — the Jinja wrapper
  - the free verify-wrapper check command in the notes
---

{% include "opus-5.md" %}

{% include "_lib/return-contract.md" %}
