# Request

## Request

> Request — specs site mobile/UX fixes from the owner's phone screenshot (/tmp/claude-1000/-home-anton-Dev--A-hermes-pet/36dbf90d-0102-4f43-add1-4a69775c2e2f/scratchpad/site/owner-phone-review.jpg — look at it):
> 1. A record card in any list is clickable as a whole (stretched link to the record; keyboard focus on the title link; text selection still possible); today only the title opens it.
> 2. Filters are too big: on phones (≤640px) the type, source and state chip groups plus the full-width sort select take half the screen before the first record. Collapse them into one compact row "Filters (n) · Sort" that opens a bottom sheet with the chip groups and the sort; show only the active filters as small removable chips under the row. On all widths make chips compact (≈30px high, 13–14px text, tighter gaps); keep ≥44px tap targets via padding/hit area, not visual size.
> 3. In a card the record ref sits on a wide filled bar; render it as a small muted mono line above the title, like the approved prototype (specs-site-mockup.html in /tmp/claude-1000/-home-anton-Dev--A-hermes-pet/36dbf90d-0102-4f43-add1-4a69775c2e2f/scratchpad/site/).
> Check with chromium screenshots at 390px (review filter page with a filter active, a list page, the filter sheet open) and 1300px before closing; compare with the owner screenshot.

## Task type

`feature` — changes what the reader sees and can do on list pages (whole-card navigation, a filter sheet, removable active-filter chips). Not `bug`: each current behaviour renders as its template and CSS say — only-the-title links, inline chip groups and the `code.ref` fill are as built in parts 1–2, not a divergence from a stated expectation (the fill comes from the bare `code` rule leaking onto `code.ref`, a styling miss that this plan fixes alongside). Not `refactoring`: every change is user-visible.

## Problem

`booping specs site` renders list pages (all records, per-type lists, tag pages, the review filter) whose rows become cards below the 760px breakpoint. Only a card's title link opens the record. On a phone the filter bar — one horizontally scrolling chip row per facet (type, source, status, flag), each chip ≥44px tall, then a full-width sort select and the count line — fills about half the first screen before the first record (owner screenshot, swarmlight review page). The ref in each card is a `<code class="ref">`, so the generic `code` rule paints it as a filled bar; the approved prototype shows a plain small muted mono line above the title. After this plan: a click or tap anywhere on a card opens its record while text stays selectable; on phones the filters sit behind one compact row that opens a bottom sheet, the active filters show as small removable chips; chips are compact at every width with ≥44px hit areas on touch; the ref reads as a quiet mono line.

## Clarifications and Decisions

- Autonomous run: every open call is settled by a default recorded in `clarifications.md` (C1–C6); the approval gate is auto-confirmed (owner's invocation, 2026-10-16).
- One plan: all three parts land on the site package's list pages and sum well under the 35 SP split threshold — no parked siblings.
- Phone breakpoint is the site's one existing breakpoint, 760px, not a new 640px one (C1).
- Without JS the filter groups stay inline and every row stays visible (part-1 design doc: everything degrades); the compact row and sheet are JS-only.
- Branch `feat/specs`, no push, path-scoped staging; snapshot drift only per the owner's standing permission (2026-10-14).
