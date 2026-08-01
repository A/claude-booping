---
{}
---

[← index](../../index.md)

# manifest — Tests

## Fixtures

| Fixture                  | Requirements                                                                          |
| ------------------------ | ------------------------------------------------------------------------------------- |
| mod-review-decomposition | confirmed decomposition index (sweep + compose, simple graph) plus the two answers: target model `opus:medium`, global destination root |

## Tests

| Fixture                  | Tier    | Title          | Check logic                                                                       |
| ------------------------ | ------- | -------------- | ---------------------------------------------------------------------------------- |
| mod-review-decomposition | smoke   | FILE-AT-PATH   | manifest written at `mod-review/playbook.md`, nothing else                        |
| mod-review-decomposition | smoke   | FRONTMATTER    | name `mod-review`, title, summary, trigger present; `jinja: true`; `graph:` block |
| mod-review-decomposition | smoke   | GRAPH-LINES    | graph carries `sweep: []` and `compose: [sweep]`                                  |
| mod-review-decomposition | smoke   | BODY-LEAN      | body never lists steps, waves or gates — no `## Steps`, no `## Execution graph`   |
| mod-review-decomposition | regress | GRAPH-VERBATIM | the graph mapping is the decomposition's, copied exactly — no rename, no reorder  |
| mod-review-decomposition | regress | BODY-CARRIES   | body holds only the lead, fan-out instructions and eval-run rules; trigger in user terms, no internal step names |
