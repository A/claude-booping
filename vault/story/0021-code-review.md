---
type: story
title: Code review
summary: The code-review playbook reviews a confirmed scope, collects the human verdict and applies only approved fixes.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-20
status: done
priority: P1
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

As **a user**, I want a confirmed scope reviewed end to end with my verdict before any
fix, so that only the fixes I approve land.

## Scenarios

1. The user runs `/playbook code-review`; `scope` offers every `done` plan with its
   review history, the latest commits, or a named target, and the user confirms one.
2. The run opens the review file under `codereviews/` and offers the review templates.
3. `review` returns severity-classified findings from a detached pass; `present` writes
   them and asks the user's verdict on each.
4. `resolve` applies the approved fixes, records every finding as applied, delegated or
   dropped, appends the review to the plan's `code_reviews:` and commits the vault.

Re-review: the user reviews the same plan again after fixes; it is a new, separately
recorded run and the plan stays in the queue.

## Edge cases

- An ad-hoc scope with no plan: the review carries `plan: null` and closing appends nothing to any plan.
- A stopped review: it resumes from the review file's own status.
- The user overrules a finding's severity or rejects a fix: the correction is logged verbatim under `corrections/`.

## Criteria

- Settles the scope: a delivered plan's diff, the latest commits, or a named ad-hoc
  target.
- Opens `codereviews/{dir}/{ts}.md`, carrying the reviewed plan or `plan: null`, and
  offers the vault's and global review templates.
- Returns severity-classified findings from a detached review pass.
- Collects the human verdict and applies only the approved fixes.
- Appends the closed review to the plan's `code_reviews:` history, never touching plan
  status.
