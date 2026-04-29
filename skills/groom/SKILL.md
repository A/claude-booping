---
name: groom
description: Deep-research a feature, bug, or refactor and produce a specified, estimated plan with Definition of Done. Cross-validates architecture with a second model when useful. Use when the user describes a new piece of work that needs to be shaped before implementation.
argument-hint: [task description or issue reference]
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
  - Bash(ls *)
  - Bash(git log *)
  - Bash(git diff *)
  - Bash(git add *)
  - Bash(git commit *)
  - Bash(booping:*)
  - Agent
  - AskUserQuestion
  - WebSearch
  - WebFetch
effort: high
---

!`booping render src/templates/skills/groom.md.j2`