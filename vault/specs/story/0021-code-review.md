---
type: story
title: Code review
summary: The code-review playbook reviews a confirmed scope, collects the human verdict and applies only approved fixes.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: done
sources: [vault/docs/_specs/features.md]
---

As **a user**, I want a confirmed scope reviewed end to end with my verdict before any
fix, so that only the fixes I approve land.

## Criteria

- Settles the scope: a delivered plan's diff, the latest commits, or a named ad-hoc
  target.
- Opens `codereviews/{dir}/{ts}.md`, carrying the reviewed plan or `plan: null`, and
  offers the vault's and global review templates.
- Returns severity-classified findings from a detached review pass.
- Collects the human verdict and applies only the approved fixes.
- Appends the closed review to the plan's `code_reviews:` history, never touching plan
  status.
