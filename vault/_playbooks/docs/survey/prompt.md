---
summary: Report which spec-set files are missing or incomplete and which delivered work is not
  yet documented, and open the run record carrying both — the run's cheap opening, settled
  before a single expensive read happens.
review_gate: "Confirm the run scope — which spec files to refresh, which delivered items to
  cover. The gate is the runner's, taken after the return lands and asked against the run
  record's two tables; a `present` spec file may still be picked for a refresh, and an
  undocumented item may still be dropped from scope"
detached: "opus:medium"
---

{% include "opus-5.md" %}
