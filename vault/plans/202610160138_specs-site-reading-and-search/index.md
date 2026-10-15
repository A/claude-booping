---
title: "Specs site redesign, part 3 — record reading and search"
type: "feature"
status: ready-for-dev
sp: null
related_to: null
created: 2026-10-16 01:39
planned: null
started: null
completed: null
code_reviews: []
sessions:
- 50d35fa2-5b16-450d-a9df-a7507d4ae767
retro: null
summary: 'Specs site part 3: ToC rail, § anchors, grouped backlinks, ADR option cards,
  Cyrillic-aware vanilla search'
commit: 253764fb4a3221781faeb3b8ebd6da0926eaba31
tracker_provider: null
tracker_request: null
tracker_issue: null
return_to: null
agents: '{"research-codebase": "a94ca418362743d51", "cross-review": "a843baee827ba90c0"}'
reviewed_at: 2026-10-16 01:51
---

# Specs site redesign, part 3 — record reading and search

## Context

- **Current state** — parts 1 and 2 (`plans/202610152329_specs-site-redesign`, `plans/202610160041_specs-site-landing-and-filters`, both done) shipped the shell, theme, fonts, record page head with state badges, the machine layer, the landing, the review filter, filterable lists and tag pages. A record page is still one long column: no "On this page" navigation, no way to link a heading, "Referenced by" is one flat list, ADR alternatives are a plain table followed by paragraphs with the chosen option not distinguished, and there is no search — the base spec's "find by text" task has no surface.
- **Motivation** — the owner's brief (`../202610152329_specs-site-redesign/design/brief.md`): reading-first documentation, ToC and open questions under the title on the phone, ADR options as cards with the chosen one first and open, and the base spec's own Cyrillic-aware vanilla search loaded via `<script src>` so `file://` works — never Pagefind or lunr. The base spec (`design/specs-site-design.md`) adds the sticky rail, rustdoc-style `§` anchors, backlinks by type and by section, and `search.html?q=`.
- **Scope** — part 3 of three, the last (`clarifications.md` C1): ToC rail and phone `<details>`, `§` anchors, grouped backlinks, ADR option cards, search. Priority 3 stays skipped (Out of scope).

## Decisions

Values in play: value/0013 (guides to the goal) and value/0008 (effective human review) drive the rail with the record's open questions, backlinks that say where they come from and the chosen ADR option first; value/0015 (deterministic where it can be) and booping:rule/0027 keep every new page and data file byte-stable, with JS only filtering, ordering and copying what the HTML and the data files already hold; value/0005 (stack-agnostic core) and value/0006 (a constructor) keep every string in config labels; value/0002 (minimal effective context) leaves the machine layer as it is and loads search data only on use; value/0003 (single source) keeps the design files in part 1's plan, referenced.

- **Source precedence**: brief > mockup > base spec, design files referenced from part 1's plan, not copied (C1).
- **Headings on `Rendered`, anchors as tokens** (C2) — one heading list feeds the ToC, grouped backlinks and nothing else re-parses the body; ids stay part 1's slugs, so the `#anchor`s records already write keep working.
- **`site.js` opens a closed `<details>` holding the hash target** (C2) — browsers differ on auto-expanding `<details>` on fragment navigation; ADR table links and ToC links must always land.
- **Rail at ≥ 1100px, `.toc-m` below** (C3) — the three-column grid needs the width; **departs** from the brief's "under the title": the `<details>` sits under the lead, as the base spec says.
- **Backlinks by type with a `via` line, plus the old generator's by-section list** (C4) — the base spec's "which `##` of the citing record" and shatterlings' "which heading of this record" answer different questions from data the site already has; both kept. `index.json` unchanged.
- **ADR cards as a token pass that falls back silently** (C5) — a tier may override the ADR schema; a shape that does not match renders as before, never an error (booping:rule/0029 spirit: no crash on content). The table stays as the summary, hidden on the phone where cards carry its columns.
- **Search data formats locked** (C6, booping:rule/0010); **matching and UI locked** (C7) — the base spec's algorithm with concrete stem lengths and weights, the WAI-ARIA APG combobox, one form doubling as the phone overlay. **Departs** from nothing in the brief; the base spec's "~80 lines" grows to ~160 with the UI.
- **JS verified in the browser, not in `just ci`** (C7) — part 2 C9 precedent; pytest owns the data files and markup.
- **Snapshots**: no playbook source is edited, so `just snapshots` is expected clean; booping:rule/0013 holds — any drift is reported, and only drift this plan describes may be accepted under the owner's standing permission for this feature (2026-10-14). The `site-*.txtar` goldens are test fixtures rebaselined by the milestones that change output (C9).

## Architecture

```
site/markdown.py  render_body(…, alternatives) → Rendered{html, marks, links, headings, text}  (M01 M04 M05)
   ├─ heading_open: id (part 1) + § anchor token (h2–h4)                                    (M01)
   └─ site/adr.py  option_cards(tokens, labels) — Alternatives table → chosen row, <details class="opt"> cards  (M04)
        │
        ▼
site/pages.py  build_site — renders every body first, then pages
   ├─ _record_view: toc, questions (M02) · backlink_groups (site/backlinks.py, M03)
   ├─ record.html.j2: {% block rail %} + .toc-m <details> (M02) · Referenced by grouped (M03)
   ├─ base.html.j2: header search form + phone search button + search.js (M06)
   ├─ search.html (M06) · search-index.js, search-body.js (site/search.py, M05)
   ├─ site.js: § copy, open <details> on hash (M01) · scroll-spy (M02)
   └─ search.js: lazy <script src>, normalise/stem/score, combobox, overlay (M06)
```

