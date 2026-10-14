---
type: story
title: Documentation site
summary: The public MkDocs reference builds strictly and publishes to gh-pages on push to master.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: done
sources: [vault/docs/_specs/features.md]
---

As **a contributor**, I want the public reference built strictly and published on every
push to `master`, so that the docs site tracks what is shipped.

## Criteria

- `just docs` builds the site strictly and `just docs-serve` previews it live.
- `documentation/` publishes to gh-pages on push to `master`.
