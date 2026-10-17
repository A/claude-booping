---
id: "04"
title: "Alternatives check — table rows match H3 options, one accepted, names from
  the schema"
sp: 4
status: done
plan: "plans/202610152146_project-level-schemas/index.md"
---

# M04: Alternatives check — table rows match H3 options, one accepted, names from the schema

`booping specs check` checks an ADR's alternatives across the file — table rows match the `###` option blocks, and exactly one option is `accepted` — under the section and column names the record's own schema sets.

**Scope**: new `booping-python/src/booping/specs/alternatives.py`. From the record's effective schema (M01's map; YAML load of the mdcheck rule file, read only): every rule whose `select` matches `SECTION("{name}") > TABLE` and has `columns:` defines one check — section `{name}`, option column `columns[0]`, status column the column `{c}` for which a rule `select`s `…TD[col="{c}"]` with an `enum` containing `accepted` (none → no status check) (C5). On the record (markdown-it, as the site parses): within the H2 section `{name}` — each table row's option cell is `[text](#anchor)`; every anchor is the `slug` (`specs/site/markdown.py`) of an H3 in that section; every such H3 is linked by exactly one row. Status: record `status` `accepted` or `superseded` → exactly one row `accepted`; any other status → at most one. Messages, check kind `alternatives`, level error, line of the offending row or H3 (1 when unknown): `option {anchor} names no ### in {name}`, `### {heading} has no row in {name}`, `### {heading} has {n} rows in {name}`, `{n} options accepted in {name}; a {status} record needs exactly one`, `{n} options accepted in {name}; at most one`. A record missing the section or table gets nothing here — mdcheck reports it. `check.py` calls it per record after the schema check.

Tests (integration tier, `booping-python/e2e/cases/specs/`, hand-derived): with the shipped `adr.yaml` — an accepted ADR with a row linking a missing `###`, an `###` with no row, and two `accepted` rows (three findings); a `proposed` ADR with no accepted row passes. With a project `_schemas/adr.yaml` translating section and columns (`Альтернативы`, `Вариант`, `Статус`) — a Russian ADR with a Cyrillic `###` anchor passes, the same ADR with zero `accepted` rows gets the exactly-one finding.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Derive the check's names from a schema file. | `booping-python/src/booping/specs/alternatives.py` | 1 | done |
| 4.2 | Rows ↔ H3 and accepted-count check on a record; wired into `check_tier`. | `booping-python/src/booping/specs/alternatives.py`, `booping-python/src/booping/specs/check.py` | 2 | done |
| 4.3 | The e2e cases above. | `booping-python/e2e/cases/specs/check-alternatives-*.txtar` | 1 | done |

## Definition of Done

### Task 4.1

- [x] For the shipped `adr.yaml` the derived names are `Alternatives` / `Option` / `Status`; for a schema without such a rule, no check.

### Task 4.2

- [x] `just specs-check` on this repo stays green (adr/0022 is `proposed` with no accepted row; every other ADR has one).
- [x] Each message is produced exactly as worded above.

### Task 4.3

- [x] The cases exist and pass.

Return: the list of changed and created files, nothing else.

## References

- `src/specs/schemas/adr.yaml` — the shipped rules the names are read from.
- `booping-python/src/booping/specs/site/markdown.py` — `slug` and the markdown-it setup to reuse.
- `vault/adr/0001-specs-tiers.md` — a passing ADR.

## Verify

`cd booping-python && uv run pytest e2e/cases/specs -q -k alternatives`
