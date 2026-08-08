---
summary: Read each in-scope delivered item in its own sub-agent and assemble the typed change
  table — one row per user-visible change, tied to the spec file it moves — written to the run
  record as the contract `sync-specs`, `targeting` and `record` all work from.
review_gate: "Extend, refine and confirm the change table, presented in chat from the `##
  Changes` section just written. An extension naming items that still have to be read sends the
  run back to this step, which reads only the added items and rewrites the section; confirmation
  is explicit — silence never counts, and the confirming edge stamps `changes_reviewed_at:` on
  the run record"
---

{% include "opus-5.md" %}
