---
summary: Check every external reference the plan names — package versions, image
  tags, API endpoints, CLI flags, config options — against current upstream docs
  and correct what is wrong.
detached: opus:medium
review_gate: null
inputs:
- what: every external reference the confirmed plan names — package and library 
    versions, container image tags, API endpoints and their payload shapes, CLI 
    commands and flags, config options and their defaults — each with the place 
    in the plan that names it
- from: the vendors' own documentation, registries and changelogs, retrieved 
    during the run
  what: the current upstream documentation for each of those references, read 
    now rather than recalled
outputs:
- _runs/groom/{slug}/references.md — H1 `# references — {slug}`, then the 
  verdict (`Verified`, `Corrected` or `Nothing to check`) with its checked / 
  corrected / unverifiable counts, the checked table carrying per reference 
  where the plan names it, what it claims, what upstream says, the verdict and 
  the dated source, then the corrections and the unverifiable references when 
  there are any; written on every path
- plans/{slug}.md — each correction folded in as a literal replacement at every 
  occurrence, nothing else touched; untouched on a clean pass
- the harness return — the Changed entries annotated with their counts, plus 
  Notes carrying every correction that changes the shape of the work and every 
  unverifiable reference, for the approval summary
reviewed_at: 20260731 20:19
---

{% include "opus-5.md" %}
