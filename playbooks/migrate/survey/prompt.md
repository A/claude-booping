---
summary: >-
  Open the run: confirm a project is attached and the recorded migration id is readable;
  when work
  is uncommitted, name it, ask, and commit repo and vault on confirmation; present
  the pending set
  the rendered body carries and what each migration will do; report "already current"
  and end the
  run when the set is empty.
review_gate: >-
  The user approves applying the whole pending set — the run's only gate, taken once
  and covering
  every listed migration. The in-body commit ask is a safety confirmation resolved
  inside the step,
  not this gate. An empty pending set ends the run with nothing to approve.
reviewed_at: 20260805 09:11
---

{% include "opus-5.md" %}
