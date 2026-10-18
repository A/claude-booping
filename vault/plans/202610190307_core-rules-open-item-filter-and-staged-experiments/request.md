# Request

## Request

> groom OI-0033 ({vault}/open-items/OI-0033.md), OI-0034 ({vault}/open-items/OI-0034.md)

Local absolute paths in the quote are shortened to `{vault}/` (rule/0033 — Private sources stay in vault/notes).

The owner's own words and the decisions settled with them live in the items: [OI-0033](../../open-items/OI-0033.md) — "Open items: only what outlives the session; ids in chat carry a short summary"; [OI-0034](../../open-items/OI-0034.md) — "Experiments run in stages: a cheap screen first, then a shortlist, then significance".

## Task type

`feature` — the change adds agent behaviour every user's runs get (two new core rules, a narrowed project-manager intake filter, an id-with-title convention in the driving protocol). Not `bug`: today's intake does what its prose says ("each distinct ask, asides included"); the owner wants a different behaviour, not a defect fixed. Not `refactoring`: user-visible behaviour changes — which asks become items, how ids appear in chat, how experiments are launched.

## Problem

Today the project-manager `intake` step files every distinct ask as an open item, asides included, so in-session instructions ("ping me at the release"), gate answers, policies and decisions land in `open-items/` and bury the real work; ids said in chat (OI, ADR, rule) come bare, so the owner cannot tell what they name. Separately, agents launch experiment and eval matrices whole (a 280-call run), spending budget on arms a ten-case screen would have dropped. After the change: only what must outlive the session becomes an item, every id in chat carries its short title, newly filed items are listed as `Создан OI-NNNN: {title}`, and experiments run cheap screen → shortlist → significance, each stage sized and justified before launch.

## Clarifications and Decisions

- Scope is exactly the decisions recorded on OI-0033 (1–7) and OI-0034 (1–3), settled with the owner on 2026-10-19 — no further scope questions (autonomous run).
- One plan for both items: both are core-rule additions on the same surfaces (`specs/rule/`, the driving protocol), small enough together for one sprint.
- OI-0033's audit of this project's open items is not in this plan — the decisions already turned the audit into rules; closing stale items is specs/project-manager work, not development (proposal).
- The OI-0034 rule is untargeted; like 0032/0033 it reaches runs through the driving protocol (proposal, following OI-0033 decision 6).
