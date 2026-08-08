---
title: Bound an agent briefing's return contract to harness-needed output only
targets:
  - groom/draft-plan
retro: retrospectives/20260610-cli-logging-and-agent-namespacing.md
---

Every agent briefing must state the exact shape the agent returns, scoped to only what the orchestrator needs (e.g. "final reply MUST contain ONLY the list of changed files"). Delegation is lossy: an unbounded return contract lets the agent emit surplus prose that rots orchestrator context. When folding DoD + Verify into tasks, bound the return shape there so /develop's briefings inherit it.

**Example**: Mid-sprint the user had to constrain the agent ("agent just need to return list of changed files, nothing else") because the briefing never bounded the return shape; the fix codified an `OUTPUT_GUIDE`.
