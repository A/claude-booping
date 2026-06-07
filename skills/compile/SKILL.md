---
name: compile
description: "Static-generation entrypoint. Regenerates the native wrapper agents for every type: cli agent into repo-local .claude/agents/ and tells you to restart Claude Code to apply. Run after changing cli-agent config."
user-invocable: true
allowed-tools:
  - Bash(booping:*)
effort: low
---

!`booping render src/templates/skills/compile.md.j2`
