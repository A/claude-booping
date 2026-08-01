---
summary: Settle architecture, pattern choice, data / API / config surface 
  changes, alternatives and risks; surface every trade-off the user must call.
detached: opus:high
review_gate: "The user iterates on the design — rejecting a call, asking for another
  alternative — and confirms it in-file before any plan body is written; every trade-off
  call is settled or its recommendation explicitly taken, an unanswered call blocks
  the gate"
inputs:
- what: the confirmed framing — the restated problem, the task type, the scope 
    boundaries, and the user's answers to the scope-challenge questions
- what: the blast radius — the files, modules, integrations and external 
    surfaces the work touches, with the prior art and the conventions already in
    play
- what: the current external practice for this work — approaches, trade-offs and
    pitfalls with their sources — or the note that the work is well-trodden and 
    none was gathered
- from: user
  what: on a loopback into design, the objection or change request and the 
    design call it targets
outputs:
- _runs/groom/{slug}/design.md — H1 `# design — {slug}` then Approach, Surface 
  changes, Alternatives, Trade-offs, Risks; no frontmatter authored, revised in 
  place on a loopback
- one numbered question per open trade-off call, empty when the design leaves 
  none
reviewed_at: 20260731 19:32
---

{% include "opus-5.md" %}
