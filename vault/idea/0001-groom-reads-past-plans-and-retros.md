---
type: idea
title: Groom offers past plans and retros as context before planning
summary: Before planning, groom has a cheap researcher list past plans and retros related to the request, and reads the ones the user picks in depth.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: open
# also distilled from the owner's local, unpublished notes (vault/notes/ is gitignored): vault/notes/Improvment ideas.md
---

## Idea

Before grooming starts planning, a researcher scans old plans and retrospectives for
anything matching the request and returns only a list of related files. Groom shows the
list to the user as a checklist: read them for a stronger start, or skip them so old data
does not rot the context. On consent, a stronger researcher reads the picked files and
returns a summary — related patterns, issues the retros flagged. The source suggests haiku
for the listing pass and sonnet or opus for the summary.

Today groom intake renders a "Latest Plans" table (state, name, summary, path) from the
plan frontmatter; retrospectives are not offered, and there is no listing pass, user
checklist or summary pass.

## How to check

- [clarify] The source names no check. Proposed: take two or three past requests in this
  vault whose retros flagged an issue, run groom on each twice — once as today, once with
  the retros' summary handed in by hand — and compare whether the plan avoids the flagged
  issue and what the extra pass costs in tokens (`booping session-stats`).
