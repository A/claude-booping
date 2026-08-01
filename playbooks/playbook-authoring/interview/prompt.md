---
summary: Infer the new playbook's slug, goal, success shape and artifact home from the user's description, asking only about real gaps.
detached: opus:medium
review_gate: "While Questions come back the user answers them; once complete the user refines and confirms the brief in-file"
inputs:
  - from: user
    what: the description of the desired playbook, verbatim
  - from: user
    what: answers to any previously returned questions
  - what: the brief a prior iteration wrote, if any
outputs:
  - _specs/brief.md created or updated — goal, success result, artifact home, optional wishes
  - numbered open questions, or — once complete — slug, goal, success shape and artifact home verbatim
---

{% include "opus-5.md" %}

{% include "_lib/return-contract.md" %}
