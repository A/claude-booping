---
type: rule
title: Every diff is reviewed in Plannotator, never in chat
summary: In this project the code-review human step always runs through the plannotator-reviewer agent; a missing agent or a dead surface stops the run, never falls back to chat.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: retired
targets: [code-review]
brief: "Hand every finding set, even an empty one, to plannotator-reviewer instead of printing findings in chat; its reply is the human's review. Agent missing or SURFACE UNAVAILABLE: stop and tell the user."
sources: [vault/_lessons/0012_review_every_diff_in_plannotator.md, vault/config.yaml]
---

## Rule

Retired on 2026-10-14: the owner deactivated the Plannotator review for now and may
revisit it. While it was accepted: this project reviews every diff in Plannotator;
the browser review replaces presenting findings in chat.

- Once findings are computed, they are handed to the `plannotator-reviewer` agent
  with the diff ref (a PR URL, or a token such as `HEAD` for the working tree), the
  repo path, and every finding as `file:lineStart[-lineEnd] · side · severity ·
  snippet · proposed-fix · rationale`. The review is launched even with zero
  findings, so the human sees the clean diff.
- The agent's reply is the human's feedback, and the run continues from it.
- If the agent is not among the available agents, the run stops and tells the user
  to install `~/.claude/agents/plannotator-reviewer.md` and register it in the
  vault config, then restart Claude Code.
- If the agent returns `SURFACE UNAVAILABLE`, the run reports exactly what failed
  and stops; it never substitutes a chat review.


## Follows from

- [Effective human review](../value/0008-effective-human-review.md) — the human reviews the diff
  inline with the findings, where it is convenient for them; the owner's preference
  for this project.
- [Lesson 0012](../../_lessons/0012_review_every_diff_in_plannotator.md) — the
  source names no retro.
