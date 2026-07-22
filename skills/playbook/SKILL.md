---
name: playbook
description: "Run a user-authored playbook from the vault: a multi-step guided procedure. Lists available global and local playbooks, selects one by trigger, and drives its steps in order — spawning per-step sub-agents or running inline, pausing at review gates."
argument-hint: [playbook name or trigger]
user-invocable: true
allowed-tools:
  - Read
  - Bash(booping:*)
  - Agent
  - AskUserQuestion
effort: medium
---

!`booping render src/templates/skills/playbook.md.j2`
