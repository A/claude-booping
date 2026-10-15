---
title: "Specs site redesign, part 6 — whole-card links, compact filters, phone filter
  sheet"
type: "feature"
status: ready-for-dev
sp: null
related_to: null
created: 2026-10-16 05:04
planned: null
started: null
completed: null
code_reviews: []
sessions:
- e9aa21f3-03e1-4516-82ea-59c4a17dbabb
retro: null
summary: 'Specs site part 6: whole-card links, quiet ref line, compact chips, phone
  filter sheet with removable active chips'
commit: 4b72920370aa176886cc650ca93055ed6f937b6f
tracker_provider: null
tracker_request: null
tracker_issue: null
return_to: null
agents:
  research-codebase: ad63f4e30866a11ac
  cross-review: af8d081b83d831db1
reviewed_at: 2026-10-16 05:21
---

# Specs site redesign, part 6 — whole-card links, compact filters, phone filter sheet

## Context

- **Current state** — parts 1–5 of the specs-site redesign (`plans/202610152329_specs-site-redesign` … `plans/202610160336_specs-site-review-comments`, all done) ship list pages — `records.html`, per-type lists, tag pages, `review.html` — built from `record_row` / `item_row` and `filter_bar` (`booping-python/src/booping/specs/site/templates/_macros.html.j2`), filtered by `filter.js` with state in `location.hash`. The owner's phone screenshot of the swarmlight review page (`request.md`) shows three problems: only a card's title opens the record; four chip rows and a full-width sort select fill half the first screen; each card's ref sits on a filled bar (the bare `code` rule leaking onto `code.ref`).
- **Outcome** — a click or tap anywhere on a card opens its record while its text stays selectable; on phones the filters collapse into one `Filters (n) · {sort}` row opening a bottom sheet, with the active filters as small removable chips under it; chips are 30px tall at every width with ≥ 44px hit areas on touch; the ref reads as a small muted mono line as in the approved prototype.
- **Scope** — card ref and whole-card link (M01), compact chips and the sheet markup + CSS (M02), the sheet and active-chip behaviour (M03), then the runner's browser check. Defaults for every open call: `clarifications.md` C1–C6; request: `request.md`.

## Decisions

Values in play: value/0013 (guides to the goal) and value/0008 (effective human review) are the reason — the review page is where the owner works through records, and on a phone the records must come first; value/0003 (single source) keeps one set of chips in one `<dialog>` serving both the inline bar and the sheet, and every new string in config labels; the part-1 design rule "everything degrades without JS" keeps the inline bar and full lists when scripts are off; value/0015 and booping:rule/0027 — the generated HTML stays byte-stable, the new behaviour is client-side.

- **Breakpoint** (C1): the existing 760px phone breakpoint, not a new 640px one. [clarify] in C1.
- **Whole-card link** (C2): stretched `a.t::after` plus raised selectable text and a selection-aware click handler in `site.js`; the title link stays the only focusable element.
- **Compact row** (C3): one `button.filter-open` reading `{Filters}[ ({n})] · {sort option}`; labels `filters`, `filter_remove`, `filters_show` in both languages.
- **Active chips** (C4): phone-only, one removable chip per pressed chip, sort not a chip.
- **Chip metrics** (C5): 30px / 13px / 6px gap; a `(pointer: coarse)` `::before` hit area for ≥ 44px; sheet chips wrap.
- **Sheet** (C6): the chip groups and sort wrapped once in `dialog.filter-sheet`, a static inline block unless `html.js` at the phone breakpoint, where it opens via `showModal()` as a bottom sheet copied from `dialog.cmt-sheet`.
- **Ref** — fixed in CSS (`.ref` resets the `code` fill), not by changing markup: one rule fixes every `code.ref` surface the same way the prototype's `span.ref` looks.
- **Checks — partial departure from value/0010** — the compact-row text and the removable-chip list are built by a pure shipped `filter-format.js` under a node-run unit test (cross-review finding); the markup and labels are held by `site_pages_test.py` and the `site-*.txtar` goldens. The DOM wiring — card click-through, selection, sheet open/close, focus — has no browser runner in CI and is held by the workers' headless checks and the runner's browser check below, not by a committed test. [clarify] A committed Playwright suite would need Chromium in CI — not named in the source.
- **Snapshots**: no playbook source is edited, so `just snapshots` is expected clean. booping:rule/0013 says a run never accepts a baseline; the owner's standing permission for this feature (2026-10-14, restated in the invocation) **departs** from it: drift this plan describes may be accepted and is listed, report by report with the reason, in `develop-defaults.md` beside this `index.md` (written by the develop runner), any other drift stops the run. The `site-*.txtar` goldens are test fixtures each milestone rebaselines with `just e2e -k site --txtar-update` and reads.

## Architecture

