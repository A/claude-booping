---
name: help
description: Show what booping is, the available commands, and how to use them. Use when the user asks for help, wants a tour of the plugin, or is onboarding.
argument-hint: "[topic: skills | agents | layout | workflow | extensions]"
user-invocable: true
effort: low
allowed-tools:
  - Read
  - Bash(ls *)
  - Bash(booping:*)
---

!`booping render src/templates/skills/help.md.j2`
