---
summary: Write one step's contract and a concrete example of its artifact — the example IS the shape the suite will pin.
agent: opus:medium
review_gate: "The user refines and confirms the spec in-file: the contract bullets and, for a markdown artifact, the example"
inputs:
  - what: the target step name
  - what: the confirmed decomposition
  - what: the original procedure description
outputs:
  - _specs/steps/<step>/index.md with the five-bullet contract and the example artifact
  - open questions only when the decomposition under-determines the step
---

{% include "opus-5.md" %}

{% include "_lib/backlink.md" %}

{% include "_lib/return-contract.md" %}
