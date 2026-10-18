---
type: rule
title: Open items hold only what outlives the session
summary: An open item is filed only for work for later or a question that waits for the owner; session instructions, gate answers, policies and decisions are never items.
created_by: claude
created_at: 2026-10-19
updated_at: 2026-10-19
status: accepted
targets: [project-manager, specs]
brief: "File an open item only for what outlives the session — work for later or a question waiting for the owner; a session instruction or gate answer stays in the session, a policy goes to a rule, a decision to an ADR."
---

## Rule

An open item is filed only for what must outlive the session: work for later — a feature, a bug, a
fix, a scope question — or a question for the owner that waits for an answer.

Four kinds of ask are never items. An instruction for this session ("ping me", "wait", "do it now")
and an answer to a gate or a UAT confirmation are done by the agent or kept in the session. A
standing policy becomes a rule through the `specs` playbook. A decision becomes an ADR.

## Follows from

- [Minimal effective context](../../vault/value/0002-minimal-effective-context.md) — the open items
  stay a short index of real work; an audit of another booping project: 11 of 34 open items were
  never work (private note, not published).
- [Single source](../../vault/value/0003-single-source.md) — a policy lives in a rule and a decision
  in an ADR, not duplicated into an item.
