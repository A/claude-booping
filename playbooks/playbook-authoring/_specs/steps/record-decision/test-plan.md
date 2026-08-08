---
{}
---

[← index](../../index.md)

# record-decision — Tests

## Fixtures

| Fixture          | Requirements                                                              |
| ---------------- | ------------------------------------------------------------------------- |
| two-decisions    | invocation relaying two decision summaries; existing DECISIONS.md with one prior line |
| bootstrap-empty  | invocation with no decisions; no DECISIONS.md on disk                     |

## Tests

| Fixture         | Tier    | Title           | Check logic                                                                               |
| --------------- | ------- | --------------- | ----------------------------------------------------------------------------------------- |
| two-decisions   | smoke   | APPEND-ONLY     | prior line byte-identical; exactly two lines appended at the end                          |
| two-decisions   | smoke   | TIMESTAMP-SHAPE | every appended line starts `` `[YYYY-MM-DD HH:MM]` `` — date and time present             |
| two-decisions   | smoke   | VERBATIM        | appended summaries match the relayed text exactly — no rewording or merging               |
| bootstrap-empty | smoke   | BOOTSTRAP       | file created with `# Decisions` heading only; return carries the bootstrap note           |
| two-decisions   | regress | NO-FILTERING    | both decisions recorded even when trivial or redundant — narrowing is not the step's call |
