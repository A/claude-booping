---
type: rule
title: Graph and render problems are reported in band, never as crashes
summary: A graph or render problem surfaces as a STOP or Note notice in the rendered output at exit 0, never as a crash.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md, CLAUDE.md]
---

## Rule

A problem in a playbook graph or a render surfaces in the rendered output as a
`**STOP — tell the user:**` or `**Note — tell the user:**` notice, with exit 0.
It never surfaces as a crash.

## Follows from

- [Guides to the goal](../value/0013-guides-to-the-goal.md) — the user is told what is wrong
  inside the run instead of facing a stack trace.
