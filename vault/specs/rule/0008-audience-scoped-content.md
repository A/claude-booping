---
type: rule
title: Generated content is scoped to its audience
summary: User-facing output — release notes, user docs, changelogs — includes only what that audience touches; the audience filter is specced into the task's DoD.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
targets: [groom/draft-plan]
brief: "For user-facing content (release notes, docs, changelogs), put the audience filter into the task's DoD: only what that audience touches, no internal churn."
sources: [vault/_lessons/0006_audience-scoped-content.md, vault/retrospectives/20260610-cli-logging-and-agent-namespacing.md]
---

## Rule

When a plan produces user-facing content (release notes, user docs, changelogs),
the content includes only what its audience interacts with; internal churn — CLI
internals, build plumbing, refactors the audience never touches — is left out.
Audience scoping is decided at generation time and written into the task's DoD,
not cleaned up in a post-edit.

## Follows from

- [Retro: CLI logging and agent namespacing](../../retrospectives/20260610-cli-logging-and-agent-namespacing.md)
  — generated release notes listed internal `booping` CLI changes users never
  invoke; the same oversharing recurred in a docs review.
