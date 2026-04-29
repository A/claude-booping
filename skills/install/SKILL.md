---
name: install
description: Scaffold a booping project under ~/Claude/{project}/ and attach it to the current repo. Use when onboarding a new repo or formalizing an existing one.
argument-hint: "[project-name]"
user-invocable: true
effort: high
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Bash(ls ~/Claude/*)
  - Bash(ls ~/Claude)
  - Bash(ls -1 ~/Claude/*)
  - Bash(ls -1 ~/Claude)
  - Bash(ls -la ~/Claude/*)
  - Bash(ls -la ~/Claude)
  - Bash(pwd)
  - Bash(booping-create-project:*)
  - Bash(booping:*)
  - AskUserQuestion
---

!`booping render src/templates/skills/install.md.j2`
