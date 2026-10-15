---
title: "Specs site redesign, part 5 — review comments and the root landing"
type: "feature"
status: presenting
sp: null
related_to: null
created: 2026-10-16 03:36
planned: null
started: null
completed: null
code_reviews: []
sessions:
- 8a86d73b-8759-4a61-afb0-73379f041cc4
retro: null
summary: 'Specs site part 5: review comments in localStorage, record and site-wide
  panels, copy-for-the-model export; root landing'
commit: 7d4023234a5faa2a341e35693bec061a1ab0348f
tracker_provider: null
tracker_request: null
tracker_issue: null
return_to: null
---

# Specs site redesign, part 5 — review comments and the root landing

## Context

- **Current state** — parts 1–4 (`plans/202610152329_specs-site-redesign`, `plans/202610160041_specs-site-landing-and-filters`, `plans/202610160138_specs-site-reading-and-search`, `plans/202610160249_specs-site-polish`, all done) shipped a static, byte-stable specs site: shell, Overview landing, review filter, record pages with § anchors, search. A reviewer has no place on the site to note a remark against a passage; remarks are written elsewhere and re-located by hand before an agent sees them. A root's own page (`{root}/index.html`) still has the pre-redesign shape — type list with "Records: N" and the full mark list.
- **Outcome** — the reader comments on a selected span, a paragraph or a § heading of any record page, sees and edits the comments per record and site-wide, copies them as one markdown block grouped by record that an agent can act on, and clears what was sent; all in the browser, from `https://` or `file://`, no network. A root page reads like the Overview landing for that root.
- **Scope** — root landing (M01), the export builder (M02), HTML hooks and storage (M03), capture (M04), panels with copy and clear (M05), docs (M06), then the runner's browser check. Defaults for every open call: `clarifications.md` C1–C8; request and brief: `request.md`.

## Decisions

Values in play: value/0015 (deterministic where it can be) and booping:rule/0027 (renders reproducible) keep every comment out of the build — the generator writes only static hooks, the comments are browser state; value/0010 (proven to work) puts the export builder in its own file under a node-run unit test beyond the request's golden-only minimum (C1); value/0003 (single source) renders index and root landings from one context helper and one set of macros (C6) and sends every UI string from config labels through `data-*`; value/0008 (effective human review) is the feature's reason — a reviewer's remarks reach the agent pinned to the passage; value/0005 keeps the export free of project specifics and words (C2); booping:rule/0010 locks the export content (C2); booping:rule/0007 removes `types_list` and an orphaned `records` label in the milestone that retires them.

- **Client-side comments, static hooks** (C1): `comments.js` + `comments-format.js` shipped verbatim beside `site.js`; HTML carries `data-ref/title/page`, the sidebar entry, the header button, closed `<dialog>` shells and `comments.html`.
- **Export block** (C2): `## {ref} — {title}`, then per comment `[§ {anchor}]({absolute url})`, the quote as `> ` lines, the note; records by ref, comments by time; no labels in it.
- **Anchors** (C3): span/paragraph comments anchor to the nearest preceding h2–h4 id; the quote pins the text. No new ids in the generated HTML.
- **Affordances** (C4): JS-injected section buttons (the keyboard path), one floating button for a selection or a tapped paragraph, placed below the selection to clear native mobile menus.
- **Panels and storage** (C5): `<dialog>` + `showModal()` for compose and the record panel — side sheet ≥ 760px, bottom sheet below; `comments.html` as the site-wide panel with a sidebar count; one localStorage key per site root URL, try/catch everywhere; Copy marks `sent`, Clear sent removes those.
- **Root landing** (C6): same macros as Overview, root-scoped counts, callout to `../review.html#source={root}`, no marks.
- **Firefox `file://`** (C7): per-file storage origin there; documented, not worked around.
- **Snapshots**: no playbook source is edited, so `just snapshots` is expected clean. booping:rule/0013 says a run never accepts a baseline; the owner's standing permission for this feature (2026-10-14, restated in the invocation) **departs** from it: drift this plan describes may be accepted and is listed in the run's defaults file, any other drift stops the run. The `site-*.txtar` goldens are test fixtures each milestone rebaselines with `just e2e -k site --txtar-update` and reads.

## Architecture

