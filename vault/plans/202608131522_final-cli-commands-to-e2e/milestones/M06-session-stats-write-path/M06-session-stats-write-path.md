---
id: "06"
title: "session-stats write path"
sp: 3
status: done
plan: "vault/plans/202608131522_final-cli-commands-to-e2e/index.md"
---

# M06: session-stats write path

Frontmatter stamping — the six `metrics_*` keys, the idempotent rerun, `--force` and `--dry-run` — is pinned by txtar cases asserting the written artifact, not just stdout.

**Scope**: `booping session-stats <path> [--force] [--dry-run]` and the frontmatter it writes. Files: new `booping-python/e2e/cases/session-stats/*.txtar`. Every case here carries an `expected/` section for the stamped artifact, since the written file is the contract; stdout's `written` flag alone would not catch a wrong value landing in the file.

Transcripts are seeded as in M05, and every stamped total is derived by hand from the seeded events, with the arithmetic shown in a comment at the top of each case that pins one.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | Write the stamping cases: a fresh artifact gaining all six `metrics_*` keys with `written` true in stdout and the keys pinned in an `expected/` section, and a per-session JSON object whose keys are the `metrics_*` names verbatim | `booping-python/e2e/cases/session-stats/*.txtar` | 1 | done |
| 6.2 | Write the idempotence cases: a rerun over an already-stamped artifact reported as not written with the file byte-identical, and `--force` overwriting stale values with the fresh ones | `booping-python/e2e/cases/session-stats/*.txtar` | 1 | done |
| 6.3 | Write the `--dry-run` case as two consecutive `cmd` lines — a dry run then a wet run over the same seeded artifact — pinning identical totals across both and the artifact unchanged after the first | `booping-python/e2e/cases/session-stats/*.txtar` | 1 | done |

## Definition of Done

### Task 6.1

- [x] A fresh artifact case pins all six `metrics_*` keys in an `expected/` section with hand-derived values, and `written: true` in the JSON.
- [x] The per-session objects in stdout use the `metrics_*` names verbatim as their keys, not a shortened alias.
- [x] The stamped artifact's non-metrics frontmatter keys and its body survive the write unchanged.

### Task 6.2

- [x] A rerun over an artifact already carrying the six keys reports `written: false` and its `expected/` section is byte-identical to the seeded fixture.
- [x] A `--force` case seeds deliberately wrong values and pins the corrected ones after the run.

### Task 6.3

- [x] The dry-run cmd line and the wet cmd line print the same totals, visible in the concatenated stdout.
- [x] The case's `expected/` section shows the artifact carrying the keys — written by the second invocation, since the first must not write.
- [x] A sibling case runs `--dry-run` alone and its `expected/` section shows the artifact still without any `metrics_*` key.

## Verify

```
cd booping-python && uv run pytest e2e -k session-stats
```

Green, including every case added in M05.
