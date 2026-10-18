# Request

Items: OI-0029, OI-0030, OI-0031, OI-0032 (owner, 2026-10-18/19, one change).

> project manager - давай все это организуй чтобы было в коде и спеках.

The items carry the owner's words verbatim; the session's settled decision list is below.

## Task type

`feature` — new behaviour for users of booping: an ADR brief with an objection window, review levels with evidence on records, a scoring pass on new ADRs, a session-start entry into playbooks. Not `bug`: nothing shipped diverges from its spec — the gaps are missing mechanics, not defects (the lost scoring idea was never built). Not `refactoring`: user-visible behaviour changes in every part.

## Problem

A session working on a booping project outside a playbook never sees the core rules (0032/0033) nor the specs guidance: they reach an agent only through `render-playbook`, agent and skill bodies. On 2026-10-18 a session in another booping project wrote two ADRs as `accepted` and dispatched developers without showing the owner the decision, its alternatives or the ADR it partly reversed; this session proposed a new status without checking the existing `reviewed` field — same cause. Today:

- an ADR goes to `accepted` with no brief to the owner and no chance to object;
- `reviewed` is one date the owner sets on the site; it cannot say "shown, not objected" vs "discussed" vs "explicitly accepted", nor carry the evidence;
- nothing checks a new ADR's alternatives are real (yesterday's audit found filler alternatives systemic; only guide line 47 shipped);
- `SessionStart` injects nothing in a booping project, so no session is told which playbook its work belongs to.

## Clarifications and Decisions

1. Accepting an ADR does not wait for a "yes": the agent shows a brief and asks for objections; none → go on. (user)
2. Brief format A+B: a table of the chosen and rejected options with the reason, plus the key points of the chosen decision so nothing important is confirmed unseen, the ADRs/values it touches or reverses, and what the agent decided alone. (user + proposal)
3. The objection ask is worded gently — not "No objections — I go on". (user)
4. Review levels, an axis separate from `status`: none / `shown` / `discussed` / `accepted`, replacing `reviewed`. (user, names `shown` proposal)
5. `accepted` carries evidence of the confirmation — the owner's words and where — so it can be checked. (user)
6. Logic of what an ADR is, how it is made and checked lives in core; project behaviour and overrides use the existing mechanics (tier `_schemas/` overlay, targeted rules). (user)
7. A cheap context-free subagent scores a new ADR's text in the `specs` step when an ADR is recorded — real alternatives, not the decision's negation, the cheap options weighed — built on yesterday's audit. (user)
8. `SessionStart` in a project with a `.booping` marker injects when to call playbooks (project work a playbook fits goes through it), the rendered playbook table, and the agent offers the right playbook in dialogue; the manager is the default offer. (user)
9. The manager is not loaded on every session start; a project that wants it at once says so in its CLAUDE.md. (proposal — owner: "подумай")
10. The entry decision and the review levels are recorded as ADRs. (user: "Пахнет ADR")
