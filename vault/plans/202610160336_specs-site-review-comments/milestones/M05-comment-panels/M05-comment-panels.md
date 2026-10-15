---
id: "05"
title: "Record and site-wide comment panels with copy and clear"
sp: 4
status: pending
plan: "/home/anton/Dev/@A/claude-booping-specs/vault/plans/202610160336_specs-site-review-comments/index.md"
---

# M05: Record and site-wide comment panels with copy and clear

The reader lists, edits and deletes their comments in a record panel and on `comments.html`, copies them as one markdown block for an agent, and clears what was sent.

**Scope**: `booping-python/src/booping/specs/site/comments.js` and `booping-python/src/booping/specs/site/style.css`, nothing else. Behaviour exactly `../../clarifications.md` C5:

- Record panel: `button.cmt-open` opens `dialog.cmt-sheet` via `showModal()`; it lists this page's comments (`ref` equal to the article's `data-ref`) by `created`: anchor link (`#{anchor}` on this page, closing the dialog on click), quote as a blockquote, note, a `sent` badge when sent, Edit and Delete buttons.
- Site-wide panel: on `comments.html`, `div.cmt-groups` gets one group per record (ordered by `ref`): an h2 linking `{prefix}{page}` with ref + title, then the same item markup with anchor links to `{prefix}{page}#{anchor}`; `p.needs-js` hidden when JS runs; the empty-state line when there are none.
- Edit: the note turns into a labelled textarea with Save/Cancel in place; Save writes the note, resets `sent`, refreshes counts. Delete removes at once and announces `comment_deleted` in `#status`.
- Copy for the model: builds the block with `SpecsComments.format(scopeComments, siteRoot)` (`comments-format.js`, M02), writes it via `navigator.clipboard.writeText`, falling back to a hidden-textarea `document.execCommand('copy')`; success → those comments `sent: true`, announce `comments_copied_n`; failure → announce `copy_failed`, nothing marked. Disabled when the scope is empty.
- Clear sent: removes the scope's `sent` comments, announces `comments_cleared_n`; disabled when none is sent.
- Every list re-renders from the store after each change and on `storage` events; all text inserted with `textContent`, never `innerHTML` of stored strings.
- CSS: the sheet is a right-side panel (width `min(28rem, 100vw)`, full height) ≥ 760px and a bottom sheet below (full width, rounded top, `max-height: 80vh`, inner scroll, `::backdrop` dimmed); every button and link in the list ≥ 44px tall under `(pointer: coarse)`; text wraps, no horizontal scroll at 390px.

Tests: none new in pytest — DOM-only; the export text is held by M02's test, the browser check by the index Final Verification. The `site-*.txtar` goldens change only in the shipped `comments.js` and `style.css` bodies.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Record sheet and `comments.html` lists; edit and delete; side/bottom sheet CSS. | `booping-python/src/booping/specs/site/comments.js`, `booping-python/src/booping/specs/site/style.css` | 2 | pending |
| 5.2 | Copy for the model with fallback and `sent` marking; Clear sent; announcements; golden rebaseline. | `booping-python/src/booping/specs/site/comments.js`, `booping-python/e2e/cases/specs/site-*.txtar` | 2 | pending |

## Definition of Done

### Task 5.1

- [ ] With two comments on one record and one on another, the record panel lists that record's two and `comments.html` lists all three in two groups, checked by the worker in headless Chromium on a built fixture site.
- [ ] Edit and Delete change the store and every visible count without reload; stored text containing `<b>` renders as text.

### Task 5.2

- [ ] Copy puts exactly `SpecsComments.format(...)` of the scope on the clipboard and marks those comments sent; Clear sent removes only sent ones in the scope.
- [ ] Each action announces its label in `#status`.
- [ ] `site-*.txtar` rebaselined with `just e2e -k site --txtar-update`; diff limited to `comments.js` and `style.css`.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/src/booping/specs/site/search.js` — `renderPage()`: filling a JS-populated page with `textContent`.
- `booping-python/src/booping/specs/site/site.js` — `announce()` on `#status`.
- `../../clarifications.md` — C2, C5.

## Verify

`cd booping-python && uv run pytest tests/specs/site_comments_format_test.py e2e -k site -q`
