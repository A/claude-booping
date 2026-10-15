---
type: idea
title: Merged OSS PRs as benchmark tasks
summary: Re-create small merged PRs from OSS repos as booping plans and score groom and develop by the repo's own tests.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: open
# also distilled from the owner's local, unpublished notes (vault/notes/ is gitignored): vault/notes/benchmark-prs.md
---

## Idea

A thin benchmark harness built from real merged PRs: each PR is a self-contained bug, small
feature or refactor, re-created as a booping plan (or a request to groom) at the PR's
parent commit and verified by the repo's tests. Selection: merged, 80-250 changed lines,
touches real test files, a clear task from the title and body, from the last two years,
on stacks that set up easily (`npm test`, `pytest`). The source lists ten — eslint,
prettier, got, axios ×2, koa, flask ×2, typer, httpx — plus four spares: eight bugs, one
feature, one refactor, so it covers grooming a bug, grooming a feature and developing a
pre-made plan.

Neither benchmark built since uses this set: `claude-booping-bench` runs cases with
injected faults on fastify and typer fixtures, and `booping-benchmarks` scores one frozen
develop sprint.

## How to check

- [clarify] The source names no check. Proposed: take one PR from the list (flask #5917),
  groom it from its title and body at the parent commit, develop the plan, and run the
  PR's own test changes against the result; if pass/fail separates a good run from a bad
  one, the set is a usable signal.
