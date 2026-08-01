---
summary: Materialize the fixtures the confirmed test rows name, as real files the step's suite runs against.
agent: opus:medium
review_gate: "The user reads the fixture files themselves and confirms the set"
inputs:
  - what: the target step name
  - what: the target step's confirmed contract and example
  - what: the step's confirmed test plan
  - from: user
    what: answers to any previously returned questions
outputs:
  - <step>/_fixtures/* — one file per fixture the confirmed rows name
  - questions only when a row's fixture is ambiguous to materialize
---

{% include "opus-5.md" %}

{% include "_lib/return-contract.md" %}
