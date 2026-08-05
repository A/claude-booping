---
summary: >-
  {%- if config.core.groom_playbook.cross_review_agent -%}
  Second-model review of the written plan — the agent reads the plan file
  `plans/{slug}/index.md` and returns severity findings only, writing nothing.
  Dispose of the findings yourself before advancing: `CRITICAL` folded into the
  plan or recorded as a deferral in `## Risk register`, `RISK` folded in unless
  it reopens a call the user settled, `NOTE` at your discretion; a finding that
  reopens a settled design call is folded in nowhere and sends the run back to
  `drafting`.
  {%- else -%}
  Skipped — no `core.groom_playbook.cross_review_agent` configured. Advance past
  `cross-reviewing` with nothing reviewer-flavoured in the plan: no findings
  list, no severity vocabulary, no risk register.
  {%- endif -%}
detached: "{{ config.core.groom_playbook.cross_review_agent or '' }}"
review_gate: null
---

{% if config.core.groom_playbook.cross_review_agent %}{% include "opus-5.md" %}{% else %}
No `core.groom_playbook.cross_review_agent` is configured. Perform nothing: post no findings, add no risk
register, and advance the run past `cross-reviewing` unchanged.
{% endif %}
