# Input — init-offer

The project is `taskflow`; the current working directory is its vault root, which lives inside the attached repo, so the project tier would sit at `specs/`. Run date: **2026-10-15**.

This run has no shell, so the `booping` commands were run for you; their outputs:

- Preamble tiers — `core` only; `project` — none: the tier is not initialised.
- `booping specs ls --tier project` — no records: `specs/` does not exist.
- `booping specs init --tier project` — not run yet; it would create `specs/`.

## Dialogue

**User:** set up specs for this project

## Context files

<file path="plans/20261010-job-retries/index.md">
---
title: "Job retries"
status: done
---

# Job retries

Failed jobs are retried three times with exponential backoff.
</file>
