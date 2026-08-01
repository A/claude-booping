---
summary: Restate the request, classify the task type, set the scope boundaries 
  and challenge the scope; create the plan file with its identity frontmatter, 
  or adopt a parked plan in place.
detached: fable:high
review_gate: "The user answers every scope-challenge question and confirms the task
  type and the scope boundaries — explicit confirmation, silence never counts; answers
  that change the task type, the restated problem or a boundary send the step back
  for another pass"
inputs:
- from: user
  what: the request to groom, verbatim
- from: user
  what: the answers to the scope-challenge questions the previous pass returned 
    — on a re-run only
- from: the attached project
  what: the task-type catalogue and the grooming guidance for the type that 
    matches
- from: the attached project
  what: the project's own conventions
- from: the vault
  what: the plans already filed, parked ones included — title, type and status 
    of each
outputs:
- "_runs/groom/{slug}/intake.md — the framing document: request verbatim, restated
  problem, task type with its rationale, scope boundaries, scope-challenge questions;
  no frontmatter authored"
- "plans/{slug}.md — identity frontmatter only and no body, or the parked plan the
  user named updated in place"
- "the chosen task type and the resolved plan path, reported in the harness return"
- "the scope-challenge questions, numbered and answerable in one line each — empty
  on the re-run whose answers settle the framing"
reviewed_at: 20260731 19:32
---

{% include "fable-5.md" %}
