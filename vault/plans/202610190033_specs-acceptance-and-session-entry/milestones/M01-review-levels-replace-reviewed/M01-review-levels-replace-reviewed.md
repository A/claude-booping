---
id: "01"
title: "Review levels replace reviewed"
sp: 11
status: done
plan: "plans/202610190033_specs-acceptance-and-session-entry/index.md"
---

# M01: Review levels replace `reviewed

## Tasks

**Goal:** a record carries `review` and `review_evidence`; every reader of `reviewed` reads the level; the site marks a record `accepted`.
**Scope:** `src/specs/README.md`, `booping-python/src/booping/specs/records.py`, `status.py`, `specs/site/**`, `booping specs check`, unit tests and e2e cases touching `reviewed`; `documentation/specs.md`.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Guide: replace the `reviewed` entry with `review` (no key / `shown` / `discussed` / `accepted`) and `review_evidence` (Decisions 5–7), keep both in the list of keys a tier schema may not rename | `src/specs/README.md` | 2 | done |
| 1.2 | Records and status: a level reader replacing `unreviewed()`; `booping status` prints the not-accepted line of Decision 10; `booping specs check` errors on a `reviewed:` key naming the replacement, and on a level outside the enum or a level without evidence | `booping-python/src/booping/specs/records.py`, `booping-python/src/booping/status.py`, the specs check module | 3 | done |
| 1.3 | Site: state, machine layer, facts, filters, search facets and icons read the level (accepted vs not accepted, the level shown as a fact); the "mark reviewed" control becomes "accepted" and its Outbox line `{ref} — accepted {date}` | `booping-python/src/booping/specs/site/*.py`, `comments.js`, `comments-format.js`, `templates/*.j2` | 4 | done |
| 1.4 | Tests and e2e: rewrite every case seeding `reviewed:`; add check cases for `reviewed:` present, level without evidence, bad level; status case for the not-accepted line; site case for the accepted icon and Outbox line; docs page `documentation/specs.md` Outbox section | `booping-python/tests/specs/*`, `booping-python/e2e/cases/specs/*`, `booping-python/e2e/cases/status/*`, `documentation/specs.md` | 2 | done |

Test surface: `booping specs check`, `booping status` and the site render, integration tier through e2e txtar cases — record with each level, legacy `reviewed:`, missing evidence.

## Definition of Done

Task 1.1
- [x] The guide lists `review` and `review_evidence` with the four levels and the evidence each needs; `reviewed` appears nowhere in it.

Task 1.2
- [x] `booping status` prints `records: {n} not accepted — none {a}, shown {b}, discussed {c}` on a fixture with one record per level.
- [x] `booping specs check` reports an error for `reviewed:`, for an unknown level, and for a level without `review_evidence`.

Task 1.3
- [x] A rendered record page shows its level; the unreviewed filter is renamed to "not accepted" and selects every record below `accepted`.
- [x] The Outbox emits `{ref} — accepted {date}`.

Task 1.4
- [x] `grep -rn "reviewed" booping-python/src documentation/specs.md src/specs` returns only the word inside prose that means "read", never the key.
- [x] `just pytest` and `just e2e -k "specs or status"` pass.

Return: the files changed and the Verify verdict, nothing else.

## References

- `migrations/003_session_metrics/migration.md` — why flat keys.
- `booping-python/e2e/cases/specs/site-writes-search-index-and-body.txtar` — the case seeding `reviewed:` to rewrite.

## Verify

`just pytest && just e2e -k "specs or status"`
