---
{}
---

[← index](../../index.md)

# fixtures — Tests

## Fixtures

| Fixture           | Requirements                                                                    |
| ----------------- | ------------------------------------------------------------------------------- |
| compose-test-plan | confirmed compose spec plus confirmed test plan whose rows name one `small-module` fixture (three-function auth module, two seeded defects); target `compose` |

## Tests

| Fixture           | Tier    | Title            | Check logic                                                                       |
| ----------------- | ------- | ---------------- | ---------------------------------------------------------------------------------- |
| compose-test-plan | smoke   | FILE-PER-ROW     | `mod-review/compose/_fixtures/small-module.md` written, substantial, nothing else |
| compose-test-plan | smoke   | NO-QUESTIONS     | the return's Questions section is empty — the rows are unambiguous                |
| compose-test-plan | regress | MATCHES-ROWS     | the module carries exactly what the Fixtures table demands — three functions, the two seeded defects, and the sweep-findings lines the step would receive |
| compose-test-plan | regress | SINGLE-FLAW-FREE | a happy-path fixture: no extra traps smuggled in beyond what the rows name        |
