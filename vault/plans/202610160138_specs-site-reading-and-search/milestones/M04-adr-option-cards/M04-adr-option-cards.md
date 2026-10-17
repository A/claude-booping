---
id: "04"
title: "ADR option cards"
sp: 4
status: done
plan: "plans/202610160138_specs-site-reading-and-search/index.md"
---

# M04: ADR option cards

An ADR's alternatives read as option cards: the chosen one first and open with a "chosen" badge, the rest collapsed, the summary table marking the chosen row and giving way to the cards on the phone.

**Scope**: new `booping-python/src/booping/specs/site/adr.py` (a token pass `option_cards(tokens, labels) -> list[Token]` run by `render_body` when called with `alternatives=True`: finds `## Alternatives`, reads its table rows into `{anchor: Row(status, complexity, reversibility, verdict)}`, marks accepted rows `chosen`, wraps each `###` section in `details`/`summary`/`div.in` tokens with the `.meta` row and verdict, reorders accepted sections first; returns the tokens untouched when the shape does not match), `markdown.py` (the `alternatives` flag and the `alts` table class), `pages.py` (`_render` passes `alternatives=record.type == "adr"`), `style.css` (`.alts tr.chosen`, `.opt .meta`, `.verdict`, table hidden below 760px; the existing `.opt` rules), `src/config.yaml` (`complexity`, `reversibility`, `level_low`, `level_medium`, `level_high` in `en` and `ru`). Exactly `../../clarifications.md` C5. The option `h3` keeps its id and M01's `§` anchor; `Rendered.headings` and marks are unaffected.

Tests (integration, new `booping-python/tests/specs/site_adr_test.py` via `render_body`): an ADR body with three options, the second `accepted`, renders the table with the accepted row `chosen` and badged, then cards in the order accepted, first, third, only the accepted one `open` and `chosen`, each card's meta and verdict from its row, and the `**Pros:**` bullets inside `.in`; an option section without a table row gets a card with no meta; a body with no `## Alternatives` and an Alternatives section without a table render byte-identical to `alternatives=False`; a non-ADR record is never transformed. Rebaseline `site-*.txtar` goldens and read the diff: ADR pages only.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | `adr.py` token pass, the `alternatives` flag in `render_body`; tests. | `booping-python/src/booping/specs/site/adr.py`, `booping-python/src/booping/specs/site/markdown.py`, `booping-python/tests/specs/site_adr_test.py` | 3 | done |
| 4.2 | Wire in `_render`; CSS; labels; golden rebaseline. | `booping-python/src/booping/specs/site/pages.py`, `booping-python/src/booping/specs/site/style.css`, `src/config.yaml`, `booping-python/e2e/cases/specs/site-*.txtar` | 1 | done |

## Definition of Done

### Task 4.1

- [x] Cards, order, `open`, `chosen`, meta and verdict match C5 on the test fixtures.
- [x] Any non-matching shape renders exactly as with `alternatives=False` — no exception, no warning.
- [x] Table links `#anchor` still land on the option `h3` ids.

### Task 4.2

- [x] Only `adr` records get cards; level and name labels resolve in `en` and `ru`.
- [x] Below 760px the `alts` table is hidden and the cards fill the width; new colours use existing tokens only (`site_contrast_test.py` green).
- [x] `site-*.txtar` goldens rebaselined; their diff touches ADR record pages only.

Return: the list of changed and created files, nothing else.

## References

- `src/specs/schemas/adr.yaml` — the Alternatives table columns, status and level enums, the `###` option shape.
- `../../../202610152329_specs-site-redesign/design/specs-site-mockup.html` — `opt()` markup and `.opt` CSS.
- `vault/adr/0001-specs-tiers.md` — a real ADR to render and look at.

## Verify

`cd booping-python && uv run pytest tests/specs/site_adr_test.py tests/specs/site_contrast_test.py e2e -k site -q`
