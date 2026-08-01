---
{}
---

[← index](../../index.md)

# llm-tests — Tests

## Fixtures

| Fixture      | Requirements                                                             |
| ------------ | ------------------------------------------------------------------------ |
| compose-spec | confirmed compose spec — five-bullet contract plus fenced example artifact; target `compose` |

## Tests

| Fixture      | Tier    | Title             | Check logic                                                                                    |
| ------------ | ------- | ----------------- | ----------------------------------------------------------------------------------------------- |
| compose-spec | smoke   | FILE-AT-PATH      | plan written at `mod-review/_specs/steps/compose/test-plan.md`, backlink present, no frontmatter of its own authored |
| compose-spec | smoke   | TABLES            | `## Fixtures` table (Fixture, Requirements) and `## Tests` table (Fixture, Tier, Title, Check logic) |
| compose-spec | smoke   | TIER-ENUM         | every Tier cell is `smoke` or `regress`                                                        |
| compose-spec | smoke   | TRAPS-OFFERED     | the return's Questions section offers candidate trap rows — at least one entry                 |
| compose-spec | regress | ROWS-FROM-EXAMPLE | smoke rows pin the example's structure; success-case rows only — no trap row written unasked   |
| compose-spec | regress | ROWS-CONCRETE     | each row's check logic carries its expected values inline, phrased so a known-bad artifact fails |
