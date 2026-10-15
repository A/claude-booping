---
id: "03"
title: "Record reading column and relations in the facts grid"
sp: 3
status: done
plan: "/home/anton/Dev/@A/claude-booping-specs/vault/plans/202610160249_specs-site-polish/index.md"
---

# M03: Record reading column and relations in the facts grid

A record page reads in one 68ch column, and its relations are rows of the facts grid instead of a separate list beside it.

**Scope**: `booping-python/src/booping/specs/site/templates/record.html.j2` (the `article` and the Referenced-by section wrapped in one `<div class="measure">`; the `r.relations` rows rendered inside the same `dl.facts` after the `r.facts` rows — `dt` the relation label, `dd` the existing `ul.rel` list of `rel_item`s; the facts `dl` renders when either list is non-empty; the `<section class="relations">` block deleted; the raw-frontmatter `dl.facts` box unchanged), `style.css` (`.relations` rules deleted; `.facts ul.rel` compact — facts font size, no dashed separators, no item padding beyond the facts row gap; the ADR table's horizontal-scroll wrapper keeps working inside the column), `booping-python/tests/specs/site_pages_test.py`. Exactly `../../clarifications.md` C1 and C2. `pages.py` `_relations` keeps its data shape. Every reference to the `relations` CSS class in templates, CSS and tests is gone at the end (booping:rule/0007).

Tests (integration, `booping-python/tests/specs/site_pages_test.py`): extend `test_record_page_head_facts_and_relations_in_russian` — the relation `dt` (Russian label) and its linked record sit inside the same `<dl class="facts">` as the author row; the page holds no `class="relations"`; the article sits inside `class="measure"`. `test_list_and_record_classes_the_pages_emit_are_styled` stays green with `relations` gone. Rebaseline the `site-*.txtar` goldens and read the diff: record page head and the measure wrapper only.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Relations as rows of the facts `dl`; delete `.relations` markup and CSS; compact `.facts ul.rel`; tests. | `booping-python/src/booping/specs/site/templates/record.html.j2`, `booping-python/src/booping/specs/site/style.css`, `booping-python/tests/specs/site_pages_test.py` | 2 | done |
| 3.2 | `.measure` around the record article and Referenced by; golden rebaseline. | `booping-python/src/booping/specs/site/templates/record.html.j2`, `booping-python/e2e/cases/specs/site-*.txtar` | 1 | done |

## Definition of Done

### Task 3.1

- [x] A record with relations renders one `dl.facts` holding the facts rows then one `dt`/`dd` pair per relation, each `dd` the `ul.rel` list with title link, ref and state badge.
- [x] A record with relations and no facts still renders the `dl.facts` with the relation rows.
- [x] `grep -rn 'class="relations"\|section.relations\|\.relations\b' booping-python/src/booping/specs/site booping-python/tests` prints nothing.

### Task 3.2

- [x] The record `article` and the Referenced-by section sit in one `div.measure`; the rail and sidebar are outside it.
- [x] `site-*.txtar` goldens rebaselined with `just e2e -k site --txtar-update`; their diff touches record pages only.

Return: the list of changed and created files, nothing else.

## References

- `vault/plans/202610152329_specs-site-redesign/design/specs-site-mockup.html` — `record()`: the whole record in `.measure`, «Служит ценностям» as a `dt`/`dd` row of `dl.facts`.
- `booping-python/tests/specs/site_pages_test.py` — `test_record_page_head_facts_and_relations_in_russian`: the test to extend.

## Verify

`cd booping-python && uv run pytest tests/specs/site_pages_test.py e2e -k site -q`
