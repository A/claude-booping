---
type: value
title: Stack-agnostic core
summary: The core knows nothing about a stack or a project; specifics live in the global and the project tiers.
kind: value
created_by: owner
created_at: 2026-10-14
updated_at: 2026-10-14
---

The core knows nothing about a stack or a project; specifics live in the global and
the project tiers.

## In practice

Skills, playbooks and the specs skeleton stay generic and leave enough room to extend booping in userland: the global and the project tiers add and override — their own plan templates, playbooks, rules.

## Trade-off

[clarify] proposed: the core ships no stack-specific defaults; whoever wants them writes them in their own tier.
