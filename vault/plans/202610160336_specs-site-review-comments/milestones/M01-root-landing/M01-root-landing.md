---
id: "01"
title: "Root page follows the Overview landing"
sp: 3
status: done
plan: "/home/anton/Dev/@A/claude-booping-specs/vault/plans/202610160336_specs-site-review-comments/index.md"
---

# M01: Root page follows the Overview landing

A root's own page (`{root}/index.html`) reads as the Overview landing for that root: callout with the root's counts, scenario cards with quiet counts, Recently updated for the root — no mark list, no "Records: N".

**Scope**: `booping-python/src/booping/specs/site/pages.py` — one helper builds the landing context (`needs`, `unreviewed`, `questions`, `types`, `recent`) from a record list, a review-row count and an href prefix; `index.html.j2` (site-wide, `href` `records.html#type={type}`) and `root.html.j2` (the root's records, `href` `{type}/index.html`, `needs` = review rows whose `source` is the root, callout link `../review.html#source={root}`, recent pages prefixed `../`) both call it. `templates/_macros.html.j2` — the callout, the `ul.scen` cards and the Recently-updated block become macros used by both templates; `types_list` is deleted. `templates/index.html.j2` uses the macros (its output stays byte-identical); `templates/root.html.j2` is rewritten: `div.measure{h1 root name, callout}`, `ul.scen`, `div.measure{Recently updated}` — no lead. `src/config.yaml` — the `records` label is removed from `en` and `ru` when no template or Python reads it after the change. Exact behaviour: `../../clarifications.md` C6.

Tests (integration, `booping-python/tests/specs/site_pages_test.py`): replace `test_root_page_lists_types_with_counts_and_marks_with_links` with a root-landing test over a two-root fixture — the root's callout counts and link `../review.html#source={root}` hand-derived from the fixture, one card per type present in that root with its count and `{type}/index.html` href, Recently updated holding only that root's records newest first with `../`-prefixed hrefs, no `class="mark"`, no "Records:" text; a root with nothing to review renders no callout. The existing home test still passes unchanged. Rebaseline the `site-*.txtar` goldens and read the diff: root pages only.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Shared landing-context helper in `pages.py`; root page context per C6; tests. | `booping-python/src/booping/specs/site/pages.py`, `booping-python/tests/specs/site_pages_test.py` | 2 | done |
| 1.2 | Landing macros; `index.html.j2` and `root.html.j2` on them; `types_list` and an unused `records` label removed; golden rebaseline. | `booping-python/src/booping/specs/site/templates/_macros.html.j2`, `booping-python/src/booping/specs/site/templates/index.html.j2`, `booping-python/src/booping/specs/site/templates/root.html.j2`, `src/config.yaml`, `booping-python/e2e/cases/specs/site-*.txtar` | 1 | done |

## Definition of Done

### Task 1.1

- [x] `index.html` and every `{root}/index.html` get their landing context from one helper.
- [x] Root callout counts and link match C6; no callout when the root's `needs` is 0.
- [x] The new root-landing test asserts hand-derived counts, cards, hrefs and recent order; the old marks test is gone.

### Task 1.2

- [x] `index.html` output is byte-identical to before (its golden hunks are unchanged).
- [x] `root.html.j2` holds no mark list and no `types_list` call; `types_list` no longer exists; `grep -rn '"records"\|ui("records")' booping-python/src src/config.yaml` finds nothing, or the label stays because something still reads it.
- [x] `site-*.txtar` goldens rebaselined with `just e2e -k site --txtar-update`; their diff touches `{root}/index.html` pages only.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/src/booping/specs/site/templates/index.html.j2` — the landing shape to reuse.
- `booping-python/tests/specs/site_pages_test.py` — `test_home_lead_callout_scenarios_and_recent`: the test shape to copy.

## Verify

`cd booping-python && uv run pytest tests/specs/site_pages_test.py e2e -k site -q`
