---
id: "08"
title: "Phone cards and chip styling"
sp: 2
status: pending
plan: "plans/202610160041_specs-site-landing-and-filters/index.md"
---

# M08: Phone cards and chip styling

Below 760px list rows read as cards and the filter bar fits one line; chips have their mockup look in both themes.

**Scope**: `booping-python/src/booping/specs/site/style.css`, `booping-python/tests/specs/site_contrast_test.py`. Per `../../clarifications.md` C10 and the mockup: `.chip` (pill, 13/1.4 meta size, icon + label + tabular-nums count, `aria-pressed="true"` filled with an accent token pair, `:focus-visible` ring), `.chips` group spacing, `.sort`, `.count`, `.empty`, `.tag-tree` nesting indent. Inside the existing 760px media query: `.row` becomes a card (border `--border`, radius, 12px padding, one column, `.ref` first, then title, badges, summary), `.filters` chips on one line with `overflow-x: auto` and hidden scrollbar, `.sort` full width, `.scen` one column, chips and rows ≥ 44px tall. Colour tokens: chips reuse `--text`/`--muted` on `--surface` with `--border`; the pressed chip adds exactly two new tokens, `--chip-on-bg` and `--chip-on-text`, each with light and dark values (mockup's pressed chip), and the pair joins `site_contrast_test.py` (≥ 4.5:1) in the light, dark and dark-auto blocks. No other new token.

Tests (integration): `site_contrast_test.py` extended with every new text/background pair, both themes. Goldens are unaffected (CSS file only; rebaseline the txtar cases embedding `style.css` if they do, and read that the diff is CSS only).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 8.1 | Chip, sort, count, tag-tree styles; phone card rules; contrast pairs. | `booping-python/src/booping/specs/site/style.css`, `booping-python/tests/specs/site_contrast_test.py` | 2 | pending |

## Definition of Done

### Task 8.1

- [ ] At 390px wide no page scrolls horizontally; rows render as cards; chips scroll in one line (runner checks in Final Verification).
- [ ] Every new colour pair is ≥ 4.5:1 in both themes, asserted by the contrast test.
- [ ] `prefers-reduced-motion` respected for any new transition.

Return: the list of changed and created files, nothing else.

## References

- `../../../202610152329_specs-site-redesign/design/specs-site-mockup.html` — `.chip`, `.chips`, `@container (max-width: 760px)` rules.
- `booping-python/tests/specs/site_contrast_test.py` — how token pairs are listed.

## Verify

`cd booping-python && uv run pytest tests/specs/site_contrast_test.py e2e -k site -q`
