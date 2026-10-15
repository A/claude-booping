# Clarifications

## C1 — phone breakpoint — answered

**Asked:** 2026-10-16 — intake

**Question:** The request says "on phones (≤640px)"; the site has exactly one phone breakpoint, `max-width: 760px` in `style.css` ("Phone: one breakpoint"), where rows already become cards and the comment panels become bottom sheets. Collapse the filters at 640px or at 760px?

**Answer:**

Default (autonomous run): 760px, the existing breakpoint. A second phone breakpoint would leave a 641–760px band with phone cards but desktop filters, and the comment sheets already switch at 760px; the owner's intent is "on phones", which the 760px band covers. [clarify] If the owner wants the filter collapse only at ≤640px, it is a one-line media query change.

## C2 — whole-card link with selectable text — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** A pure-CSS stretched link (`.t::after { inset: 0 }`) makes the card's text unselectable; the request wants both. Which mechanism?

**Answer:**

Default (autonomous run): the hybrid "inclusive card" pattern. `.row` is `position: relative`; the title link `a.t` carries a `::after` covering the card (native link for clicks on padding and gaps, middle/ctrl-click included). The ref, summary and badge area sit above it (`position: relative; z-index: 1`) so their text is selectable, and the mark links inside the badges stay their own links. A small script in `site.js` (loaded on every page) makes a click on that raised text open the record — only when it is a primary-button click, the target is not inside an `a`/`button`, and the selection is collapsed (no text was selected); ctrl/meta-click opens it in a new tab. The title link stays the only focusable element of the card (keyboard path unchanged; focus ring drawn on the card via `.row:has(a.t:focus-visible)` with the link's own ring as fallback). A row without a page (`item_row` with no `page`) is not clickable. Without JS: clicks on padding and title navigate, clicks on text select.

## C3 — compact filter row content — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** Exact content of the compact row (booping:rule/0010 — UI text locked in grooming)?

**Answer:**

Default (autonomous run). One button, `button.filter-open`, text:

- `{filters}` when no chip is pressed, `{filters} ({n})` otherwise — `n` = number of pressed chips across all facets;
- then ` · ` and the selected sort option's own text (e.g. `Filters (1) · Review order`, `Фильтры (1) · Для ревью`).

New config labels `core.specs.site.labels.{en,ru}.ui`: `filters` (`Filters` / `Фильтры`), `filter_remove` (`Remove filter: {label}` / `Убрать фильтр: {label}`) for the removable chips' aria-label, `filters_show` (`Show records` / `Показать записи`) for the sheet's done button. The sheet heading reuses `filters`; its close button reuses `close`. The count line ("79 records shown") stays visible on the page under the active chips.

## C4 — active-filter chips — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** What do the removable chips under the compact row show, and where do they appear?

**Answer:**

Default (autonomous run): one `button.chip.chip-x` per pressed chip, in facet then chip order, text = the chip's label without its count, followed by a `×` glyph (`aria-hidden`); `aria-label` from `filter_remove`. Clicking one un-presses the matching chip, re-applies and rewrites the hash. They appear only at the phone breakpoint with JS (the desktop filter bar already shows pressed chips in place); none pressed → the line is empty and takes no space. Sort is not shown as a chip (it is in the button text).

## C5 — chip size and hit area — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** Exact chip metrics at every width?

**Answer:**

Default (autonomous run): `min-height: 30px`, `padding: 2px 10px`, `font-size: 13px` (brief's meta/chips 13/1.4), `gap: 4px` inside, `6px` between chips. The ≥44px tap target comes from an invisible `::before` hit area (`position: absolute; inset: -7px -2px`) under `@media (pointer: coarse)`, the same media query the comment panels use; the phone rule `.chip { min-height: 44px }` is removed. In the phone sheet the chip groups wrap (`flex-wrap: wrap`, row gap 14px so hit areas do not overlap) instead of scrolling sideways, each under its facet label as a small heading.

## C6 — sheet mechanics — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** How does one set of chips serve both the inline desktop bar and the phone sheet without duplicating markup or moving DOM?

**Answer:**

Default (autonomous run): the chip groups and the sort label are wrapped once in `<dialog class="filter-sheet">` inside `.filters`. CSS shows that dialog as a static inline block at every width (`display: block; position: static`, dialog chrome reset) — so without JS, and with JS on desktop, the bar looks as today. Only under `html.js` at the phone breakpoint is a closed `.filter-sheet` hidden, the compact row shown, and an open one styled as the bottom sheet (`max-height: 80vh`, rounded top, `::backdrop` dimmed, slide-up off under `prefers-reduced-motion`), copying `dialog.cmt-sheet`. `filter.js` opens it with `showModal()`, closes it on the close button, the "Show records" button, Escape and a backdrop click, returns focus to `button.filter-open`, and closes it when the breakpoint media query stops matching. Chip presses inside the open sheet apply live (count line and list update behind it). Filter state stays in `location.hash` as today; the sheet's open state is not stored.

## C7 — cross-review dispositions — answered

**Asked:** 2026-10-16 — cross-review

**Question:** How are the cross-review findings (codex) disposed of?

**Answer:**

Default (autonomous run):

- CRITICAL `p.empty` lookup — folded in: M02 now keeps `p.empty` as the next sibling after `div.filters`, where `filter.js` finds it; M03 names that lookup as unchanged.
- RISK no committed check — folded in partly: M03 adds the pure `filter-format.js` (row text, removable-chip list) under a node-run unit test (+1 SP); the DOM wiring stays held by headless checks, recorded as a departure from value/0010 in `index.md` Decisions.
- RISK breakpoint 759 vs 760 — not folded: the phone block the plan targets is `@media (max-width: 760px)`; only `dialog.cmt-sheet` uses `759px`/`760px` min. The new rules use the phone block's `760px`.
- RISK defaults file — folded in: `index.md` names `develop-defaults.md` beside the plan as the place accepted snapshot drift is listed.
