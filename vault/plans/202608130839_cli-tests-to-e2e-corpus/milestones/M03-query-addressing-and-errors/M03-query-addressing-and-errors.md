---
id: "03"
title: "query corpus — spec addressing, flag errors, exit codes"
sp: 4
status: done
plan: "vault/plans/202608130839_cli-tests-to-e2e-corpus/index.md"
---

# M03: query corpus — spec addressing, flag errors, exit codes

`booping query`'s two addressing forms, its flag-level errors and its exit-code contract are covered by txtar cases under `e2e/cases/query/`.

**Scope**: `booping query`'s argument surface — `--config`, `--glob`, `--where`, `--project`, `--output` — asserted through rows returned, error text and exit codes. The 8 `parse_where` unit assertions land here as CLI cases. Files: new `booping-python/e2e/cases/query/*.txtar`. Nothing is deleted in this milestone; `tests/commands/query_test.py` goes in M07 once both query milestones' cross-checks are in.

Each case carries only the vault files it needs — a case about a malformed clause needs no plans at all.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Addressing cases: a `--config` dotted path resolves a spec from the project tier and runs; inline `--glob` runs without any config entry; inline `--where` / `--sort` / `--columns` narrow a resolved config spec; repeated `--where` applies both clauses conjunctively; zero matches exits 0 with an empty result | `booping-python/e2e/cases/query/*.txtar` | 2 | done |
| 3.2 | Clause-shape cases carrying `parse_where`'s coverage: equality, inequality keeping the operator suffix, `:in` splitting on commas, a value containing `=`, an ordering clause reaching the engine, a negative ordering operand | `booping-python/e2e/cases/query/*.txtar` | 1 | done |
| 3.3 | Error and exit-code cases: a malformed `--where` pair and an empty ordering operand each exit 1 naming the offending clause; an unknown config path and a non-mapping config value give distinct messages; both addressing forms together and neither of them each exit 1; an unknown `--output` exits 1; a vault-relative spec with no project exits 2; `--help` lists every flag and enumerates the `--where` operators | `booping-python/e2e/cases/query/*.txtar` | 1 | done |

## Definition of Done

### Task 3.1

- [x] A case with a project vault whose `config.yaml` declares a spec runs it by `--config` and returns the expected rows.
- [x] `--glob 'plans/*/index.md'` returns the same rows with no config entry present.
- [x] A case passing `--config` plus inline `--where`, `--sort` and `--columns` shows the inline flags narrowing the resolved spec rather than replacing it.
- [x] Two `--where` flags in one invocation return only rows satisfying both.
- [x] A spec matching nothing exits 0 and prints an empty result in the invoked `--output` format.

### Task 3.2

- [x] `--where status=done` and `--where 'status!=done'` return complementary row sets over the same fixture.
- [x] `--where 'status:in=done, ready-for-dev'` returns rows matching either option, proving the comma split and the whitespace trim.
- [x] `--where 'k=a=b'` treats everything after the first `=` as the value.
- [x] `--where id:gt=3` and `--where id:lt=9` filter numerically, and `--where id:gt=-1` is accepted as a negative operand rather than parsed as a flag.

### Task 3.3

- [x] A `--where` pair with no `=` exits 1 and the message names the pair.
- [x] `--where id:gt=` exits 1 and the message names the clause.
- [x] An unknown `--config` path and a `--config` path resolving to a non-mapping produce two distinct messages, both exit 1.
- [x] `--config` with `--glob` exits 1 saying they are mutually exclusive; neither flag exits 1 saying one is required.
- [x] An unknown `--output` value exits 1 and the message lists the legal formats.
- [x] A vault-relative spec run outside any project exits 2 with the no-vault-resolved message.
- [x] `booping query --help` exits 0, its output names every flag, and it enumerates the `--where` operator suffixes.

## Verify

```
cd booping-python && uv run pytest e2e -k query
```

Every case in this milestone passes with no `--txtar-update` needed.
