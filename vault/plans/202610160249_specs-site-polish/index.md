---
title: "Specs site redesign, part 4 — landing column, reading measure, relations in
  the facts grid"
type: "feature"
status: in-progress
sp: 8
related_to: null
created: 2026-10-16 02:52
planned: null
started: 2026-10-16 03:00
completed: null
code_reviews: []
sessions:
- c768fd6c-5287-467e-b5b6-da56d84b7512
- 1bc94760-415d-4cb1-91b0-37550e5cd6b7
retro: null
summary: 'Specs site part 4: 68ch reading column on home and records, relations in
  the facts grid, callout breakdown, plain sidebar tags'
commit: 674f39b0a38c78faa4dd0934f77072edcd83b3fb
tracker_provider: null
tracker_request: null
tracker_issue: null
return_to: null
reviewed_at: 2026-10-16 02:58
---

# Specs site redesign, part 4 — landing column, reading measure, relations in the facts grid

## Context

- **Current state** — parts 1–3 (`plans/202610152329_specs-site-redesign`, `plans/202610160041_specs-site-landing-and-filters`, `plans/202610160138_specs-site-reading-and-search`, all done) shipped the shell, the landing, the review filter, the record page and search. Rendered over booping's vault at 1300px and 390px (`request.md`, Problem): the home already holds lead, one "N need you →" link, scenario cards with a quiet count and Recently updated, with no mark list — but lead, callout and Recently updated run ~990px wide, the callout does not name what needs the owner, the sidebar renders tags as monospace chips including empty ones, and a phone Recently-updated title is squeezed into a narrow column. A record's reading column runs ~78ch, and its relations sit in a second `<dl>` offset from the facts box.
- **Motivation** — the brief's "Found after part 1" and "Found after part 2" sections (`/tmp/claude-1000/-home-anton-Dev--A-hermes-pet/36dbf90d-0102-4f43-add1-4a69775c2e2f/scratchpad/site/brief.md`) and the owner-approved prototype beside it, committed as `plans/202610152329_specs-site-redesign/design/specs-site-mockup.html`: one 68ch reading column on home and record pages, relations as rows of the facts grid, monospace only for refs and code.
- **Scope** — a polish pass: home column and callout (M01), sidebar tags (M02), record column and facts grid (M03), then the runner's visual comparison with the prototype. Defaults for every open call: `clarifications.md` C1–C6.

## Decisions

Values in play: value/0008 (effective human review) and value/0013 (guides to the goal) drive a callout that says what needs the owner and a reading column a reviewer can read; value/0003 (single source) reuses the existing `.measure` token and the existing relation rows instead of new ones; value/0005 and value/0006 keep every new string in config labels, en and ru; value/0015 and booping:rule/0027 keep output byte-stable — every change is template, CSS or a computed count, no JS; booping:rule/0010 locks the callout's text (C3); booping:rule/0007 removes the `.relations` markup and CSS in the milestone that retires them.

- **One 68ch column** (C1): `.measure` around the whole record column and the home lead, callout and Recently updated; scenario cards stay full width — the prototype's shape. The brief allowed facts to stay wider; the prototype keeps them in the column, and the prototype wins on look (brief: "Match its layout").
- **Relations are facts rows** (C2): the one `dl.facts` aligns by construction; the raw-frontmatter box stays separate.
- **Callout breakdown** (C3): `{n} need you →` link, then `· {u} unreviewed · {q} open questions`, zeros omitted.
- **Sidebar tags** (C4): plain text with a count; zero-count tags left out of the sidebar only.
- **Phone Recently updated** (C5): date under the title below 760px.
- **Visual check fixture** (C6): booping's own vault and the swarmlight vault in a temp `lang: ru` project.
- **Snapshots**: no playbook source is edited, so `just snapshots` is expected clean. booping:rule/0013 says a run never accepts a baseline; the owner's standing permission for this feature (2026-10-14, in `request.md`) **departs** from it: drift this plan describes may be accepted and is listed in the run's defaults file, any other drift stops the run. The `site-*.txtar` goldens are test fixtures each milestone rebaselines with `just e2e -k site --txtar-update` and reads.

