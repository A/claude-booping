---
id: "03"
title: "Theme and icons — mockup tokens, reading typography, SVG sprite"
sp: 4
status: pending
plan: "plans/202610152329_specs-site-redesign/index.md"
---

# M03: Theme and icons — mockup tokens, reading typography, SVG sprite

The site's stylesheet becomes the approved mockup's reading-first design — its palette tokens in light and dark, the brief's type scale and measure, badges, chips, rows, facts and the phone layout — and every page can draw state icons from one inline SVG sprite.

**Scope**: the visual source of truth is the approved mockup `../../design/specs-site-mockup.html` (its `<style>` block and the `<svg>` sprite at its top); the owner's typography numbers are in `../../clarifications.md` C1 and `../../index.md` Decisions. Rewrite `booping-python/src/booping/specs/site/style.css`: the mockup's custom properties verbatim (`--bg --surface --sunk --text --muted --faint --line --link --link-bg --ok --ok-bg --warn --warn-bg --bad --bad-bg --info --info-bg --idle --idle-bg --sans --mono`), light on `:root`, dark on `:root[data-theme="dark"]` and on `:root:not([data-theme="light"])` inside `@media (prefers-color-scheme: dark)`, `color-scheme` per theme (C8); body 17px/1.6 `var(--sans)`, H1 28/1.3, H2 22/1.35, H3 18/1.4, meta and chips 13/1.4, code 15/1.5 `var(--mono)`, `.lead` 19/1.55 muted, `.measure` max 68ch, 4px spacing unit, paragraph gap 1em, section gap 2.5em; layout classes the mockup uses (`.top .body .side main .rail .crumbs .badges .b .b.ok .b.warn .b.bad .b.info .b.idle .b.plain .chip .rows .row .facts .mark .opt .drawer .scrim .skip`), the grid `232px minmax(0,1fr) 210px` with `.norail`; the mockup's `@container (max-width: 760px)` rules become `@media (max-width: 760px)` (a real site has no resizable container): one column, sidebar and rail hidden behind the drawer, H1 24px, lead 17px, rows stacked with the ref first, facts one column, crumbs show the last level only, no horizontal scroll (`overflow-wrap: anywhere` on code and refs, tables inside `.table-wrap` scroll only themselves); `html:not(.js)` narrow layout shows `.side` in flow after `main` (C7); focus rings visible (`:focus-visible` 2px `var(--link)` outline); tap targets ≥ 44px on narrow screens; `@media (prefers-reduced-motion: reduce)` drops the drawer transition. New partial `templates/_icons.html.j2`: one `<svg aria-hidden="true" style="display:none">` holding the mockup's 11 `<symbol>`s with their ids (`i-accepted i-open i-planned i-rejected i-clarify i-unknown i-unreviewed i-reviewed i-menu i-search i-moon`) plus `i-sun` and `i-auto` drawn in the same 16×16 stroke style for the theme states. `_macros.html.j2` gains `icon(id)` (`<svg class="ic" aria-hidden="true"><use href="#{id}"/></svg>`) and `state_badges(state, labels, hide_unreviewed=false)` — status badge (status icon + status label, class from the mockup's `STATUS` map: accepted/done/live/resolved → ok, proposed/planned/validating → warn, open → info, rejected/retired/superseded/deferred → plain), clarify badge (`i-clarify` + `labels.plural("clarify", n)`, class warn), unknown badge (`i-unknown` + `ui("unknown")`, class bad), unreviewed (`i-unreviewed` + `ui("unreviewed")`, class plain) — text always beside the icon, badges never links. `state` is the mapping M05 adds; this milestone defines the macro against the keys `status`, `clarify`, `unknown`, `unreviewed` and pages call it from M05 on.

Tests (integration, `booping-python/tests/specs/site_pages_test.py`): the rendered `_icons.html.j2` holds 13 `<symbol>`s with unique ids; `state_badges` rendered through `environment()` for `{status: accepted, clarify: 3, unknown: 1, unreviewed: true}` in ru yields four badges in that order, each with an `<svg>` and non-empty text; `style.css` contains every token name above in both themes. Contrast: create `booping-python/tests/specs/site_contrast_test.py` computing WCAG contrast from the hex tokens in `style.css` — text, muted, link and each badge foreground on its background, both themes, ≥ 4.5:1; body text on bg ≥ 7:1 in dark.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | `style.css` rewrite from the mockup tokens and the type scale, phone rules, no-JS narrow fallback, focus and motion rules; the contrast test. | `booping-python/src/booping/specs/site/style.css`, `booping-python/tests/specs/site_contrast_test.py` | 3 | pending |
| 3.2 | `_icons.html.j2` sprite, `icon` and `state_badges` macros, their tests. | `booping-python/src/booping/specs/site/templates/_icons.html.j2`, `booping-python/src/booping/specs/site/templates/_macros.html.j2`, `booping-python/tests/specs/site_pages_test.py` | 1 | pending |

## Definition of Done

### Task 3.1

- [ ] Every token of the mockup's `:root` appears in `style.css` with the mockup's value, in both themes.
- [ ] `uv run pytest tests/specs/site_contrast_test.py -q` passes.
- [ ] No `system-ui` anywhere in `style.css`; monospace only on code, refs and the `kbd` hint.

### Task 3.2

- [ ] Every icon pairs with text in `state_badges`; no colour-only state.
- [ ] The new tests in `site_pages_test.py` pass.

Return: the list of changed and created files, nothing else.

## References

- `../../design/specs-site-mockup.html` — the approved visual reference (tokens, sprite, classes).
- `booping-python/src/booping/specs/site/templates/_macros.html.j2` — existing macro shape.

## Verify

`cd booping-python && uv run pytest tests/specs -k "site" -q`
