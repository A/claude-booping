---
id: "01"
title: "Review model — reasons, per-kind mark anchors, open items"
sp: 3
status: done
plan: "plans/202610160041_specs-site-landing-and-filters/index.md"
---

# M01: Review model — reasons, per-kind mark anchors, open items

The site knows, per record, why it needs the owner and where its first mark of each kind sits, and it can read the vault's open items — the data the review page, the landing and the list filters render.

**Scope**: `booping-python/src/booping/specs/site/state.py`, `booping-python/src/booping/specs/site/items.py` (new), `booping-python/src/booping/specs/site/pages.py` (signature only), `booping-python/src/booping/commands/specs.py`. `RecordState` gains `first_clarify` and `first_unknown` (`L{line}` of the first mark of that kind, `None` when none; `first_mark` stays) and `reasons: tuple[str, ...]` — the `flag` values of `../../clarifications.md` C3/C4 in the fixed order `unreviewed, clarify, unknown, conflict, proposed, open`: `conflict` for a `conflict` with `status: open`, `proposed` for an `adr` with `status: proposed`, `open` for an `idea` with `status: open`. New `items.py`: `OpenItem(id, title, record)` and `load_open_items(directory: Path) -> tuple[list[OpenItem], list[Warning]]` — parse every `OI-*.md` frontmatter in id order, keep `status: open`, `record` the raw ref string or `None`; a missing directory returns `([], [])`; an unparsable file is skipped with a site warning (same `Warning` type `build_site` returns). `build_site` gains keywords `open_items: list[OpenItem] = ()` and `items_root: str | None = None` — the name of the root an item's `record:` ref resolves from via `Site.resolve_ref` (consumed by the sidebar count in M03, the review page in M05 and the callout in M06); the reader's warnings join `build_site`'s. `_run_site` passes `load_open_items(ctx.vault / {core.specs.open_items.dir})` and `items_root` = the default root of the project tier only when no `--root` flag was given and `ctx.vault` is set, otherwise no items.

Tests (integration, `booping-python/tests/specs/site_state_test.py` new, `site_items_test.py` new): records built in a tmp tier through `load_site` — an unreviewed record with two clarify marks at known lines and one unknown gets `reasons == ("unreviewed", "clarify", "unknown")` and the hand-computed `L{n}` anchors; a reviewed `open` conflict gets `("conflict",)`; a reviewed `accepted` ADR gets `()`. Items: a tmp `open-items/` with an `open`, a `done` and a `planned` item yields only the open one; a missing directory yields `([], [])`; a file with unparsable frontmatter yields one warning naming it and no item.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Reasons and per-kind first-mark anchors on `RecordState`; tests. | `booping-python/src/booping/specs/site/state.py`, `booping-python/tests/specs/site_state_test.py` | 1 | done |
| 1.2 | Open-item reader, `build_site` keyword, wiring in `_run_site`; tests. | `booping-python/src/booping/specs/site/items.py`, `booping-python/src/booping/specs/site/pages.py`, `booping-python/src/booping/commands/specs.py`, `booping-python/tests/specs/site_items_test.py` | 2 | done |

## Definition of Done

### Task 1.1

- [x] `RecordState.reasons` follows C3/C4 and the fixed order; `first_clarify` / `first_unknown` point at the first mark of their kind.
- [x] Existing site tests and goldens unchanged (no rendered output changes in this milestone).

### Task 1.2

- [x] `load_open_items` returns only `status: open` items, in id order, and one warning per unparsable file; missing dir → no items, no warnings.
- [x] `_run_site` reads items only for default roots with a vault attached.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/src/booping/specs/site/state.py` — the dataclass being extended.
- `booping-python/src/booping/specs/open_items.py` — the item file format (do not import its CLI machinery; read frontmatter the way `site/model.py` reads records).
- `booping-python/tests/specs/site_pages_test.py` — tmp-tier fixture style.

## Verify

`cd booping-python && uv run pytest tests/specs/site_state_test.py tests/specs/site_items_test.py tests/specs/site_pages_test.py -q`
