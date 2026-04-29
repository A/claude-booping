---
name: learn
description: Extract lessons from a retrospective and fold improvements into project-local skill/agent extensions under _booping/. Use after /retro writes a retrospective.
argument-hint: [retrospective file path]
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash(ls *)
  - Bash(test *)
  - Bash(git add *)
  - Bash(git commit *)
  - Bash(grep *)
  - Bash(booping:*)
  - AskUserQuestion
effort: high
---

!`booping render src/templates/skills/learn.md.j2`