```
templates/_macros.html.j2
   record_row / item_row        unchanged markup (code.ref, a.t | span.t)
   filter_bar (M02)             div.filters
                                  button.filter-open[data-label]
                                  div.filter-active[data-remove]
                                  dialog.filter-sheet
                                    div.filter-head {h2, button.filter-close}
                                    (p.facet + div.chips)*  label > select.sort
                                    button.filter-done
                                  p.count
                                p.empty
style.css   .ref reset, stretched card, card focus ring (M01)
            compact .chip + coarse hit area, inline sheet, phone row/sheet (M02)
site.js     selection-aware card click (M01)
filter-format.js  SpecsFilters.row / .removable — pure, node test (M03)
filter.js   row text, active chips, sheet open/close (M03) — hash format unchanged
pages.py    ships filter-format.js; filtered pages load it before filter.js (M03)
src/config.yaml  labels.{en,ru}.ui: filters, filter_remove, filters_show (M02)
```

`model.py`, `labels.py`, `search.*`, `comments*.js`, `index.json` and `llms.txt` do not change.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [Quiet ref line and whole-card link](milestones/M01-card-ref-and-whole-card-link/M01-card-ref-and-whole-card-link.md) | 3 | pending |
| 02 | [Compact chips and the filter sheet markup](milestones/M02-compact-chips-and-filter-sheet-markup/M02-compact-chips-and-filter-sheet-markup.md) | 4 | pending |
| 03 | [Filter sheet, compact row and removable chips behaviour](milestones/M03-filter-sheet-behaviour/M03-filter-sheet-behaviour.md) | 4 | pending |

## Milestone files

Each milestone directory under `milestones/` holds its file with goal, scope, tasks, DoD, references and Verify; this index is context only.

## Final Verification

- [ ] `just ci` green, run once at the end in the foreground.
- [ ] `just snapshots` clean (no playbook source touched); any drift handled per Decisions → Snapshots.
- [ ] Browser check by the runner: build `bin/booping specs site --out /tmp/specs-site-booping` from the repo and the Russian fixture (`~/.tmp/specs-site-fixtures/swarmlight/vault` copied to `/tmp`, `bin/booping specs site --out /tmp/specs-site-ru`); a throwaway Playwright script (`uv run --with playwright python /tmp/filter-check.py`, the system Chromium via `executable_path`) screenshots over `file://` at 390×2400 with touch emulation: (a) `review.html#flag=unreviewed` on the Russian site, (b) a type list page (`adr/index.html`), (c) the review page with the filter sheet open; and at 1300×2200: (d) the review page, (e) the type list page. The runner looks at all five and compares (a) with the owner screenshot (`/tmp/claude-1000/-home-anton-Dev--A-hermes-pet/36dbf90d-0102-4f43-add1-4a69775c2e2f/scratchpad/site/owner-phone-review.jpg`). Pass when: at 390 the first card starts within the first screen (≤ 844px from the top) under the compact row, the active chip and the count line; the ref is a plain muted line above the title; the sheet is a bottom sheet with wrapping chip groups and the sort; no horizontal scroll; at 1300 the inline bar shows 30px chips and the ref column has no fill; a click on a card's summary opens the record.
- [ ] Typecheck clean (`just typecheck`, inside `just ci`).

## Accessibility & interaction

- [ ] Keyboard paths: Tab → each card's title link (focus ring on the card) → Enter opens; phone: Tab → `Filters` row → Enter opens the sheet → Tab through chips, sort, Show records, close → Escape closes; Tab → each removable chip → Enter removes it, focus moves to the next one or the row.
- [ ] Labels: the row's text names count and sort; removable chips carry `Remove filter: {label}`; the close button `close`; the sheet `aria-label` `filters`; chip groups keep their `role="group"` labels; pressed state stays `aria-pressed`.
- [ ] Focus: `showModal()` traps focus and inerts the page; on close focus returns to the row.
- [ ] Announcements: the existing `.count` `role="status"` line announces the shown count after each change.
- [ ] Reduced motion: the sheet's slide-up is off under `prefers-reduced-motion`.

## Responsive & cross-browser

- [ ] ≥ 761px, and any width without JS: inline filter bar (chip groups, sort, count) as today, compact chips.
- [ ] ≤ 760px with JS: compact row, active-chip row, count line, then cards; the sheet as a bottom sheet, `max-height: 80vh`, inner scroll; tap targets ≥ 44px under `(pointer: coarse)`.
- [ ] Verified in Chromium at 1300 and 390 (Final Verification); `:has()` and `:modal` are in every current engine — without `:has()` the card focus ring falls back to the link's own ring.

## Out of scope

- Facet or sort changes, the hash format, filters on the home page.
- A committed browser test suite (Decisions → Checks).
- Restyling the record page itself beyond the shared `.ref` reset.

## CLAUDE.md impact

No CLAUDE.md changes required — the site's pages and assets are not described there; no command, layout or convention changes.
