---
title: "Specs site redesign, part 2 — landing, review filter, list filters, tags"
type: "feature"
status: presenting
sp: null
related_to: null
created: 2026-10-16 00:42
planned: null
started: null
completed: null
code_reviews: []
sessions:
- c310b57e-c84e-4872-9b76-858b73cd43c6
retro: null
summary: 'Specs site part 2: landing with one needs-you link, review filter, list
  chips+sort in location.hash, Source facet, tag pages, phone cards'
commit: 6b1712be5b1951e11a5af9a460858794ffe679f3
tracker_provider: null
tracker_request: null
tracker_issue: null
return_to: null
---

# Specs site redesign, part 2 — landing, review filter, list filters, tags

## Context

- **Current state** — part 1 (`plans/202610152329_specs-site-redesign`, done) shipped the mockup's shell, theme, fonts, record page head with state badges, plain list pages and the machine layer. The home page is an H1 plus per-root type lists, type pages are unfiltered row lists, nothing gathers what needs the owner, tags are plain text, and the tier sits at the top of the navigation.
- **Motivation** — the owner's brief (`../202610152329_specs-site-redesign/design/brief.md`): the site is documentation; home is a landing with ONE «N need you →» link, review is a filter over the list with a reason icon per row and a link to the mark, and the phone layout is thought through. The base spec (`design/specs-site-design.md`) adds hash-state filters, the Source facet and tag pages from `tags.yaml`.
- **Scope** — part 2 of three (`clarifications.md` C1): landing, review filter, list chips and sort with `location.hash` state, the Source facet, phone cards, tag tree and tag pages. Part 3 and the skipped priority 3 are under Out of scope.

## Decisions

Values in play: value/0013 (guides to the goal) and value/0008 (effective human review) drive the single needs-you link, the review pool and rows that say why they are listed; value/0015 (deterministic where it can be) and booping:rule/0027 keep server-rendered chips, counts and order byte-stable, with JS only re-arranging what the HTML already holds; value/0005 (stack-agnostic core) keeps every label in config and the hash format host-free; value/0002 (minimal effective context) leaves the machine layer as it is.

- **Source precedence**: brief > mockup > base spec, design files referenced from part 1's plan, not copied (C1, value/0003).
- **New pages beside part 1's paths**: `records.html`, `review.html`, `{root}/tags/…` (C2) — existing links survive; tags stay per root because each tier owns its `tags.yaml`.
- **Facets OR within, AND across; one `flag` key; hash format locked** (C3, booping:rule/0010). **Departs** from the base spec's per-flag keys (`#status=open&unreviewed=1`) so OR-within holds for flags too, and from the mockup's flat AND, which makes two status chips always empty.
- **Server-rendered chips and counts** (C3) — counts independent of other active chips, as in the mockup; the page reads fully without JS (base spec constraint).
- **Review pool and reasons** (C4): records with any reason plus open items; mark links use part 1's `L{line}` anchors. **Departs** from the mockup's pre-selected "unreviewed" chip — the page is already the pool.
- **Landing exactly as C5**; the lead shares `llms.txt`'s source (value/0003).
- **Sidebar per C6** — the base spec's groups; tiers become Sources.
- **Tag tree = dictionary ∪ used tags ∪ ancestors, descendant-inclusive counts** (C7), ported from shatterlings `tag_tree`/`tagged`.
- **No tag facet on lists** (C8) — **departs** from the base spec; tag pages carry tag navigation.
- **`filter.js` verified in the browser, not in `just ci`** (C9) — CI stays Python-only; pytest owns the data the script reads.
- **Phone cards on part 1's 760px breakpoint** (C10).
- **Snapshots**: no playbook source is edited, so `just snapshots` is expected clean; booping:rule/0013 holds — any drift is reported, and only drift this plan describes may be accepted under the owner's standing permission for this feature (2026-10-14). The txtar goldens under `booping-python/e2e/` are test fixtures rebaselined by the milestones that change output, each diff read against the milestone's stated pages.

## Architecture

```
commands/specs.py  _run_site ── open items from {vault}/{core.specs.open_items.dir} (default roots only)  (M01)
        │
        ▼
site/state.py   RecordState + reasons, first_clarify, first_unknown          (M01)
site/items.py   load_open_items → [OpenItem]                                  (M01)
site/tags.py    tag_tree, tagged, tag_page_path                               (M02)
        │
        ▼
site/pages.py   build_site(…, open_items)
   ├─ nav: Overview · Review(N) · All records · Types · Tags · Sources · llms.txt   (M03)
   ├─ _macros: record_row (data-*), item_row, filter_bar, tag_tree             (M03 M04 M05 M07)
   ├─ records.html (M03) · type pages + filter bar (M04) · review.html (M05)
   ├─ index.html landing (M06) · {root}/tags/index.html, {root}/tags/{a.b}.html (M07)
   ├─ filter.js — hash ⇄ chips/sort, OR-within/AND-across, live count          (M04)
   └─ style.css — chips, cards at 760px, contrast pairs                        (M06 M08)
```

