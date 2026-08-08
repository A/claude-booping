---
{}
---

[← index](../../index.md)

# step-spec — Tests

## Fixtures

| Fixture                    | Requirements                                                                      |
| -------------------------- | --------------------------------------------------------------------------------- |
| compose-from-decomposition | confirmed mod-review decomposition plus the original procedure description; target `compose` |

## Tests

| Fixture                    | Tier    | Title             | Check logic                                                                             |
| -------------------------- | ------- | ----------------- | ---------------------------------------------------------------------------------------- |
| compose-from-decomposition | smoke   | FILE-AT-PATH      | spec written at `mod-review/_specs/steps/compose/index.md`, no frontmatter of its own authored |
| compose-from-decomposition | smoke   | SECTIONS          | H2s Contract, Example artifact, Return Format — in order; backlink to the index present |
| compose-from-decomposition | smoke   | FIVE-BULLETS      | Contract holds the five bold bullets: Needs, Value, Output files, Harness return, Review gate |
| compose-from-decomposition | regress | CONTRACT-GROUNDED | bullets reflect the compose row — artifact `_review/review.md`, gate on findings; example is a compact fenced review report |
| compose-from-decomposition | regress | NEEDS-BLIND       | Needs is information only — no upstream step names, no artifact paths                   |