`site-index` is untouched. `model.py`, `machine.py`, `index.json`, `llms.txt` and the `.md` copies do not change.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [Headings on Rendered and § section anchors](milestones/M01-heading-anchors/M01-heading-anchors.md) | 3 | pending |
| 02 | [On this page rail, open questions and the phone details](milestones/M02-toc-rail/M02-toc-rail.md) | 3 | pending |
| 03 | [Backlinks grouped by type and by section](milestones/M03-grouped-backlinks/M03-grouped-backlinks.md) | 3 | pending |
| 04 | [ADR option cards](milestones/M04-adr-option-cards/M04-adr-option-cards.md) | 4 | pending |
| 05 | [Search data — search-index.js and search-body.js](milestones/M05-search-data/M05-search-data.md) | 3 | pending |
| 06 | [Search UI — header combobox, phone overlay, search.html](milestones/M06-search-ui/M06-search-ui.md) | 4 | pending |
| 07 | [Docs and the Russian fixture](milestones/M07-docs-and-fixtures/M07-docs-and-fixtures.md) | 2 | pending |

## Final Verification

- [ ] `just ci` passes (lint, typecheck, pytest, snapshots, mdcheck, specs-check, e2e), run once in the foreground.
- [ ] Two runs of `bin/booping specs site --out /tmp/specs-site-a` and `--out /tmp/specs-site-b` over this repo's vault give identical trees (`diff -r`).
- [ ] Behaviour check by the runner with headless Chromium from `file://` over `bin/booping specs site --out /tmp/specs-site-booping`: on `adr/0001` the chosen card is first and open, clicking a table option link opens its card; the rail marks the section in view; clicking a `§` changes the hash; `/` focuses search, `tiers` returns `adr/0001` in the dropdown, Down + Enter opens it; `search.html?q=tiers` lists results with a count; with JS disabled every card's content is reachable, the ToC links work and the search form submits to `search.html`.
- [ ] Russian search check over the swarmlight fixture vault (`~/.tmp/specs-site-fixtures/swarmlight/vault`, copied to `/tmp` first) with `core.specs.site.lang: ru`: a query with `ё` and its `е` spelling return the same records; a stem query (word minus its ending) finds the full word.
- [ ] Visual check by the runner: screenshot a record page with rail, an ADR page and the search overlay at 1280×900 and 390×844 in light and dark; confirm the rail at 1280, `.toc-m` at 390, cards on the phone, no horizontal scroll at 390px.

## Accessibility & interaction

- [ ] `§` anchors are real links with an `aria-label` naming the section; the copy notice is a `role="status"` live region (M01).
- [ ] The rail ToC is a labelled `<nav>`; the current section uses `aria-current="location"` (M02).
- [ ] ADR cards are native `<details>`/`<summary>`, keyboard-operable; status shown as icon + text, never colour alone (M04).
- [ ] Search follows the WAI-ARIA APG editable combobox with listbox popup: `role="combobox"`, `aria-expanded`, `aria-controls`, `aria-activedescendant`, Down/Up/Enter/Esc; `/` never steals keys from form fields; the overlay returns focus to its opener on close (M06).
- [ ] New colours use existing tokens, ≥ 4.5:1 in both themes, `site_contrast_test.py` green (M01 M04 M06).
- [ ] Without JS all content stays reachable: anchors and ToC are links, cards open by click, search submits to `search.html` with a note (M01–M06).

## Responsive & cross-browser

- [ ] Rail at ≥ 1100px; `.toc-m` below; part 1's 760px breakpoint for the ADR table → cards and the search overlay; tap targets ≥ 44px; no horizontal scroll (M02 M04 M06).
- [ ] Verified in headless Chromium at 1280 and 390 px wide from `file://` (Final Verification).

## Risk register

| Risk | Disposition |
|------|-------------|
| Cross-review CRITICAL: `search.js` (and `site.js` additions) have no automated test in `just ci` | Deferred — reopening it reverses part 2 C9 and this plan's C7 (CI stays Python-only). Mitigation: C7 locks the algorithm to concrete stem lengths, weights and order; the M06 worker runs the headless Chromium checks itself before returning; the runner repeats them in Final Verification with the Russian `ё`/stem queries. |

## Out of scope

- Relation graph and hover previews (base spec priority 3) — skipped.
- Git history / source links from a repo URL.
- Tag chips on list pages (part 2 C8).
- Changes to `llms.txt` / `index.json` / `.md` copies — grouped backlinks and search data stay out of them.
- A JS test runner in `just ci`.

## CLAUDE.md impact

| Section | Change | Owning task |
|---------|--------|-------------|
| — | — | — |

No CLAUDE.md changes required — no CLI verb, flag, config key shape or layout line changes; the new behaviour is documented in `documentation/specs.md` (M07) and the labels are commented with the rest in `src/config.yaml`.
