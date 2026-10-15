---
id: "05"
title: "Record model — superseded-by, resolved relations, record state"
sp: 3
status: done
plan: "plans/202610152329_specs-site-redesign/index.md"
---

# M05: Record model — superseded-by, resolved relations, record state

The site model knows, per record, its resolved typed relations, who supersedes it and its review state, so the record page, the lists and the machine layer read one computed source instead of re-deriving it in templates.

**Scope**: `booping-python/src/booping/specs/site/model.py` and a new `booping-python/src/booping/specs/site/state.py`. In `Site`: `relations(record) -> dict[str, list[SiteRecord]]` — every frontmatter key whose value is a ref or a list of refs (`values`, `rules`, `supersedes`, and any tier-own key such as `mechanics`), keys sorted, refs that resolve only, in frontmatter order, deduplicated; `superseded_by(record) -> list[SiteRecord]` — the records whose `supersedes` resolves to this one, in `site.records` order (direct refs only, as the old generator's `link_graph`). Both are `cached_property` indexes built once, like `_backlinks`. `state.py`: frozen dataclass `RecordState(status: str | None, kind: str | None, clarify: int, unknown: int, unreviewed: bool, first_mark: str | None)` — `first_mark` the anchor id (`L{line}`) of the record's first mark, the target the clarify badge links from the record head — and `record_state(record, marks) -> RecordState` over the marks `render_body` already returns. `build_site` computes one `RecordState` per record once and keeps it beside the rendered marks for M06–M08. `unreviewed()` stays where it is and `record_state` calls it.

Tests (integration, `booping-python/tests/specs/site_test.py`): an ADR with `values: [value/0001, value/0001, value/0099]` relates to value/0001 once and drops the missing ref; a tier-own key `mechanics: [mechanic/0001]` appears under `mechanics`; ADR 0002 `supersedes: [adr/0001]` → `superseded_by(adr/0001) == [adr/0002]` and `superseded_by(adr/0002) == []`; a cross-root `booping:rule/0002` resolves when that root is rendered; a record with two `[clarify]` and one `[unknown]` → `clarify=2, unknown=1`, `first_mark` the first mark's `L{line}`; `reviewed: 2026-10-01` → `unreviewed=False`.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | `Site.relations` and `Site.superseded_by` indexes and their tests. | `booping-python/src/booping/specs/site/model.py`, `booping-python/tests/specs/site_test.py` | 2 | done |
| 5.2 | `state.py` with `RecordState`/`record_state`, computed once in `build_site`; its tests. | `booping-python/src/booping/specs/site/state.py`, `booping-python/src/booping/specs/site/pages.py`, `booping-python/tests/specs/site_test.py` | 1 | done |

## Definition of Done

### Task 5.1

- [x] Both indexes are built once per `Site` and return records in a deterministic order.
- [x] The relation and supersession cases above pass.

### Task 5.2

- [x] `RecordState` is the only place clarify/unknown counts and the unreviewed flag are computed; `_counts`/`_block` in `pages.py` read it.
- [x] Site output is byte-identical to before this milestone — `uv run pytest e2e -k site -q` passes without rebaselining.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/src/booping/specs/site/model.py` — `_backlinks`, the index pattern to copy.
- `/home/anton/Dev/@A/shatterlings/crates/specs/src/site.rs` — `link_graph` (lines ~262–288), the superseded-by computation being ported.

## Verify

`cd booping-python && uv run pytest tests/specs e2e -k site -q`
