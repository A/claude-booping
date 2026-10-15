---
id: "02"
title: "Sidebar tags as plain links, empty tags hidden"
sp: 2
status: pending
plan: "/home/anton/Dev/@A/claude-booping-specs/vault/plans/202610160249_specs-site-polish/index.md"
---

# M02: Sidebar tags as plain links, empty tags hidden

The sidebar tag tree shows tags as plain links with a count and leaves out tags no record carries.

**Scope**: `booping-python/src/booping/specs/site/pages.py` (`_nav`: sidebar tag nodes with `count` 0 are dropped — the sidebar only; the tag tree page and tag pages built from `trees` are untouched), `templates/base.html.j2` (the sidebar tag `<li>`: the tag text without `<code>`), `style.css` (any rule styling `.side` tag `code` removed). Exactly `../../clarifications.md` C4.

Tests (integration, `booping-python/tests/specs/site_pages_test.py`): extend `test_sidebar_tags_group_per_root_with_top_level_counts` — a `tags.yaml` tag no record carries is absent from the sidebar and present on `{root}/tags/index.html`; the sidebar tag link text is the bare tag, no `<code>`. Rebaseline the `site-*.txtar` goldens and read the diff: the sidebar tag list only.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Drop zero-count sidebar tags, plain-text tag links, CSS cleanup, tests, golden rebaseline. | `booping-python/src/booping/specs/site/pages.py`, `booping-python/src/booping/specs/site/templates/base.html.j2`, `booping-python/src/booping/specs/site/style.css`, `booping-python/tests/specs/site_pages_test.py`, `booping-python/e2e/cases/specs/site-*.txtar` | 2 | pending |

## Definition of Done

### Task 2.1

- [ ] No sidebar tag link carries `<code>`; each shows the tag text and its count.
- [ ] A tag with 0 records is absent from every page's sidebar and still listed on the tag tree page.
- [ ] `site-*.txtar` goldens rebaselined with `just e2e -k site --txtar-update`; their diff touches the sidebar tag list only.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/tests/specs/site_pages_test.py` — `test_sidebar_tags_group_per_root_with_top_level_counts`: the test to extend.
- `vault/plans/202610152329_specs-site-redesign/design/specs-site-mockup.html` — `sideHTML()`: tags as plain links with a count.

## Verify

`cd booping-python && uv run pytest tests/specs/site_pages_test.py e2e -k site -q`
