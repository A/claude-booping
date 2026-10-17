---
id: "04"
title: "Comment affordances and the compose dialog"
sp: 4
status: done
plan: "/home/anton/Dev/@A/claude-booping-specs/vault/plans/202610160336_specs-site-review-comments/index.md"
---

# M04: Comment affordances and the compose dialog

On a record page the reader starts a comment on a selected span, a paragraph or a section heading — by mouse, keyboard or touch — writes a note in the compose dialog and saves it to the store.

**Scope**: `booping-python/src/booping/specs/site/comments.js` and `booping-python/src/booping/specs/site/style.css`, nothing else. Behaviour exactly `../../clarifications.md` C4 and the Compose bullet of C5:

- Section buttons: after each `.body` h2–h4 `a.anchor`, insert `button.cmt-add` (`i-comment` via `<svg><use href="#i-comment">`, aria-label `comment_section` from the dialog's `data-*`), kind `section`, anchor = the heading id, `anchorText` and `quote` = the heading text without `§`.
- Selection: one floating `button.cmt-float` per C4 — shown for a non-empty selection whose range lies inside `article .body`, positioned under the selection's last client rect, debounced; kind `span`, quote = `selection.toString()`.
- Paragraph: click/tap on a body `p`, `li`, `blockquote`, `td` or `pre` with a collapsed selection shows `button.cmt-float` beside that block, label `comment_paragraph`; kind `paragraph`, quote = the block's `textContent`. Clicks on links inside the block keep their default.
- Anchor for `span`/`paragraph`: the nearest h2–h4 with an id preceding the selection start / block in document order inside `.body`; none → empty anchor and `anchorText`.
- Compose: `dialog.cmt-compose` via `showModal()`, preview filled with the quote, Save disabled while the note is blank, Ctrl/Cmd+Enter saves, Escape/Cancel close without saving, focus returns to the opener; Save stores `{ref, title, page}` from the article's `data-*`, `created` as ISO time, `sent: false`, clears the selection and refreshes the counts.
- CSS: `.cmt-add` and `.cmt-float` visible focus ring, ≥ 44 × 44 px under `(pointer: coarse)`; the compose dialog is a bottom sheet below 760px (full width, rounded top, `max-height: 80vh`, inner scroll) and a centred box above; `prefers-reduced-motion` drops any transition.

Tests: none new in pytest — the behaviour is DOM-only; the runner's browser check (index Final Verification) covers it. The `site-*.txtar` goldens change only in the shipped `comments.js` and `style.css` bodies.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Section buttons, floating span/paragraph button, anchor resolution. | `booping-python/src/booping/specs/site/comments.js`, `booping-python/src/booping/specs/site/style.css` | 2 | done |
| 4.2 | Compose dialog wiring, save to store, keyboard and focus; phone sheet CSS; golden rebaseline. | `booping-python/src/booping/specs/site/comments.js`, `booping-python/src/booping/specs/site/style.css`, `booping-python/e2e/cases/specs/site-*.txtar` | 2 | done |

## Definition of Done

### Task 4.1

- [x] Each C4 trigger opens the compose dialog with the right kind, anchor and quote, checked by the worker in headless Chromium on a built fixture site (`bin/booping specs site --out /tmp/…`).
- [x] Without JS or without storage no comment control is visible.

### Task 4.2

- [x] A saved comment is in localStorage under the C5 key with every C5 field; the header and sidebar counts update without reload.
- [x] Tab reaches every section button; Escape closes the dialog and focus returns to the opener.
- [x] `site-*.txtar` rebaselined with `just e2e -k site --txtar-update`; diff limited to `comments.js` and `style.css`.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/src/booping/specs/site/site.js` — event-delegation and focus-return style (the drawer).
- `booping-python/src/booping/specs/site/style.css` — the 760px block and the 44px tap-target literals.
- `../../clarifications.md` — C3, C4, C5.

## Verify

`cd booping-python && uv run pytest e2e -k site -q`
