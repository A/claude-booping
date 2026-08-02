---
summary: Second-model review of the written plan — requires the plan file
  `plans/{slug}/index.md`, which the reviewing agent reads; it returns severity
  findings only and writes nothing. Skip the step when the project configures no
  `cross_review` agent.
detached: "{{ config.cross_review.agent }}"
review_gate: null
---

{% include "opus-5.md" %}
