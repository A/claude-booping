---
id: "07"
title: "the session-stats tier split"
sp: 2
status: pending
plan: "vault/plans/202608131522_final-cli-commands-to-e2e/index.md"
---

# M07: the session-stats tier split

`tests/test_session_stats.py` loses its thirteen CLI tests and its one redundant test, keeps its twenty-eight library tests, and is renamed to the repo's dominant convention.

**Scope**: the tier line inside one unit file. Files: deleted `booping-python/tests/test_session_stats.py`; new `booping-python/tests/session_stats_test.py`. This is the only milestone in the plan that draws a tier line *inside* a file rather than deleting one wholesale, and the reason is stated in the plan's Decisions: the CLI is a thin JSON-and-frontmatter wrapper, while the parsing and active-time arithmetic underneath it is library logic that would need a fixture corpus per edge case to re-derive through argv.

Depends on M05 and M06 — no CLI test is removed before its case exists.

The surviving twenty-eight tests are the `locate_transcript`, `parse_transcript`, `summarize` and `build_report` tests: transcript location and its tolerances, turn-start classification, prompt-versus-notification origin, meta and sidechain exclusion, tool-use extraction and denial kinds, idle-gap and blocking-span subtraction, empty and header-only transcripts, token summation rules including the `iterations` array and the cache-field separation, model deduplication, and the rounding of total minutes.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | Rename the file to `session_stats_test.py`, matching the `*_test.py` convention the rest of the suite uses, and delete the thirteen CLI tests now covered by cases along with `test_cli_registers_session_stats_with_contract_defaults` | `booping-python/tests/session_stats_test.py`, `booping-python/tests/test_session_stats.py` | 1 | pending |
| 7.2 | Confirm the surviving file imports only `booping.session_stats` library symbols, reads only `tests/fixtures/session_stats/`, and record in the milestone which corpus case covers each deleted test | `booping-python/tests/session_stats_test.py` | 1 | pending |

## Definition of Done

### Task 7.1

- [ ] `tests/test_session_stats.py` no longer exists and `tests/session_stats_test.py` holds the twenty-eight library tests.
- [ ] The thirteen CLI tests — directory walk, single-file path, skipped artifact, stdout-versus-stderr split, both exit-1 refusals, the four write-path tests, and the per-session key-name test — are gone from the file.
- [ ] `test_cli_registers_session_stats_with_contract_defaults` is gone, and its four defaults are each exercised by a case that omits the flag.

### Task 7.2

- [ ] The surviving file imports no symbol from `booping.commands.session_stats`.
- [ ] `uv run pytest tests/session_stats_test.py` is green and the collected count is twenty-eight.
- [ ] Every deleted test is listed in this milestone against the case file that replaced it, or marked as a recorded drop with its reason. M10 rolls this mapping up with the other milestones' into the plan-wide cross-check table; it is recorded here first because this is the only milestone that splits a file rather than deleting one, so the mapping is the evidence the tier line was drawn where the plan says.

## Verify

```
cd booping-python && uv run pytest tests/session_stats_test.py && uv run pytest e2e -k session-stats
```

Both green; the library file no longer touches the CLI and every CLI behaviour it dropped is collected in the corpus.