## Architecture

```
site/pages.py  build_site
   ├─ index.html.j2 ctx: needs, questions, + unreviewed (M01)
   │     index.html.j2: div.measure{h1, lead, callout} · ul.scen (full width) · div.measure{Recently updated}
   ├─ _nav: tag nodes with count 0 dropped from the sidebar (M02) → base.html.j2 plain tag links
   └─ record.html.j2: div.measure{ article{ h1, badges, tags, lead, toc-m, dl.facts{facts…, relations…}, dl.facts{raw}, body }, Referenced by } (M03)
style.css: .measure (exists, 68ch) · .facts ul.rel compact · .relations removed · phone .recent wrap
src/config.yaml: labels.{en,ru}.ui.unreviewed_n
```

`model.py`, `machine.py`, `search.*`, `site.js`, `filter.js`, `index.json`, `llms.txt` and `site-index` do not change.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [Home landing column and callout breakdown](milestones/M01-home-landing-column/M01-home-landing-column.md) | 3 | done |
| 02 | [Sidebar tags as plain links, empty tags hidden](milestones/M02-sidebar-tags/M02-sidebar-tags.md) | 2 | done |
| 03 | [Record reading column and relations in the facts grid](milestones/M03-record-reading-column/M03-record-reading-column.md) | 3 | done |

## Milestone files

Each milestone directory under `milestones/` holds its file with goal, scope, tasks, DoD, references and Verify; this index is context only.

## Final Verification

- [ ] `just ci` green, run once at the end in the foreground.
- [ ] `just snapshots` clean (no playbook source touched); any drift handled per Decisions → Snapshots.
- [ ] Visual check by the runner, compared side by side with the approved prototype `plans/202610152329_specs-site-redesign/design/specs-site-mockup.html` (a committed copy of the brief's mockup) (opened at `#home`, `#record`, `#home-phone`, `#record-phone`): `bin/booping specs site --out /tmp/specs-site-booping` from the repo, and `bin/booping specs site --out /tmp/specs-site-ru` from `/tmp/specs-site-ru/` built per C6; Chromium `--headless=new --hide-scrollbars --screenshot` at `--window-size=1300,2200` and `390,2400` of `index.html`, `claude-booping/adr/0001-specs-tiers.html` and `swarmlight/adr/0003-*.html`. Pass when: home lead/callout/Recently updated share one left edge and right edge narrower than the scenario grid; the callout reads per C3 in en and ru; no mark list on home; record body lines hold ≤ 70 characters at 1300px; relation labels sit in the facts `dt` column inside the facts box; sidebar tags are sans with no zero counts; at 390px no horizontal scroll and Recently-updated dates sit under titles.
- [ ] Typecheck clean (`just typecheck`, inside `just ci`).

## Accessibility & interaction

N/A — no new interactive element. The callout keeps one link with visible text; relation rows keep their links and text badges.

## Responsive & cross-browser

- [ ] ≥ 1100px: sidebar + 68ch column + rail on record pages; home without rail.
- [ ] 760–1099px: sidebar + 68ch column.
- [ ] < 760px: one column, facts single-column (part 1), Recently-updated date under the title (C5).
- [ ] Verified in headless Chromium at 1300 and 390 (Final Verification); no other browser in this sprint.

## Out of scope

- The ADR Alternatives table and option cards both on desktop — part 3's settled decision (C5 there).
- New data, JS, search or machine-layer changes; `site-index`.
- Type-label config for the swarmlight `mechanic` type beyond the temp visual-check project.

## CLAUDE.md impact

No CLAUDE.md changes required — no command, layout or convention changes; the site's look is not described there.
