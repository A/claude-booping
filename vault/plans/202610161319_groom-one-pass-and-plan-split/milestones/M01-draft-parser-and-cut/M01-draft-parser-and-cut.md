---
id: "01"
title: "Draft parser and cut"
sp: 4
status: done
plan: "plans/202610161319_groom-one-pass-and-plan-split/index.md"
---

# M01: Draft parser and cut

**Goal**: a pure function turns a one-file plan draft into a `Cut` — plan lines, overview lines, milestones with their sections and fields, groups and flags — with every draft line placed exactly once.

**Scope**: new package `booping-python/src/booping/plan/` (`__init__.py`, `split.py`), new tests `booping-python/tests/plan/split_test.py` plus draft fixtures under `booping-python/tests/plan/__fixtures__/`. No CLI, no disk writes — M02 wires them. Port source (read-only, outside the repo): `~/Dev/@A/booping-benchmarks/groom/split/heading_cut.py`, the helpers it imports from `cut.py` (`meta_fences`, `meta_row`, `META_KEY`, `demote`, `block`) and from `check.py` (`MS_HEAD`, `DEP_META`, `STD_HEADINGS`).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Port detection and ownership: fences, milestone heading blocks (`### M1 — t`, `### M01-slug`, path headings, embedded `# M1 —`, repeated ids), end of the last block, overview table, embedded metadata (fenced, bare frontmatter, key/value tables), section switching on Tasks / DoD / References / Verify and their synonyms, text before the first section to Tasks. Return a frozen `Cut` dataclass instead of the prototype's line-map JSON; drop `.meta/`, timing and the `cut.py` map validation. Names in English snake_case, typed, no module-level state. | `booping-python/src/booping/plan/__init__.py`, `booping-python/src/booping/plan/split.py` | 2 | done |
| 1.2 | Port fields and groups: title (metadata → overview row → heading → path heading with a flag), `sp` (metadata → overview row → `SP: n` text, else `None` with a flag), `depends_on` (metadata → overview row → `Depends on:` text → prose), renumbering to `01…` in draft order, kebab slug. Groups: contiguous runs in id order while the sum stays ≤ `max_sp`, a lone milestone always valid, `max_sp=None` → one milestone per group; a `depends_on` naming an unknown id or a later milestone is a flag. Count `#`/`##` headings demoted to `###` inside sections, and flag a section with an unbalanced code fence. | `booping-python/src/booping/plan/split.py` | 1 | done |
| 1.3 | Unit tests on small hand-written drafts (behaviour, hand-derived expectations, no mocks): the fixed format `### M01 — t` + `sp:` + `depends_on:` + `#### Tasks…`; a path-heading draft; a heading inside a code fence is never a cut; no milestone heading → `Cut` with no milestones; missing `sp` → `None` + flag; groups at the cap boundary (sum == cap stays, cap+1 closes) and `max_sp=None`; a `depends_on` naming a later milestone → flag; coverage — the multiset of non-marker draft lines equals the multiset of lines across plan lines and all sections. | `booping-python/tests/plan/__init__.py`, `booping-python/tests/plan/split_test.py`, `booping-python/tests/plan/__fixtures__/*.md` | 1 | done |

Tests: surface `booping.plan.split.cut_draft(text, max_sp)`; cases above; tier unit (pure function over strings).

## Definition of Done

### Task 1.1

- [x] `cut_draft(text: str, max_sp: int | None) -> Cut` exists in `booping/plan/split.py`; `Cut` exposes `plan_lines`, `overview_lines`, `milestones` (each with `id`, `title`, `slug`, `sp`, `depends_on`, `sections` keyed `tasks`/`dod`/`references`/`verify` holding source lines with their line endings), `groups`, `flags`, `demoted`.
- [x] Lines are kept with their original line endings; no line is re-wrapped, stripped or re-encoded.

### Task 1.2

- [x] A draft whose milestones state no `sp` yields `sp is None` for each and one flag per milestone naming it.
- [x] Groups follow the rule above; a forward-only dependency graph produces no flag.

### Task 1.3

- [x] `uv run pytest tests/plan/split_test.py` passes with every case listed in the Tasks table.
- [x] The coverage test fails if any task line is dropped or duplicated (proved by the test asserting multiset equality, not counts alone).

## References

- `~/Dev/@A/booping-benchmarks/groom/split/heading_cut.py` — the algorithm being ported, function by function.
- `booping-python/src/booping/specs/` — package layout and typing style of an existing multi-module area.
- `booping-python/tests/context/plan_template_test.py` — plain pytest functions over real fixture files.

## Verify

```
cd booping-python && uv run pytest tests/plan/split_test.py -q
```
