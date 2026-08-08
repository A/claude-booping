---
title: Scope generated content to its audience — exclude internal-only changes from user-facing output
targets:
  - groom/draft-plan
retro: retrospectives/20260610-cli-logging-and-agent-namespacing.md
---

When a plan produces user-facing content (release notes, user docs, changelogs), filter by audience: include only what that audience interacts with, and drop internal-only churn (CLI internals, build plumbing, refactors users never touch). Audience-scoping is a generation-time decision, not a post-edit cleanup — spec it into the task's DoD.

**Example**: Generated release notes listed internal `booping` CLI updates users never invoke directly; the same oversharing recurred in the May-21 cli-agent docs review ("no oversharing in docs … internal details of booping cli").
