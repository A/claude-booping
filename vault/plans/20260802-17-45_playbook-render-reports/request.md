# Framing brief

## Request

> i want to add into justfile a command that renders each existing core playbook into playbooks/<playbook>/reports/output.md, and add it into claude.md as instruction to do it after playbook updates, so any updates/prs will contain the output of the playbook, so i can review it.

## Task type

`feature` — new developer-facing capability (a justfile recipe + a documented convention). Not `bug`: nothing diverges from expected behavior today. Not `refactoring`: it adds a new artifact and workflow step, no internal restructure of existing code.

## Problem

Core playbooks (`playbooks/develop/`, `playbooks/groom/`, `playbooks/playbook-authoring/`) are authored as manifests + step dirs; their composed render (`booping render-playbook <name>`) is only visible by running the CLI. PRs touching playbook sources show template diffs, not the rendered procedure, so review of the actual output requires a local render. The change: a `just` recipe renders every core playbook to a committed report file per playbook, and CLAUDE.md instructs running it after playbook edits — making rendered output part of every playbook PR diff.

## Clarifications and Decisions

- Reports live at `playbooks/{name}/_reports/output.md` — underscore prefix avoids the orphan-step warning a plain `reports/` dir would trigger.
- Full render, lessons included — report shows exactly what a run sees; lesson-driven diff churn accepted.
- Dynamic enumeration: recipe loops over `playbooks/*/playbook.md`, skipping `_`-prefixed dirs.
- No post-implementation prose-reshape milestone needed.
- Deterministic render required: date/time, commit sha, and any other run-varying context must be pinnable so a re-render with no source change produces no diff.
