---
name: retro
description: Generate a project- and plan-specific sprint retrospective by reviewing session logs, gathering user feedback, and comparing plan vs built. No cross-project generalization or candidate lessons. Use after /develop reports a sprint DONE, or when the user explicitly asks to retro a plan.
argument-hint: [plan file path(s), space-separated; omit to pick interactively]
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash(git log *)
  - Bash(git diff *)
  - Bash(git show *)
  - Bash(git add *)
  - Bash(git commit *)
  - Bash(ls *)
  - Bash(booping:*)
  - Agent
  - AskUserQuestion
  - WebSearch
  - WebFetch
effort: high
---

!`booping render src/templates/skills/retro.md.j2`