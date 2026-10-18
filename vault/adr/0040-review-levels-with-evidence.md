---
type: adr
title: Records carry a review level with evidence
summary: A spec record's review is its own axis beside status — none, shown, 
  discussed, accepted — and accepted carries the owner's words and where they 
  were said; it replaces the reviewed date.
created_by: claude
created_at: 2026-10-19
updated_at: 2026-10-19
status: accepted
values: [value/0008, value/0009]
rules: []
issues: []
sources: [vault/open-items/OI-0030.md, 
    vault/plans/202610190033_specs-acceptance-and-session-entry/request.md]
review: accepted
review_evidence: «Давай opus сразу… В остальном, да, все правильно» — 
  2026-10-19, chat (plan + ADR briefs)
---

## Context

A record's `reviewed:` is a date the owner sets, by hand or through the specs site's Outbox ([adr/0032](0032-specs-review-on-the-site-goes-to-the-agent.md)). It says the owner read the record, nothing more: it cannot tell a brief the owner was shown from a record discussed at length or one explicitly accepted, and it carries no evidence anyone can check. ADR acceptance does not wait for an explicit yes — the agent shows a brief and asks for objections (owner, 2026-10-19) — so how deeply a record was reviewed has to be visible on the record itself. Today no record in this repo carries `reviewed:`.

## Decision

Review is an axis separate from `status`, with four levels (owner, 2026-10-19):

1. none — the owner has not seen it;
2. `shown` — the agent showed the brief and the owner raised no objection;
3. `discussed` — there was a discussion, without an explicit yes;
4. `accepted` — the owner explicitly accepted it.

The level replaces `reviewed: {date}`. `accepted` carries evidence: the owner's words and where they were said (session, date), for example «А тут вроде ок. газ», so the acceptance can be checked (owner, 2026-10-19).

The name `shown` is the agent's proposal: it names what the agent can prove — it showed the brief — not what the owner did ("witnessed", "seen"), which the agent cannot prove.

- Frontmatter: two flat keys, `review: {level}` and `review_evidence: "{quote} — {date}, {where}"` — flat so Obsidian shows them as columns.
- An agent may set a level, only with its evidence; never `accepted` without a quote of the owner.
- `reviewed:` becomes a `booping specs check` error naming the replacement, with no migration (no known record carries it); the site Outbox line becomes `{ref} — accepted {date}`.
- `shown` is named by what the agent can prove: it showed the brief.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [Review levels with evidence](#review-levels-with-evidence) | accepted | medium | high | Shows how deep the owner's review went and lets anyone check an acceptance |
| [A new status between proposed and accepted](#a-new-status-between-proposed-and-accepted) | rejected | low | medium | Mixes the record's lifecycle with the owner's engagement |
| [Keep reviewed as a date](#keep-reviewed-as-a-date) | rejected | low | high | Cannot tell shown from discussed from accepted; no evidence |
| [The agent-decisions journal](#the-agent-decisions-journal) | rejected | low | high | Autonomous runs only, and it lives in the vault, not on the record |

### Review levels with evidence

The decision above.

- **Pros:** the depth of review is visible on the record; an acceptance can be checked against the owner's words; it fits acceptance by brief and no objection.
- **Cons:** a second axis beside `status` to keep consistent; the guide, the schemas, the checker, the site's review panel and Outbox all change; the evidence quote may carry another project's words into a public record ([rule/0033](../rule/0033-private-sources-stay-in-vault-notes.md)).
- **Complexity:** medium.
- **Reversibility:** high.

### A new status between proposed and accepted

An `assumed` status for a record the agent acts on before the owner accepts it.

- **Pros:** one field; the status already shows on every listing.
- **Cons:** mixes the lifecycle of the decision with how far the owner engaged; every type's status set changes; the existing `reviewed` field is already the axis for the owner's engagement.
- **Complexity:** low.
- **Reversibility:** medium.

### Keep reviewed as a date

Leave `reviewed: {date}` as it is.

- **Pros:** nothing to change.
- **Cons:** cannot tell a shown brief from a discussion from an explicit acceptance; carries no evidence.
- **Complexity:** low.
- **Reversibility:** high.

### The agent-decisions journal

Record each acceptance as an entry under `agent-decisions/` ([adr/0037](0037-journal-entries-are-vault-files.md)).

- **Pros:** the mechanism exists.
- **Cons:** it is written in autonomous runs only, and the entry lives in the vault, not on the record it is about.
- **Complexity:** low.
- **Reversibility:** high.

## Consequences

- The specs guide's `reviewed` entry, the list of keys a tier schema may not rename, and the site's reviewed mark from [adr/0032](0032-specs-review-on-the-site-goes-to-the-agent.md) change with the level; adr/0032 is partly reversed in its `reviewed` date.
- The specs playbook's "never set `reviewed`" line becomes the level rule above.
