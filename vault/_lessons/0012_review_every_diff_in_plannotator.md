---
title: Review every diff in Plannotator, never in chat
targets:
  - code-review
---

This project reviews **every** diff in Plannotator, never in chat — the browser review replaces the chat-only findings phase (g).

`plannotator-reviewer` is a required agent: if it is **not** in the Available Agents table, its global agent file is missing — stop and tell the user to install `~/.claude/agents/plannotator-reviewer.md` and register it under `skills.code-review.agents.plannotator-reviewer` in the vault `config.yaml`, then restart Claude Code (see `documentation/integrating-external-agents.md`). Do not fall back to a chat-only review.

After findings are computed (phases (e)–(f)), do **not** print them grouped in chat. Instead:

1. Delegate to `plannotator-reviewer` via the `Agent` tool (`subagent_type="plannotator-reviewer"`). Brief it with:
   - the resolved diff ref (PR URL, or a non-URL token like `HEAD` for the working tree),
   - the repo path to run in,
   - every finding as `file:lineStart[-lineEnd] · side · severity(BLOCKER|SUGGESTION|NIT) · snippet · proposed-fix · rationale`.

   Always launch the review — even with **zero** findings, hand over an empty finding set so the human can review the clean diff in the browser.
2. The agent's **returned message is the human's feedback** (the Agent-tool result). Phase (h) proceeds from that text directly — treat it as the user's review response. No special variable or format.
3. If the agent returns a `SURFACE UNAVAILABLE` signal (binary absent / server down / seed failed), **surface the failure and stop** — report exactly what failed so the user can fix the transport. Do not silently substitute a chat-only review.
