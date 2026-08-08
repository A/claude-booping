---
summary: Decide per confirmed change which role × surface combinations must be written and what
  each one must say — one row per destination document on the run record, which is both the
  authorisation every later write runs on and the loop's unit of parallelism.
review_gate: "Confirm the targeting plan before anything is written — this gate always fires, at
  every severity the run may be driven with. Hold it at `awaiting-targeting-confirm`, presenting
  the rows from the return; a rework answer — a destination, an assignment, or what a row must
  say — re-enters `targeting` over the same inputs plus the correction"
---

{% include "opus-5.md" %}
