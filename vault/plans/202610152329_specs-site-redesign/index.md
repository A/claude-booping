---
title: "Specs site redesign, part 1 — fonts, theme, shell, record state, machine layer"
type: "feature"
status: in-progress
sp: 34
related_to: null
created: 2026-10-15 23:30
planned: null
started: 2026-10-15 23:49
completed: null
code_reviews: []
sessions:
- 89fea733-132d-4d26-8d40-e7167a12bdd1
- 247b0aa9-8026-4117-88f5-18a7b3234051
retro: null
summary: 'Specs site part 1: shipped fonts, mockup theme and shell, labelled record
  pages, plain lists, llms.txt/index.json/.md copies'
commit: 25e1bcb953b1ebe3b59a2efd6da344d71b321406
tracker_provider: null
tracker_request: null
tracker_issue: null
return_to: null
agents: '{"research-codebase": ["a58e0220f768d569f", "aac49bc2f976b8701"], "research-web":
  "a4c624d6825488430", "cross-review": "a722dee293a62d7a9"}'
reviewed_at: 2026-10-15 23:44
---


## Context

- **Current state** — `booping specs site` (`booping-python/src/booping/specs/site/`, ~1,080 lines with templates and CSS) renders a tier × type count matrix at the root, type pages that concatenate every record body, raw frontmatter keys, bare relation codes, `lang="en"` hardcoded, no navigation, no theme toggle, no shipped fonts, no phone patterns and no machine layer (`design/specs-site-design.md`, audit 1–12). `site-index` shares its look.
- **Motivation** — the owner reads the site as documentation and finds it badly thought out for its scenarios (`design/brief.md`, owner's words): tables of small numbers, unclear clicks, no reading typography, nothing designed for the phone. On the owner's Linux `system-ui` resolves to a monospace face, so the whole site renders mono. The owner approved a clickable prototype (`design/specs-site-mockup.html`).
- **Scope** — this is part 1 of three (`clarifications.md` C2): shipped fonts, labels and `lang`, the mockup's theme and icon sprite, the page shell, record state and the record page head, list pages instead of concatenated bodies and count matrices, `llms.txt` / `index.json` / `.md` copies / `404.html`, and `site-index` in the same design. Not here: the landing with "N need you →", review as a filter, list filter chips with hash state, tag pages, ToC rail, `§` anchors, grouped backlinks, ADR option cards, search — parts 2 and 3, under Out of scope.

## Decisions

Values in play: value/0015 (deterministic where it can be) and booping:rule/0027 drive byte-stable output; value/0008 (effective human review) and value/0013 (guides to the goal) drive the state badges and the reading-first layout; value/0006 (a constructor) puts labels in config; value/0005 (stack-agnostic core) keeps GitLab out of the generator; value/0002 (minimal effective context) motivates the machine layer.

- **Source precedence**: brief > approved mockup > base spec (C1) — the brief carries the owner's corrections, the mockup is what the owner approved after it.
- **Palette**: the mockup's tokens verbatim, light and dark (C1) — the brief says to match them; type scale body 17/1.6, H1 28/1.3, H2 22/1.35, H3 18/1.4, meta 13/1.4, code 15/1.5, measure 68ch, 4px unit, paragraph gap 1em, section gap 2.5em (brief, identical in the mockup).
- **Fonts**: Golos Text and JetBrains Mono variable woff2 (fontsource 5.3.0, cyrillic + latin, OFL 1.1) vendored once and base64-embedded in `fonts.css` (C3) — Firefox blocks `file://` fonts from parent directories, so separate woff2 files would break every nested page. **Departs** from the brief's "woff2 files in the site output" for that reason, and from the base spec's "system font stack, no web fonts" by the owner's correction.
- **Labels in config**: `core.specs.site.lang` + `core.specs.site.labels.{lang}`, `en` and `ru` shipped, key-by-key fallback (C4) — a user adds a locale or names a tier-own type through the three-tier merge instead of code (value/0006, booping:rule/0017). Alternative: a label file beside the templates — rejected, a project could not label its own types.
- **Plural forms**: a list of forms per countable label, Slavic three-form rule for three-form lists (M02) — «5 вопроса» is wrong Russian; full CLDR is more than two languages need.
- **Theme**: one three-state button, `localStorage` key absent = auto, inline head script before stylesheets (C8) — no flash, system preference without JS.
- **Drawer**: real button + `site.js`, no-JS fallback renders the sidebar in flow (C7) — **departs** from the base spec's checkbox hack for its keyboard and screen-reader failures.
- **No build date**: footer names the generator only (C6) — **departs** from the base spec's footer to keep rebuilds byte-identical (value/0015).
- **Machine formats locked**: `llms.txt`, `index.json`, `.md` copies and `404.html` exactly as C9 (booping:rule/0010).
- **404 via `--site-url`**: generic flag, the GitLab template passes `$CI_PAGES_URL` (C9) — the generator stays host-agnostic (value/0005).
- **Part-1 list pages are plain lists** (C10) — part 2 adds filters on the same rows; shipping rows now removes the duplicated body render.
- **Snapshots**: this plan edits no playbook source, so `just snapshots` is expected clean; booping:rule/0013 holds — any drift is reported, and only drift this plan describes may be accepted under the owner's standing permission for this feature (2026-10-14).

## Architecture

```
commands/specs.py  _run_site  ── config core.specs.site{lang,labels,roots}, --title, --site-url
        │
        ▼
site/model.py   load_site → Site{records, relations(), superseded_by(), backlinks()}   (M05)
site/labels.py  load_labels → Labels{ui, type_*, status, fact, author, date, plural}    (M02)
site/state.py   record_state → RecordState{status, clarify, unknown, unreviewed, first_mark} (M05)
        │
        ▼
site/pages.py   build_site → files{path: str|bytes}
   ├─ templates/base.html.j2  shell: head script, header, sidebar/drawer, crumbs, footer (M04)
   │     _icons.html.j2 sprite, _macros icon()/state_badges()                       (M03)
   ├─ record.html.j2 (M06) · type/root/index.html.j2 (M07) · not_found.html.j2 (M09)
   ├─ style.css (M03) · site.js (M04) · fonts.py → fonts.css + OFL (M01)
   └─ machine.py → llms.txt, index.json (M08) · {stem}.md copies (M09)
site/index.py   build_index → site-index on the same shell (M10)
site/write.py   write_site — str and bytes (M01)
```

The output tree keeps today's paths (`index.html`, `{root}/index.html`, `{root}/{type}/index.html`, `{root}/{type}/{stem}.html`) so existing links survive; part 2 may restructure lists across roots.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [Shipped fonts — vendored woff2 embedded in fonts.css](milestones/M01-shipped-fonts/M01-shipped-fonts.md) | 3 | done |
| 02 | [Labels and lang — config label table, html lang, site title](milestones/M02-labels-and-lang/M02-labels-and-lang.md) | 3 | done |
| 03 | [Theme and icons — mockup tokens, reading typography, SVG sprite](milestones/M03-theme-and-icons/M03-theme-and-icons.md) | 4 | done |
| 04 | [Page shell — header, theme toggle, sidebar, drawer, crumbs, footer](milestones/M04-page-shell/M04-page-shell.md) | 4 | done |
| 05 | [Record model — superseded-by, resolved relations, record state](milestones/M05-record-model/M05-record-model.md) | 3 | done |
| 06 | [Record page — state badges, labelled facts, titled relations, marks](milestones/M06-record-page/M06-record-page.md) | 3 | done |
| 07 | [List pages — type, root and home pages as record and type lists](milestones/M07-list-pages/M07-list-pages.md) | 3 | done |
| 08 | [Machine layer — llms.txt and index.json](milestones/M08-llms-and-index-json/M08-llms-and-index-json.md) | 3 | done |
| 09 | [Machine layer — .md copies and 404 page with --site-url](milestones/M09-md-copies-and-404/M09-md-copies-and-404.md) | 3 | done |
| 10 | [site-index in the new design](milestones/M10-site-index-design/M10-site-index-design.md) | 2 | pending |
| 11 | [Docs and a Russian fixture case](milestones/M11-docs-and-russian-fixture/M11-docs-and-russian-fixture.md) | 3 | pending |

## Final Verification

- [ ] `just ci` passes (lint, typecheck, pytest, snapshots, mdcheck, specs-check, e2e), run once in the foreground.
- [ ] Two runs of `bin/booping specs site --out /tmp/specs-site-a` and `--out /tmp/specs-site-b` over this repo's vault give identical trees (`diff -r`).
- [ ] Visual check by the runner: render this repo's specs (`bin/booping specs site --out /tmp/specs-site-booping`) and the swarmlight fixture vault (`~/.tmp/specs-site-fixtures/swarmlight/vault`, copied to `/tmp` first) with `core.specs.site.lang: ru`; screenshot home, a type page and an ADR record at 1280×900 and 390×844 in light and dark with headless Chromium; confirm Golos Text renders (not monospace), no horizontal scroll at 390px, badges carry icon and text, theme toggle cycles, drawer opens and closes.
- [ ] Opened from `file://` in Firefox, a record page two directories deep renders in Golos Text.

## Accessibility & interaction

- [ ] Keyboard paths: skip link → menu (phone) → brand → theme toggle → sidebar → main; drawer closes on Esc and returns focus (M04).
- [ ] Roles and labels: `<nav aria-label>` for sidebar and breadcrumbs, `aria-current="page"`, `aria-expanded`/`aria-controls` on the menu button, theme button `aria-label` names the state (M04).
- [ ] State is never colour alone: every badge has icon + text; icons `aria-hidden` (M03).
- [ ] Contrast ≥ 4.5:1 for text, links and badges in both themes, body ≥ 7:1 in dark — asserted by `site_contrast_test.py` (M03).
- [ ] `prefers-reduced-motion` drops the drawer transition; `:focus-visible` rings (M03).

## Responsive & cross-browser

- [ ] One breakpoint, 760px: one column, sidebar in the drawer, crumbs last level only, rows stacked, facts one column, tap targets ≥ 44px, no horizontal scroll (M03).
- [ ] Verified in headless Chromium at 1280 and 390 px wide and in Firefox from `file://` (Final Verification).

## Out of scope

- Part 2 (parked, groomed in its own run): "Specs site — landing, review filter and list filters" — documentation landing with framing line, reading scenarios and recently updated, one "N need you →" link; review as a filter over the list (unreviewed, has [clarify], has [unknown], open conflicts, proposed ADRs, open ideas/items) with a reason icon and a link to the mark anchor per row; filter chips and sort with `location.hash` state; tiers as a Source facet; phone cards; tag tree and tag pages from `tags.yaml`.
- Part 3 (parked, groomed in its own run): "Specs site — record reading and search" — sticky ToC rail and phone `<details>`, `§` heading anchors, backlinks by type and by section, ADR option cards (chosen first and open, others collapsed, phone cards), the Cyrillic-aware vanilla search (`search-index.js`, `search-body.js`, header box with `/`, phone overlay, `search.html?q=`).
- Relation graph and hover previews (base spec priority 3) — skipped.
- Git history / source links from a repo URL.

## CLAUDE.md impact

| Section | Change | Owning task |
|---------|--------|-------------|
| `## Config` | No new bullet: `core.specs` is already described; the label keys are documented in `documentation/specs.md` and commented in `src/config.yaml`. | — |

No CLAUDE.md changes required — the CLI verb list and layout lines stay true; the new flags and keys live in the user docs (M11) and config comments (M02).
