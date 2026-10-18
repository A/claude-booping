---
type: rule
title: Experiments run in stages
summary: An experiment, eval or benchmark matrix runs a cheap screen, then a shortlist, then significance for finalists only, each stage sized before launch.
created_by: claude
created_at: 2026-10-19
updated_at: 2026-10-19
status: accepted
---

## Rule

An experiment, eval or benchmark matrix runs in three stages. First a cheap screen on a small sample drops the arms that clearly lose. Then a shortlist runs the surviving arms on more cases. Significance is measured only for the finalists, and only when the decision needs it.

Before each stage the agent names its size — the number of calls and a rough cost — and what the stage decides. A stage larger than a small screen is not launched without a stated reason.

The driving protocol (`src/templates/_partials/_playbook_driving.j2`) carries this rule for every playbook, and the session-start block (`src/templates/hooks/session_start.md.j2`) for every session in a booping project, so it needs no targets.

## Follows from

- [Quality at a rational cost](../../vault/value/0012-quality-at-a-rational-cost.md) — budget goes only to arms that survive a screen; on 2026-10-19 a 280-call matrix was stopped after 104 calls, which had already shown the arms to drop.
- [Proven to work](../../vault/value/0010-proven-to-work.md) — significance is earned on the finalists, where it decides something.
