---
type: story
title: Documentation site
summary: The public MkDocs reference builds strictly and publishes to gh-pages on push to master.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-20
status: done
priority: P2
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

As **a contributor**, I want the public reference built strictly and published on every
push to `master`, so that the docs site tracks what is shipped.

## Scenarios

1. A contributor edits a page under `documentation/` and previews it live with
   `just docs-serve`.
2. The contributor builds the site with `just docs`, which builds it
   strictly.
3. The change is pushed to `master`, and the site is published to gh-pages.

## Edge cases

- [clarify] What the strict build rejects is not named in the sources.

## Out of scope

- The plugin-internal fragments under `docs/`: they are lazy-loaded by skills, not published.

## Criteria

- `just docs` builds the site strictly and `just docs-serve` previews it live.
- `documentation/` publishes to gh-pages on push to `master`.
