---
type: adr
title: The owner reviews specs on the site and hands the review to an agent
summary: Accepted — a review panel beside each record collects comments and a reviewed mark in the browser; an Outbox page shows and copies everything for the agent, which edits the records.
created_by: claude
created_at: 2026-10-16
updated_at: 2026-10-16
status: accepted
values: [value/0008, value/0011, value/0002]
issues: []
---

## Context

The owner reads specs on the published site (GitLab and GitHub Pages, adr/0029), often on a phone,
and is the only one who may set `reviewed:` on a record. The site is static: no server, no login, no
write path back to the repo. The first comment feature (a floating Comment button on a selection, §
buttons on paragraphs, a header sheet and a "My comments" page) was not found by the owner on a real
record page (2026-10-16), and it had no way to mark a record reviewed at all. The sidebar's "Review"
entry already names a different thing: the list of records without a review.

## Criteria

- Commenting and marking reviewed are visible on the page without being told how.
- What reaches the agent is exactly what the owner sees before sending.
- No server, no credentials in the browser; the repo changes only through an agent.

## Decision

1. **A review panel beside each record** (and plan and retrospective pages): always visible on wide
   screens, a bottom sheet on phones. It keeps a free-form input at the top for a comment on the whole
   record, and lists the record's comments below it, newest first. Selecting text in the body opens a new comment card
   with the quote and focuses its input; clicking a comment focuses it, clicking its quote scrolls to
   the place. A **Reviewed** checkbox marks the whole record.
2. **Outbox** — a header button with the count of unsent items opens a page with every comment and
   reviewed mark on the site, grouped by record (the record with the newest comment first, comments
   newest first), in the exact text that will be sent, with **Copy
   all** and **Clear**. It replaces "My comments".
3. **The agent applies the review.** The owner pastes the block to an agent; the agent edits the
   records and sets `reviewed:` with the date of each `<ref> — reviewed <date>` line. It checks each
   item against the record first, so an item sent twice is recognised as done and skipped.
4. **Names.** The header page is **Outbox** / «К отправке»; the sidebar list of records without a
   review becomes **Awaiting review** / «Ждут ревью». "Review" alone names neither.
5. **Where the review lives and how it ends.**
   - *Storage:* the browser's localStorage, one key per site (its base URL), so a site rebuild keeps it
     and two sites never mix. It is per browser and device: nothing syncs, the copied text is the only
     transfer. In a private window it lasts for that window; clearing site data loses it.
   - *Reload:* everything is restored — the panel's cards, typed inputs (saved as you type) and the
     reviewed checkbox.
   - *No sent state:* Copy all only copies; nothing is marked. The owner clears when done —
     **Clear** on the Outbox removes everything, Delete removes one item. Sending an item again is
     harmless (point 3).
   - *Moved text:* when a quote no longer appears in the record, the comment stays with its quote and
     a "text changed" note instead of a highlight.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [Review panel and Outbox](#review-panel-and-outbox) | accepted | medium | high | Visible, phone-friendly, the agent stays the only writer |
| [Keep the floating affordances](#keep-the-floating-affordances) | rejected | low | high | The owner did not find them; no reviewed mark |
| [Comments as tracker issues](#comments-as-tracker-issues) | rejected | high | medium | Needs a token in the browser or a backend; GitHub and GitLab sites differ |
| [Edit records in the browser and open a PR](#edit-records-in-the-browser-and-open-a-pr) | rejected | high | medium | Credentials in the browser; skips the agent that keeps records consistent |

### Review panel and Outbox

The decision above.

- **Pros:** the affordance is on screen, not hidden behind hover; free-form notes need no selection;
  the Outbox is a preview of exactly what the agent gets; works offline and from `file://`.
- **Cons:** a review lives in one browser until it is copied; a cleared browser loses unsent notes;
  nothing tracks what was sent, so clearing is the owner's step.
- **Complexity:** medium — a panel, a page, the reviewed mark and its badge.
- **Reversibility:** high — client-side only; the export format is unchanged.

### Keep the floating affordances

The first comment feature as shipped.

- **Pros:** already built.
- **Cons:** not discoverable on a real record page; no reviewed mark; two different things called
  "Review".
- **Complexity:** low.
- **Reversibility:** high.

### Comments as tracker issues

Each comment posted to GitHub or GitLab as an issue or a note.

- **Pros:** shared between devices; visible to other people.
- **Cons:** a token in the browser or a backend for a static site; two trackers with different APIs;
  the agent still has to apply them to the records.
- **Complexity:** high.
- **Reversibility:** medium.

### Edit records in the browser and open a PR

An editor on the record page that commits through the forge's API.

- **Pros:** the change lands without an agent.
- **Cons:** credentials in the browser; the owner edits Markdown by hand, the agent's consistency work
  (refs, dates, related records) is skipped.
- **Complexity:** high.
- **Reversibility:** medium.

## Consequences

- The site's comment UI is rebuilt around the panel; `comments.html` becomes the Outbox page.
- The sidebar entry is renamed; labels in `en` and `ru`.
- The export gains `<ref> — reviewed <date>` lines; the specs playbook tells the agent how to apply
  them (set `reviewed:`, never on its own initiative).
