---
id: "03"
title: "List rows with data attributes, All records page, sidebar"
sp: 4
status: done
plan: "plans/202610160041_specs-site-landing-and-filters/index.md"
---

# M03: List rows with data attributes, All records page, sidebar

Every list renders its rows through one macro carrying the filter data, `records.html` lists every record across roots, and the sidebar becomes the C6 navigation.

**Scope**: `booping-python/src/booping/specs/site/templates/_macros.html.j2`, `templates/type.html.j2`, `templates/records.html.j2` (new), `templates/base.html.j2`, `pages.py`, `config` labels in `src/config.yaml` (`core.specs.site.labels.{en,ru}.ui`). One `record_row(view, labels, prefix, hide_unreviewed=false)` macro replaces the inline `<li class="row">` of `type.html.j2` (same visible markup as today) and adds `data-type`, `data-source` (root name), `data-status` (raw status, `""` when none), `data-flags` (space-joined `RecordState.reasons`), `data-updated` (`YYYY-MM-DD` or `""`), `data-title` (the displayed title), `data-created-by`, `data-order` (0-based page position). `records.html`: H1 label "All records", every record of every root in page order (roots in order, types in site type order, records by number) as `record_row`s, crumbs Overview › All records. Sidebar (`nav` built in `pages.py`, rendered in `base.html.j2`) per `../../clarifications.md` C6: Overview, Review (count = M05's pool — compute it here from `reasons` plus `open_items` so the count is right from this milestone), All records (count), Types (across roots, count, `records.html#type={type}`), Tags (only roots whose M02 tree is non-empty: top-level nodes with counts linking `tag_page_path`, plus the tree link `{root}/tags/index.html`; root name sub-heading only when more than one root has tags — those links point at pages M07 writes), Sources (root pages with record counts), `llms.txt`. `aria-current="page"` as today. The Review link points at `review.html` (M05) and the tag links at pages M07 writes: the `_Links` checker in `site_pages_test.py` excludes exactly `review.html` and `tags/` until those milestones drop the exclusion. New `ui` labels in both `en` and `ru`, countable ones as plural lists.

Tests (integration, `site_pages_test.py`): every `.row` on a type page and on `records.html` carries all eight `data-*` attributes with hand-derived values for a fixture record (an unreviewed ADR with a clarify mark → `data-flags="unreviewed clarify"`); `records.html` holds one row per record across two roots; the sidebar holds the C6 groups in order with the counts of the fixture, whose `open_items` holds one item so the Review count is records with reasons + 1; no hardcoded English in the new templates under `lang: ru` (every new label resolves from the `ru` table). Rebaseline `site-*.txtar` goldens with `--txtar-update` and read the diff: sidebar on every page, `records.html` added, row attributes on type pages; record bodies unchanged.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | `record_row` macro with data attributes; type page uses it; `records.html`. | `booping-python/src/booping/specs/site/templates/_macros.html.j2`, `booping-python/src/booping/specs/site/templates/type.html.j2`, `booping-python/src/booping/specs/site/templates/records.html.j2`, `booping-python/src/booping/specs/site/pages.py` | 2 | done |
| 3.2 | Sidebar per C6; labels en/ru; tests; golden rebaseline. | `booping-python/src/booping/specs/site/templates/base.html.j2`, `booping-python/src/booping/specs/site/pages.py`, `src/config.yaml`, `booping-python/tests/specs/site_pages_test.py`, `booping-python/e2e/cases/specs/site-*.txtar` | 2 | done |

## Definition of Done

### Task 3.1

- [x] One row macro serves every record list; rows carry the eight `data-*` attributes.
- [x] `records.html` lists all records of all roots in page order.

### Task 3.2

- [x] Sidebar matches C6 on every page, desktop and drawer; its Review count includes open items.
- [x] New labels exist in `en` and `ru`; `site_labels_test.py` still passes.
- [x] Rebaselined goldens differ only by the sidebar, the new page and row attributes.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/src/booping/specs/site/templates/type.html.j2` — today's row markup to keep.
- `../../../202610152329_specs-site-redesign/design/specs-site-mockup.html` — sidebar (`.side`) groups and count spans.

## Verify

`cd booping-python && uv run pytest tests/specs/site_pages_test.py tests/specs/site_labels_test.py e2e -k site -q`
