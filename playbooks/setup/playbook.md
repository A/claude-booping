---
name: setup
title: Setup
summary: Take a repo from any starting state to a working booping project — machine-level config, then project-level vault — in one driven conversation.
trigger: setting booping up on this machine for the first time; attaching or initializing this repo as a booping project
inline_steps: true
jinja: true
reviewed_at: 20260804 08:47
---
Setup takes a repo from any starting state to a working booping project: a booping config with a resolved `home_dir` at the machine level, then a scaffolded vault, `.booping` marker and, for a repo-local vault, a home-dir symlink at the project level. Every phase already satisfied on entry is detected and skipped rather than redone, so a re-run on a fully set-up project reports the state instead of changing it. The run is ephemeral — it lives in this one conversation, has no persisted state and nothing to resume — and a cancelled run leaves the machine and the repo untouched.

{% include "_partials/playbook_shared_instructions.md" %}
