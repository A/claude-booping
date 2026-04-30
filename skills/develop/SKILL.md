---
name: develop
description: Execute a groomed plan milestone-by-milestone via sub-agents. Use after /groom produces a plan file that is ready to implement.
argument-hint: [plan file path]
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Bash(booping:*)
  - Agent
  - AskUserQuestion
  - TaskCreate
  - TaskUpdate
effort: low
context: fork
---

!`booping render src/templates/skills/develop.md.j2`
