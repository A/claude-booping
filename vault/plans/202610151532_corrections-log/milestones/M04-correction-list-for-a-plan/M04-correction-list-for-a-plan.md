---
id: "04"
title: "booping correction list prints a plan's feed"
sp: 3
status: done
plan: "plans/202610151532_corrections-log/index.md"
---

# M04: booping correction list prints a plan's feed

`booping correction list --plan PATH` prints every correction logged against a plan — its own sidecar, then its code reviews' — as one markdown feed.

**Scope**: `list` verb in `booping-python/src/booping/commands/correction.py`, logic in `booping-python/src/booping/correction.py`: the plan's `code_reviews:` frontmatter read with the shared frontmatter reader; sidecars in the order and shape of `index.md` `## I/O contract` → `list`, each distinct review directory once, missing sidecars skipped. Missing plan → `error: plan not found: {path}`, exit 1.

Tests: integration tier, txtar cases — a plan sidecar alone; a plan sidecar plus two reviews in one `codereviews/{dir}/` printed once; a review sidecar with no plan sidecar; no sidecar prints `no corrections for {plan}`; a missing plan is exit 1.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | `list` verb and feed assembly. | `booping-python/src/booping/commands/correction.py`, `booping-python/src/booping/correction.py` | 2 | done |
| 4.2 | The txtar cases named in Tests. | `booping-python/e2e/cases/correction/list-*.txtar` | 1 | done |

## Definition of Done

### Task 4.1

- [x] `booping correction list --help` lists `--plan`.
- [x] stdout matches the `list` shape of `index.md` `## I/O contract` exactly; nothing on stderr on success.

### Task 4.2

- [x] One case per behaviour named in Tests.

Return: the list of changed files, nothing else.

## References

- `booping-python/src/booping/commands/session_stats.py` — reading an artefact's frontmatter list (`_frontmatter`, `_session_ids`).
- `booping-python/e2e/cases/correction/` — the M01 cases, for fixture sidecars.

## Verify

`just e2e -k "correction and list"`