Rows carry `data-type data-source data-status data-flags data-updated data-title data-created-by data-order`; `filter.js` reads only those. `site-index` is untouched.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [Review model — reasons, per-kind mark anchors, open items](milestones/M01-review-model/M01-review-model.md) | 3 | pending |
| 02 | [Tag model — per-root tree from tags.yaml and used tags](milestones/M02-tag-model/M02-tag-model.md) | 3 | pending |
| 03 | [List rows with data attributes, All records page, sidebar](milestones/M03-list-rows-and-all-records/M03-list-rows-and-all-records.md) | 4 | pending |
| 04 | [Filter bar — chips, sort, hash state in filter.js](milestones/M04-filter-bar/M04-filter-bar.md) | 4 | pending |
| 05 | [Review page — the needs-you pool as a filtered list](milestones/M05-review-page/M05-review-page.md) | 3 | pending |
| 06 | [Home landing — lead, needs-you callout, scenarios, recently updated](milestones/M06-home-landing/M06-home-landing.md) | 3 | pending |
| 07 | [Tag pages — tag tree, per-tag lists, linked record tags](milestones/M07-tag-pages/M07-tag-pages.md) | 3 | pending |
| 08 | [Phone cards and chip styling](milestones/M08-phone-cards/M08-phone-cards.md) | 2 | pending |
| 09 | [Docs and the Russian fixture](milestones/M09-docs-and-fixtures/M09-docs-and-fixtures.md) | 3 | pending |

## Final Verification

- [ ] `just ci` passes (lint, typecheck, pytest, snapshots, mdcheck, specs-check, e2e), run once in the foreground.
- [ ] Two runs of `bin/booping specs site --out /tmp/specs-site-a` and `--out /tmp/specs-site-b` over this repo's vault give identical trees (`diff -r`).
- [ ] Behaviour check by the runner with headless Chromium from `file://` over `bin/booping specs site --out /tmp/specs-site-booping`: `records.html#type=rule&status=accepted` shows only accepted rules and the count matches; clicking a chip rewrites the hash; `sort=updated` reorders rows newest first; `review.html` defaults to review order; an unknown hash key is ignored; with JS disabled every row is visible and the filter bar hidden.
- [ ] Visual check by the runner: render this repo's specs and the swarmlight fixture vault (`~/.tmp/specs-site-fixtures/swarmlight/vault`, copied to `/tmp` first) with `core.specs.site.lang: ru`; screenshot home, review, a type page with an active chip and a tag page at 1280×900 and 390×844 in light and dark; confirm one needs-you link, reason icons with text, cards on the phone, no horizontal scroll at 390px.

## Accessibility & interaction

- [ ] Chips are `<button aria-pressed>` in a labelled `role="group"` per facet; sort is a labelled native `<select>`; the visible-row count is a `role="status"` live region (M04).
- [ ] Keyboard: Tab reaches each chip and the select in DOM order; Space/Enter toggles a chip; no focus trap (M04).
- [ ] Reasons are icon + text, icons `aria-hidden` — never colour alone (M05, part 1 badges).
- [ ] New colour pairs ≥ 4.5:1 in both themes, asserted by `site_contrast_test.py` (M06, M08); `:focus-visible` rings on chips (M08).
- [ ] Without JS, all content and full lists stay visible (M04).

## Responsive & cross-browser

- [ ] One breakpoint, 760px: rows as cards, chips on one scrolling line, sort full width, scenario grid one column, tap targets ≥ 44px, no horizontal scroll (M08).
- [ ] Verified in headless Chromium at 1280 and 390 px wide from `file://` (Final Verification).

## Out of scope

- Part 3 (parked, groomed in its own run): "Specs site — record reading and search" — sticky ToC rail and phone `<details>`, `§` heading anchors, backlinks by type and by section (decide which side's heading — shatterlings groups by the target's heading, the base spec says the citing record's), ADR option cards (chosen first and open, others collapsed, phone cards), the Cyrillic-aware vanilla search (`search-index.js`, `search-body.js`, header box with `/`, phone overlay, `search.html?q=`).
- Tag chips on list pages (C8).
- Changes to `llms.txt` / `index.json` / `.md` copies (C1).
- Relation graph and hover previews (base spec priority 3) — skipped.
- Git history / source links from a repo URL.

## CLAUDE.md impact

| Section | Change | Owning task |
|---------|--------|-------------|
| — | — | — |

No CLAUDE.md changes required — no CLI verb, flag, config key or layout line changes; the new pages are documented in `documentation/specs.md` (M09).
