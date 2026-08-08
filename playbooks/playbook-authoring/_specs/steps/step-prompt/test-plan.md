---
{}
---

[← index](../../index.md)

# step-prompt — Tests

## Fixtures

| Fixture               | Requirements                                                                  |
| --------------------- | ----------------------------------------------------------------------------- |
| compose-spec-manifest | confirmed compose spec plus confirmed mod-review manifest; target model `opus:medium`; target `compose` |

## Tests

| Fixture               | Tier    | Title         | Check logic                                                                            |
| --------------------- | ------- | ------------- | --------------------------------------------------------------------------------------- |
| compose-spec-manifest | smoke   | TWO-FILES     | `mod-review/compose/opus-5.md` and `mod-review/compose/prompt.md` written, nothing else |
| compose-spec-manifest | smoke   | BODY-CLEAN    | the body carries no frontmatter and no Jinja tokens                                    |
| compose-spec-manifest | smoke   | WRAPPER-SHAPE | wrapper frontmatter has `name: compose`, `agent: opus:medium`, `review_gate`; body is exactly the include of `opus-5.md` |
| compose-spec-manifest | smoke   | NOTES-VERIFY  | the return's Notes carry the free `just verify-wrapper` check                          |
| compose-spec-manifest | regress | BODY-COMPLETE | body states what the step receives, the file to write with a document contract matching the confirmed example, and the harness return |
