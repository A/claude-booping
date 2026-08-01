---
status: spec-ing
---

# llm-tests

[← index](../../index.md)

## Contract

- **Needs** — the target step name; the target step's confirmed contract and example;
  answers to any previously returned offers.
- **Value** — EVERY check the step's suite will run, pinned as a table while it is cheap to
  review: a row is one glance, a written assert or rubric is not. The tier column decides the
  implementation: smoke rows become script asserts, regress rows become judge rubrics. A row
  is concrete because its fixture is known — expected values go inline (`written at
  release-notes/_specs/brief.md`), never "should work" claims. Grown minimally: success-case
  rows first; trap rows are never presumed — they are OFFERED, each named with the failure it
  would provoke, and written only when the user picks them.
- **Output files** — `[CREATED] <name>/_specs/steps/<step>/test-plan.md`, two sections.
  `## Fixtures`: a table — fixture | requirements (very compact; for a trap, the failure it
  provokes). ONE happy-path fixture is the norm; a second only when the step's happy-path
  contract genuinely cannot be exercised on one input. `## Tests`: the table —
  fixture | tier | title | check logic (compact, one line, phrased so a known-bad artifact
  fails it). Fixtures may not exist yet — the fixtures step materializes exactly what this
  file describes. The file carries no frontmatter of its own and opens with a backlink to
  the decomposition index.
- **Harness return** — `## Changed:` list and `## Questions:` — after the success rows, one
  question offering candidate trap rows with the fixture each would need; empty once the
  step's rows are settled.
- **Review gate** — the user extends, narrows or strikes the rows, then confirms them.

## Example artifact

```markdown
[← index](../../index.md)

# compose — Tests

## Fixtures

| Fixture      | Requirements                                              |
| ------------ | --------------------------------------------------------- |
| small-module | two-file module, one seeded defect (token expiry uses `<`) |

## Tests

| Fixture      | Tier    | Title        | Check logic                                  |
| ------------ | ------- | ------------ | -------------------------------------------- |
| small-module | smoke   | SECTIONS     | Findings and Verdict sections present        |
| small-module | smoke   | KNOWN-DEFECT | the seeded `<` defect is among the findings  |
| small-module | regress | GROUNDED-FIX | each finding's fix sketch matches its defect |
```

## Return Format

```markdown
## Changed:
- [CREATED] mod-review/_specs/steps/compose/test-plan.md — 3 success rows

## Questions:
1. Trap rows worth adding? (a) NO-FALSE-POSITIVE on a new `noisy-module` fixture — provokes
   reporting stale TODOs; (b) EMPTY-INPUT on `empty-module` — provokes invented findings;
   (c) none for now.
```
