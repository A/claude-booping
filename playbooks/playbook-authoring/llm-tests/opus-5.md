# Pin one step's test rows

The input names the target step and carries its confirmed contract and example, plus answers
to any offers you returned earlier. Produce the step's **test plan**: EVERY check its suite
will run, pinned as a table while it is cheap to review — a row is one glance, a written
assert or rubric is not. The tier column decides the implementation later: smoke rows become
script asserts, regress rows become judge rubrics.

Grow the rows minimally: success-case rows first, derived from the confirmed example's
structure. Trap rows are never presumed — OFFER them in Questions, each named with the
failure it would provoke and the fixture it would need, and write them only when the user
picks them.

A row is concrete because its fixture is known: expected values go inline
(`written at release-notes/_specs/brief.md`), never "should work" claims — phrase each check
so a known-bad artifact fails it.

## The file to write

`<name>/_specs/steps/<step>/test-plan.md`:

- no frontmatter of your own — harness stamps may exist on update; preserve them
- the single H1, right after the backlink: `# <step> — Tests`
- `## Fixtures` — table: Fixture | Requirements (very compact; for a trap, the failure it
  provokes). ONE happy-path fixture is the norm; a second only when the step's happy-path
  contract genuinely cannot be exercised on one input. Fixtures may not exist yet — the
  fixtures step materializes exactly what this file describes.
- `## Tests` — table: Fixture | Tier | Title | Check logic (compact, one line). A literal
  `|` inside a cell — a regex alternation, say — must be escaped as `\|` even inside
  backticks, or it splits the cell.
- no other sections: the spec's remaining facts (gate, contract, example) stay in the spec —
  the plan is fixtures and tests alone. The file is a clean artifact: questions (trap-row
  offers) never live in it, they go in your own harness return below.

## Return format

```
## Changed:
- [CREATED] <name>/_specs/steps/<step>/test-plan.md

## Questions:
1. Trap rows worth adding? (a) <TITLE> on <fixture> — provokes <failure>; (b) …; (c) none.
```

`## Questions:` empties once the step's rows are settled.
