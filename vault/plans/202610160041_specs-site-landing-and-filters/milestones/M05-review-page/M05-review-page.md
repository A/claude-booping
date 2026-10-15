---
id: "05"
title: "Review page — the needs-you pool as a filtered list"
sp: 3
status: done
plan: "plans/202610160041_specs-site-landing-and-filters/index.md"
---

# M05: Review page — the needs-you pool as a filtered list

`review.html` lists every record and open item that needs the owner, each row showing why by icon and linking straight to its marks, with the review chips and sort.

**Scope**: `booping-python/src/booping/specs/site/templates/review.html.j2` (new), `_macros.html.j2`, `pages.py`, `src/config.yaml` labels. Per `../../clarifications.md` C4: the pool is the records with non-empty `reasons` in `records.html` order, then the open items (M01) in id order. Record rows use `record_row`; their badges carry the reasons — the clarify badge links `{record page}#{first_clarify}`, the unknown badge links `{record page}#{first_unknown}` (extend `state_badges` with an `unknown_href` the way `clarify_href` works). Item rows (`item_row` macro): `<code class="ref">` the item id, the title linked to the record page `Site.resolve_ref(item.record, items_root)` returns (M01), unlinked when it returns nothing, `data-flags="open"`, `data-source=""`, `data-type=""`, `data-status="open"`, `data-order` continuing the record count. Filter bar (M04) with facets `type`, `source`, `flag` — `flag` values `unreviewed, clarify, unknown, conflict, proposed, open` — and the sort options `review` (default), `number`, `updated`, `title`; `data-default-sort="review"`. Head: H1 "Needs you" label, a lead line (label: claude-written first, then oldest). Empty pool: the empty-state paragraph visible server-side ("Nothing needs you"). Crumbs Overview › Review. Drop the M03 `_Links` checker exclusion for `review.html`.

Tests (integration, `site_pages_test.py`): a fixture with an unreviewed record, a reviewed record with an unknown mark at a known line, a reviewed accepted ADR and one open item — `review.html` holds exactly three rows (the ADR absent), the unknown badge's href ends `#L{line}` and resolves (the `_Links` checker), the item row links its record; the flag facet shows chips only for present reasons with hand-derived counts; the sidebar Review count equals the row count. Rebaseline `site-*.txtar` goldens and read the diff: `review.html` added.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Review pool, `review.html`, item rows, unknown-badge link; labels. | `booping-python/src/booping/specs/site/templates/review.html.j2`, `booping-python/src/booping/specs/site/templates/_macros.html.j2`, `booping-python/src/booping/specs/site/pages.py`, `src/config.yaml` | 2 | done |
| 5.2 | Tests; golden rebaseline. | `booping-python/tests/specs/site_pages_test.py`, `booping-python/e2e/cases/specs/site-*.txtar` | 1 | done |

## Definition of Done

### Task 5.1

- [x] `review.html` lists the C4 pool with reasons shown as icon + text and mark links resolving to `L{line}` anchors.
- [x] `filter.js` sorts the page by `review` order when no `sort` is in the hash.

### Task 5.2

- [x] Tests above pass; goldens differ only by the new page.

Return: the list of changed and created files, nothing else.

## References

- `../../../202610152329_specs-site-redesign/design/specs-site-mockup.html` — `list(review=true)`: head copy, `.why` badges, empty state.
- `booping-python/src/booping/specs/site/templates/root.html.j2` — `#L{n}` mark links across pages.

## Verify

`cd booping-python && uv run pytest tests/specs/site_pages_test.py e2e -k site -q`
