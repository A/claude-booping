---
summary: For novel or non-obvious work, gather current best practice, competing 
  approaches and known pitfalls with sources; return a skip note when the work 
  is well-trodden.
detached: opus:medium
review_gate: null
inputs:
- what: the confirmed framing — the restated problem, the task type, and the 
    scope boundaries the user confirmed
- what: the uncertainty signals that framing carries — unfamiliar surfaces, new 
    or upgraded dependencies, approaches with no obvious precedent
outputs:
- _runs/groom/{slug}/research-web.md — verdict first (`Researched` or `Skipped` 
  plus one line of rationale), then on the researched path the candidate 
  approaches with their trade-offs, the pitfalls that constrain the design, and 
  a source table carrying a URL and a retrieval date per claim; written on both 
  paths
- the harness return — the Changed entry annotated with the verdict and its 
  counts, plus Notes carrying the recommendation and the pitfall count, or the 
  skip rationale
reviewed_at: 20260731 19:32
---

{% include "opus-5.md" %}
