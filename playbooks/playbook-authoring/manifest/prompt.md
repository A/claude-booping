---
summary: Write the playbook's manifest early — identity, trigger, and the confirmed graph verbatim; body as a lean guide the renderer completes.
detached: sonnet:medium
review_gate: "The user confirms name, trigger, graph, target model and destination root before any per-step file is written"
inputs:
  - what: the confirmed decomposition — graph verbatim, machines translated verbatim when designed
  - from: user
    what: the target model (default opus:medium)
  - from: user
    what: the destination root
outputs:
  - playbook.yaml — graph plus state machines when present
  - playbook.md — identity and lean guide body
---

{% include "opus-5.md" %}

{% include "_lib/return-contract.md" %}
