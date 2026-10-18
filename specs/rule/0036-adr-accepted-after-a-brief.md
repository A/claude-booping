---
type: rule
title: An ADR is accepted after a brief
summary: An ADR is drafted proposed and accepted only after the owner was shown its brief and given a window to object; the answer sets the review level with its evidence.
created_by: claude
created_at: 2026-10-19
updated_at: 2026-10-19
status: accepted
targets: [specs]
brief: "Draft an ADR `proposed`; before accepting it show the brief — the options table, the key points, what it touches or reverses, what you decided alone, the alternatives score — and ask for objections. No objection → accepted with `review: shown`; an explicit yes → `review: accepted` with the owner's words quoted; a discussion → `review: discussed`; an objection → back to the draft. Autonomous: log the brief as an agent decision, no `review` key."
---

## Rule

An ADR is never accepted silently. The agent drafts it `status: proposed` and shows the owner a brief in the specs guide's locked shape: the chosen and rejected options with the reason, the chosen decision's key points, what the decision touches or reverses, what the agent decided alone, and the alternatives score. It ends with an objection ask, not a request for a yes: no objection lets the run go on. The answer sets the record's `review` level with its `review_evidence` — `shown` when the owner raised nothing, `accepted` only with the owner's words quoted, `discussed` when the owner engaged and agreed — and an objection sends the ADR back to the draft. An autonomous run logs the brief as an agent decision instead and accepts the ADR with no `review` key, so what the agent settled alone stays visible (owner, 2026-10-19).

## Follows from

- [Effective human review](../../vault/value/0008-effective-human-review.md) — the brief puts the alternatives, the key points and any reversal where the owner reads them, instead of inside the record.
- [Adjustable control](../../vault/value/0009-adjustable-control.md) — the owner can stop a decision without having to approve every one; the level records how far they engaged.
