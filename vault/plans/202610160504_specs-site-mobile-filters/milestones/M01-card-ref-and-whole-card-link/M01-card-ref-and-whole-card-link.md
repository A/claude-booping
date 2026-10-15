---
id: "01"
title: "Quiet ref line and whole-card link"
sp: 3
status: pending
plan: "/home/anton/Dev/@A/claude-booping-specs/vault/plans/202610160504_specs-site-mobile-filters/index.md"
---

# M01: Quiet ref line and whole-card link

A record card in every list opens its record from a click anywhere on it, its text stays selectable, and its ref reads as a small muted mono line instead of a filled bar.

**Scope**: `booping-python/src/booping/specs/site/style.css`, `booping-python/src/booping/specs/site/site.js`, the `booping-python/e2e/cases/specs/site-*.txtar` goldens. Behaviour exactly `../../clarifications.md` C2:

- Ref: add `background: none; padding: 0; border-radius: 0;` to the `.ref` rule so `code.ref` stops inheriting the bare `code` fill on every surface (cards, Recently updated, relation lists, comment groups) — the prototype's `.ref { font: 13px/1.4 var(--mono); color: var(--muted) }`. Markup stays `<code class="ref">`. Card layout unchanged: desktop keeps the 96px ref column, phone keeps `.row .ref { order: -1 }` (the line above the title).
- Stretched link: `.row { position: relative; }`; `.row a.t::after { content: ""; position: absolute; inset: 0; }`; `.row .ref, .row .s, .row .why { position: relative; z-index: 1; }` so their text is selectable and the mark links inside `.why` keep working; `.row:has(a.t[href]) { cursor: pointer; }`; focus: `.row:has(a.t:focus-visible) { outline: 2px solid var(--link); outline-offset: 2px; }` and `.row a.t:focus-visible { outline: none; }` inside a `@supports selector(:has(*))` block (the link's own ring stays outside it).
- `site.js`: one delegated `click` listener on `document` — when the target is inside a `.row` that holds `a.t[href]`, is not inside an `a`, `button`, `input`, `select` or `textarea`, `event.button === 0`, and `getSelection().isCollapsed` → `ctrlKey`/`metaKey` opens the link's `href` with `window.open(href, "_blank", "noopener")`, otherwise `location.assign(href)`. Rows with `span.t` (open items without a page) are untouched.

Tests: no pytest change — CSS and a DOM handler; the `site-*.txtar` goldens change only in the shipped `style.css` and `site.js` bodies. The click paths are held by the worker's headless check (DoD) and the runner's browser check (index Final Verification).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Quiet `.ref`: drop the inherited `code` fill. | `booping-python/src/booping/specs/site/style.css` | 1 | pending |
| 1.2 | Stretched title link, raised selectable text, card focus ring, selection-aware click handler; golden rebaseline. | `booping-python/src/booping/specs/site/style.css`, `booping-python/src/booping/specs/site/site.js`, `booping-python/e2e/cases/specs/site-*.txtar` | 2 | pending |

## Definition of Done

### Task 1.1

- [ ] In headless Chromium on a built site (`bin/booping specs site --out /tmp/specs-site-booping`), the computed `background-color` of `.row .ref` is transparent and its `padding` 0 on `records.html` at 390px and 1300px.

### Task 1.2

- [ ] On `records.html` at 390px and 1300px: a click on a card's summary text navigates to that record; a click on the card's padding navigates; a click on a `[clarify]` mark link on `review.html` lands on that mark's anchor; a drag-selection over the summary text selects it and does not navigate.
- [ ] Tab reaches each card's title link once and the card shows the focus ring; Enter opens the record.
- [ ] `site-*.txtar` rebaselined with `just e2e -k site --txtar-update`; diff limited to the `style.css` and `site.js` bodies.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/src/booping/specs/site/site.js` — existing delegated listeners and the `html.js` convention.
- `/tmp/claude-1000/-home-anton-Dev--A-hermes-pet/36dbf90d-0102-4f43-add1-4a69775c2e2f/scratchpad/site/specs-site-mockup.html` — `.ref` (line 30) and `.row` (lines 106–111, 146–149): the approved look.
- `../../clarifications.md` — C2.

## Verify

`cd booping-python && uv run pytest tests/specs/site_pages_test.py e2e -k site -q`
