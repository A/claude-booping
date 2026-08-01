---
summary: Design the playbook's persisted state machines from decompose's tier verdict — or skip on ephemeral — as a States chart the manifest translates verbatim.
detached: opus:high
review_gate: "The user confirms machine granularity — statuses, gates, hooks, artifacts — in-file and re-confirms the index"
inputs:
  - what: the confirmed decomposition — graph and Steps table
  - what: the state-machine persistence-tier verdict, or the user's override of it
  - what: the brief
outputs:
  - _specs/states.md with the machine tables, and the index re-opened linking it — or no file change on an ephemeral verdict
  - machine count and tier, or the skip note
---

{% include "opus-5.md" %}

{% include "_lib/return-contract.md" %}
