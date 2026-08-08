---
{}
---

[← index](../../index.md)

# step-suite — Tests

## Fixtures

| Fixture       | Requirements                                                                            |
| ------------- | --------------------------------------------------------------------------------------- |
| compose-ready | confirmed compose spec, confirmed test plan (2 smoke + 1 regress row on `small-module`), the shipped prompt body, and the compact suite conventions; target `compose` |

## Tests

| Fixture       | Tier    | Title           | Check logic                                                                                 |
| ------------- | ------- | --------------- | -------------------------------------------------------------------------------------------- |
| compose-ready | smoke   | TWO-FILES       | `mod-review/compose/promptfooconfig.yaml` and `tests.yaml` written; `_fixtures/*` allowed   |
| compose-ready | smoke   | CONFIG-SHAPE    | config names the body as labeled prompt, the provider with `mode: step`, the shared grader `defaultTest`, `tests: file://tests.yaml` |
| compose-ready | smoke   | TESTS-SHAPE     | every case carries `metadata` (playbook, step, fixture, tier); smoke cases use `javascript` asserts, regress cases `llm-rubric` |
| compose-ready | smoke   | NOTES-COMMANDS  | the return's Notes propose the `just eval-smoke` / `just eval-regress` commands — proposed, not run |
| compose-ready | regress | SUITE-FROM-PLAN | one smoke case pinning the example-derived contract; one rubric per regress row, NAMED after its title, on the row's fixture |
