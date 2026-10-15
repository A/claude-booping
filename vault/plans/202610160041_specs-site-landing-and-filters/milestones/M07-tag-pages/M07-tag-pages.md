---
id: "07"
title: "Tag pages — tag tree, per-tag lists, linked record tags"
sp: 3
status: done
plan: "plans/202610160041_specs-site-landing-and-filters/index.md"
---

# M07: Tag pages — tag tree, per-tag lists, linked record tags

Each root with tags gets a tag tree page and one page per tag listing its records (descendants included) with filters; record pages link their tags.

**Scope**: `booping-python/src/booping/specs/site/templates/tags.html.j2` (new), `templates/tag.html.j2` (new), `templates/record.html.j2`, `_macros.html.j2` (`tag_tree` recursive macro), `pages.py`, `src/config.yaml` labels. Per `../../clarifications.md` C7, from M02's `tag_tree`/`tagged`/`tag_page_path`: `{root}/tags/index.html` — H1 "Tags" label, crumbs Overview › root › Tags, nested `<ul class="tag-tree">` of nodes (tag link, count, description); `{root}/tags/{tag}.html` — crumbs Overview › root › Tags › ancestors › tag, H1 the tag in mono, description as lead, children as the same tree list, then the `tagged` records as `record_row`s with the M04 filter bar (facets `type`, `status`, `flag`; sort `number` default). Record page tag chips become links to their tag pages. Pages written only for roots whose tree is non-empty. The `:` → `.` file name is collision-free because tags are kebab-case segments without `.` (`booping-python/src/booping/specs/tags.py` `_TAG_RE`); a used tag outside that pattern still gets a page under the same mapping (the checker reports it). Drop the M03 `_Links` checker exclusion for `tags/` — every sidebar tag link now resolves. M02 warnings join `build_site`'s warnings.

Tests (integration, `site_pages_test.py`): the M02 fixture renders `tags/index.html` with the nested tree and counts, `tags/a.html` lists both `a:*` records and links child `a:b`, `tags/a.b.c.html` has crumbs through `a` and `a:b`; a record page's tag links resolve; a root with no tags gets no `tags/` directory; every link in the output resolves (the `_Links` checker, no exclusions). Add one txtar case `booping-python/e2e/cases/specs/site-renders-tag-pages-from-tags-yaml.txtar` (a tier with `tags.yaml` and two-level tags; expected `tags/index.html` and one tag page) and rebaseline the others; read the diff: record pages' tag links and the new pages only.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | Tag tree page, tag pages with filtered lists, record tag links; labels. | `booping-python/src/booping/specs/site/templates/tags.html.j2`, `booping-python/src/booping/specs/site/templates/tag.html.j2`, `booping-python/src/booping/specs/site/templates/record.html.j2`, `booping-python/src/booping/specs/site/templates/_macros.html.j2`, `booping-python/src/booping/specs/site/pages.py`, `src/config.yaml` | 2 | done |
| 7.2 | Tests, new txtar case, golden rebaseline. | `booping-python/tests/specs/site_pages_test.py`, `booping-python/e2e/cases/specs/site-renders-tag-pages-from-tags-yaml.txtar`, `booping-python/e2e/cases/specs/site-*.txtar` | 1 | done |

## Definition of Done

### Task 7.1

- [x] Tag pages and tree follow C7; record tags link to them.
- [x] No link in the output is unresolved.

### Task 7.2

- [x] Tests and the new txtar case pass; other goldens differ only by tag links.

Return: the list of changed and created files, nothing else.

## References

- `/home/anton/Dev/@A/shatterlings/crates/specs/src/site.rs` — `tag_page` (line ~868): crumbs per prefix level, children tree, records table.
- `booping-python/e2e/cases/specs/site-renders-one-root-with-links-and-marks.txtar` — txtar case shape.

## Verify

`cd booping-python && uv run pytest tests/specs/site_pages_test.py e2e -k site -q`
