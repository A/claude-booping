---
summary: Append every user decision the runner relays to _specs/DECISIONS.md, timestamped; bootstrap the file on first call.
agent: haiku:low
review_gate: "none — mechanical log; the user narrows the file later"
inputs:
  - from: runner
    what: zero or more user decision summaries, relayed verbatim
outputs:
  - _specs/DECISIONS.md created or appended, one timestamped line per decision
  - the recorded count or the bootstrap note
---

{% include "haiku-4-5.md" %}

{% include "_lib/return-contract.md" %}