```
site/pages.py  build_site
   ├─ ships verbatim: style.css, site.js, filter.js, search.js, + comments-format.js (M02), comments.js (M03)
   ├─ _landing(records, needs, href…) → index.html.j2 (site) and root.html.j2 (per root) (M01)
   ├─ record.html.j2: article[data-ref,data-title,data-page] + _comments.html.j2 {dialog.cmt-sheet, dialog.cmt-compose} (M03)
   ├─ base.html.j2: header button.cmt-open (record pages), sidebar li.cmt-nav → comments.html, script tags (M03)
   └─ comments.html.j2 → comments.html (site root, JS-populated shell) (M03)
browser:
   comments-format.js  SpecsComments.format(comments, siteRoot) → markdown block (pure; node test M02)
   comments.js         store (localStorage "specs-comments:v1:{site root URL}") · counts (M03)
                       section buttons · floating button · compose dialog (M04)
                       record sheet · comments.html groups · edit/delete · copy/clear (M05)
src/config.yaml: labels.{en,ru}.ui.* for every comment string (M03); `records` label dropped if orphaned (M01)
```

`model.py`, `markdown.py`, `machine.py`, `search.*`, `filter.js`, `index.json`, `llms.txt` and `site-index` do not change.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [Root page follows the Overview landing](milestones/M01-root-landing/M01-root-landing.md) | 3 | pending |
| 02 | [Comment export builder and its node test](milestones/M02-export-builder/M02-export-builder.md) | 3 | pending |
| 03 | [Comment hooks in the generated HTML and the storage module](milestones/M03-comment-hooks/M03-comment-hooks.md) | 4 | pending |
| 04 | [Comment affordances and the compose dialog](milestones/M04-comment-capture/M04-comment-capture.md) | 4 | pending |
| 05 | [Record and site-wide comment panels with copy and clear](milestones/M05-comment-panels/M05-comment-panels.md) | 4 | pending |
| 06 | [Document review comments and the root landing](milestones/M06-comments-docs/M06-comments-docs.md) | 2 | pending |

## Milestone files

Each milestone directory under `milestones/` holds its file with goal, scope, tasks, DoD, references and Verify; this index is context only.

## Final Verification

- [ ] `just ci` green, run once at the end in the foreground.
- [ ] `just snapshots` clean (no playbook source touched); any drift handled per Decisions → Snapshots.
- [ ] Browser check by the runner: `bin/booping specs site --out /tmp/specs-site-booping` from the repo; a throwaway Playwright script (`uv run --with playwright python /tmp/cmt-check.py`, launching the system Chromium via `executable_path`) opens `claude-booping/adr/0001-specs-tiers.html` over `file://`, adds two comments through the UI — one on a selected span under `## Decision`, one via a section button on `## Alternatives` — opens the record panel and screenshots at 1300×2200 and 390×2400; then opens `comments.html` and screenshots both widths; then clicks Copy and reads the clipboard text, comparing it with the C2 shape. The runner looks at all four screenshots before closing. Pass when: both comments listed with ref, anchor, quote and note; at 1300 the panel is a right-side sheet, at 390 a bottom sheet with no horizontal scroll; buttons ≥ 44px tall at 390 (touch emulation); the copied block matches C2; `claude-booping/index.html` shows callout, scenario cards and Recently updated, no marks.
- [ ] Typecheck clean (`just typecheck`, inside `just ci`).

## Accessibility & interaction

- [ ] Keyboard paths: Tab to a section's comment button → Enter opens compose; keyboard text selection → Tab reaches the floating button; header "My comments" button opens the panel; Tab through items (anchor link, Edit, Delete) and Copy / Clear sent; Escape closes any dialog.
- [ ] Labels: every icon-only button has an aria-label from config labels (`comment_section`, `my_comments`, `close`); the compose textarea has a visible label `comment_note`; counts are text, not colour.
- [ ] Focus: `showModal()` traps focus and inerts the page; on close focus returns to the opener; after Delete focus moves to the next item or the list heading.
- [ ] Announcements: copy, clear and delete results go through the existing `#status` live region.
- [ ] Reduced motion: sheet slide-in transitions off under `prefers-reduced-motion`.

## Responsive & cross-browser

- [ ] ≥ 760px: record panel as a right-side sheet; compose as a centred dialog.
- [ ] < 760px: both as bottom sheets, `max-height: 80vh`, inner scroll, tap targets ≥ 44px under `(pointer: coarse)`.
- [ ] Verified in Chromium at 1300 and 390 (Final Verification); Firefox `file://` per-file storage documented (C7), not verified in this sprint.

## Out of scope

- Highlighting commented spans in the page text (CSS Custom Highlight API) — park as an idea.
- Syncing comments between browsers or devices, import, or any server; comments on non-record pages.
- Ids for paragraphs in the generated HTML (C3).

## CLAUDE.md impact

No CLAUDE.md changes required — the site's pages and assets are not described there; no command, layout or convention changes.
