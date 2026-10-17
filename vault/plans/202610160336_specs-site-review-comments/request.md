# Request

## Request

> Request — specs site: review comments, and the root page.
> 1. Review comments (owner, 2026-10-16): on any record page the reader can comment on a selected text span, a paragraph or a heading (the § anchor) — a small "Comment" affordance, a text box, saved in localStorage per site (try/catch; works from file://; no network). A "My comments" panel on the record page and a site-wide one (sidebar entry with a count) list every comment with its record ref, anchor, quoted text and note; edit and delete. "Copy for the model" copies one markdown block: for each comment the record ref and title, the anchor link, the quoted text as a blockquote, and the note — grouped by record — ready to paste to an agent; "Clear sent" removes them after copying. Keyboard and phone friendly (tap targets ≥44px, the panel as a bottom sheet on phones). Vanilla JS only, deterministic HTML (the comments are client-side state only).
> 2. A root's own page (`/<root>/index.html`) still lists marks under the cards and shows "Records: N" labels; make it follow the Overview landing (callout, scenario cards with quiet counts, recently updated for that root).
> Tests: unit tests for the copy-format builder if it is generated server-side, otherwise a txtar/golden case for the HTML hooks; a chromium screenshot check desktop 1300 + phone 390 of a record with two comments and the panel open, looked at before closing.

## Task type

`feature` — a new reader-facing capability (comments on record pages, a site-wide comments panel, a copy-to-agent export) plus a landing redesign of an existing page. Not `bug`: the root page renders as its template says, nothing diverges from a stated expectation — it predates the Overview landing (part 2/4). Not `refactoring`: both parts change what the reader sees and can do.

## Problem

`booping specs site` renders a static, deterministic HTML site (parts 1–4 of the redesign). A reviewer reading a record has no way to note a remark against a passage: remarks are kept elsewhere and re-located by hand before they reach an agent. The site must let the reader attach a note to a selected span, a paragraph or a § heading of any record page, keep the notes in the browser only (localStorage, per site, file:// included, no network), list them per record and site-wide with edit and delete, and export them as one markdown block grouped by record that an agent can act on, then clear what was sent. The HTML the generator writes stays byte-stable — comments are client state.

A root's own page (`{root}/index.html`, `templates/root.html.j2`) still shows the pre-redesign shape: the type list with "Records: N" labels and the full mark list under it. It must follow the Overview landing (`index.html.j2`): callout, scenario cards with quiet counts, Recently updated — scoped to that root.

## Clarifications and Decisions

- Autonomous run: every open call is settled by a default recorded in `clarifications.md`; the approval gate is auto-confirmed (owner's invocation, 2026-10-16).
- One plan: both parts land on the site package and together sit under the 35 SP split threshold — no parked siblings.
- Comments are client state only: the generator writes static hooks (stable anchors, data attributes, an empty panel shell, labels) and one shipped JS file; no comment ever reaches the build output.
- The copy-format builder runs in the browser (no server side exists for client state), so its exact output is locked in grooming (booping:rule/0010) and held by a check that executes the shipped JS — details in the plan.
- Branch `feat/specs`, no push, path-scoped staging; snapshot drift only per the owner's standing permission (2026-10-14).
