---
id: "02"
title: "Tag model — per-root tree from tags.yaml and used tags"
sp: 3
status: pending
plan: "plans/202610160041_specs-site-landing-and-filters/index.md"
---

# M02: Tag model — per-root tree from tags.yaml and used tags

The site builds each root's tag tree with descriptions and descendant-inclusive counts — the data the tag pages and the sidebar render.

**Scope**: `booping-python/src/booping/specs/site/tags.py` (new). `TagNode(tag, description, count, children: tuple[TagNode, ...])` and `tag_tree(root: SiteRoot, records: list[SiteRecord]) -> tuple[list[TagNode], list[Warning]]` implementing `../../clarifications.md` C7 exactly: nodes = `booping.specs.tags.load(root.path)` keys ∪ tags the root's records carry ∪ their ancestors; children one `:` segment deeper; order by tag id; count = records of that root carrying the tag or any descendant; description from the dictionary or `""`; `MalformedDictionary` → one warning on `{root.path}/tags.yaml`, tree from used tags. Also `tagged(tag, records) -> list[SiteRecord]` (descendant-inclusive, page order) and `tag_page_path(root, tag) -> str` = `{root}/tags/{tag with ':' → '.'}.html`. A record's `tags:` that is not a list of strings is ignored for the tree (the checker reports it). Pure functions, no rendering.

Tests (integration, `booping-python/tests/specs/site_tags_test.py` new): a tmp tier with `tags.yaml` `{a: A, a:b: AB}` and records tagged `[a:b]`, `[a:b:c]`, `[x]` — tree `a(2) → a:b(2) → a:b:c(1)`, `x(1)` with empty description, order by id; `tagged("a")` returns both `a:*` records; no `tags.yaml` → tree from used tags; a malformed `tags.yaml` → one warning and the used-tag tree; `tag_page_path` for `a:b:c` is `{root}/tags/a.b.c.html`.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | `tag_tree`, `tagged`, `tag_page_path`; tests. | `booping-python/src/booping/specs/site/tags.py`, `booping-python/tests/specs/site_tags_test.py` | 3 | pending |

## Definition of Done

### Task 2.1

- [ ] Tree, counts, order and fallbacks match C7 on the test cases above.
- [ ] Output is deterministic for the same input (no set iteration order leaks).

Return: the list of changed and created files, nothing else.

## References

- `booping-python/src/booping/specs/tags.py` — `load`, `MalformedDictionary`, the tag regex.
- `/home/anton/Dev/@A/shatterlings/crates/specs/src/site.rs` — `tag_tree` (line ~831) and `tagged` (line ~862), the algorithm being ported.

## Verify

`cd booping-python && uv run pytest tests/specs/site_tags_test.py -q`
