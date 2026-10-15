---
id: "05"
title: "Russian schema set \u2014 src/specs/schemas-ru, a translation of every shipped schema"
sp: 3
status: pending
plan: "plans/202610152146_project-level-schemas/index.md"
---

# M05: Russian schema set — src/specs/schemas-ru, a translation of every shipped schema

booping ships `src/specs/schemas-ru/`, a Russian translation of every shipped schema, and a Russian record of each type passes `booping specs check` under it.

**Scope**: create `src/specs/schemas-ru/{adr,conflict,idea,reference,rule,runbook,story,value}.yaml`, each a copy of `src/specs/schemas/{type}.yaml` with the same rules, header comment translated, and only headings, bold labels, the story sentence pattern, and the alternatives Сложность/Обратимость cell enums changed — exactly the strings in `clarifications.md` C7. Unchanged: every frontmatter key and enum, `summary` ≤ 200, the Статус cell enum `accepted | proposed | rejected`, `doc:` values. The rule schema keeps booping's `Follows from` semantics under `Следует из ценностей` (an item links any source).

Tests (integration tier, `booping-python/e2e/cases/specs/`, hand-derived): one case — a project tier whose `_schemas/` holds the eight Russian files (fixture copies) and one valid Russian record per type, including an ADR whose alternatives pass M04's check — `booping specs check` exits 0 with empty stdout. A unit test (`booping-python/tests/specs/schemas_ru_test.py`) asserts `schemas-ru/` has exactly the stems of `schemas/` and that each pair's `FRONTMATTER` rule is identical, so a shipped type without a translation, or a translated frontmatter key or enum, fails.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | The eight Russian schema files. | `src/specs/schemas-ru/*.yaml` | 2 | pending |
| 5.2 | The e2e case and the stem-parity unit test. | `booping-python/e2e/cases/specs/check-russian-set-*.txtar`, `booping-python/tests/specs/schemas_ru_test.py` | 1 | pending |

## Definition of Done

### Task 5.1

- [ ] `mdcheck src/specs/schemas-ru/{type}.yaml {fixture record}` exits 0 for each type's fixture record.
- [ ] Every file's `FRONTMATTER` rule is identical to its shipped counterpart's.

### Task 5.2

- [ ] The case and the unit test exist and pass.

Return: the list of changed and created files, nothing else.

## References

- `src/specs/schemas/*.yaml` — the source of every rule.
- `/home/anton/Dev/@A/hermes-pet/specs/schemas/*.yaml` (read-only) — the Russian headings and labels.
- `vault/plans/202610152146_project-level-schemas/clarifications.md` C7 — the locked string list.

## Verify

`cd booping-python && uv run pytest tests/specs/schemas_ru_test.py e2e/cases/specs -q -k "russian or schemas_ru"`
