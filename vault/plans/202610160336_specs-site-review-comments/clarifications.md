# Clarifications

## C1 — where the comment logic runs — answered

**Asked:** 2026-10-16 — intake

**Question:** The request allows a server-side copy-format builder (then unit tests) or a client-side one (then a golden of the HTML hooks). Which?

**Answer:**

Default (autonomous run): client-side. Comments are browser state only and never reach the build, so nothing server-side can format them. The generator writes static hooks — record identity as `data-*` on the article, the sidebar entry, the panel and compose `<dialog>` shells with their labels, the `comments.html` page shell — held by the `site-*.txtar` goldens and `site_pages_test.py` (value/0015, booping:rule/0027: byte-stable output). Beyond the request's minimum, the pure export builder lives in its own shipped file `comments-format.js` and is unit-tested by pytest running it under `node` with hand-derived expectations (value/0010: a behaviour that matters is held by a check). `node` is on PATH locally and on GitHub's `ubuntu-latest`; a missing `node` fails the test, it never skips.

## C2 — export format — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** Exact content of the "Copy for the model" block (booping:rule/0010 — output content is locked in grooming)?

**Answer:**

Default (autonomous run). The block carries no translatable words, so it reads the same on an `en` and a `ru` site:

```
## {ref} — {title}

[§ {anchor text}]({anchor url})

> {quote line 1}
> {quote line 2}

{note}

[§ {anchor text}]({anchor url})

> {quote}

{note}

## {next ref} — {next title}

…
```

- Records ordered by `ref` (plain code-unit string compare); a record's comments by `created` ascending, ties by `id`.
- `{ref}`, `{title}` — the record's ref and title as the page states them (`data-ref`, `data-title`).
- Anchor line: `[§ {heading text}]({page url}#{heading id})` when the comment sits under an h2–h4; a comment above the first such heading gets `[{title}]({page url})`. `{page url}` is absolute: the site root URL (resolved in the browser from the page's `prefix`) plus the record page path — an `https://` URL on a published site, a `file:///` URL locally.
- Quote: the stored quote split on line breaks, each line trimmed, empty lines dropped, each line prefixed `> `. Span → the selected text; paragraph → the block's text; section → the heading text without the `§`.
- Note: verbatim, trailing whitespace trimmed, inner line breaks kept.
- One blank line between parts; the block ends with exactly one `\n`. Nothing to copy → the button is disabled.

## C3 — anchors for spans and paragraphs — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** Paragraphs carry no ids (only h2–h4 and marked blocks do). Give every block a generated id, or anchor span/paragraph comments to their section?

**Answer:**

Default (autonomous run): a span or paragraph comment anchors to the nearest preceding h2–h4 of the body (its slug id, the same § link the page already offers), and the quote pins the exact text. Generating an id per block would churn every golden and break whenever a line above moves (line-number ids); heading slugs are already the page's stable links. No HTML changes in `markdown.py`.

## C4 — comment affordances — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** How does the reader start a comment on a span, a paragraph and a heading, by mouse, keyboard and touch?

**Answer:**

Default (autonomous run), all JS-injected, so the generated HTML holds none of them:

- **Section**: a "Comment" icon button (`i-comment`, aria-label "Comment on this section") inserted after each body h2–h4 § anchor — Tab-reachable, the keyboard path.
- **Span**: a non-empty selection inside the article's `.body` shows one floating "Comment" button just below the selection's last client rect (below, not above, so it clears the native iOS/Android selection menu), on `selectionchange` debounced ~150 ms plus `pointerup`/`keyup`; hidden when the selection collapses or leaves `.body`. It is inserted in the DOM right after the block holding the selection end, so Tab from a keyboard selection reaches it.
- **Paragraph**: a click/tap on a body block (`p`, `li`, `blockquote`, `td`, `pre`) with no selection shows the same floating button beside that block, labelled "Comment on paragraph"; clicking elsewhere hides it.
- Every button is ≥ 44 × 44 px on touch (`pointer: coarse`) and has a visible focus ring.

## C5 — panels, compose box and storage — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** Shape of the compose box, the record panel, the site-wide panel, and the storage?

**Answer:**

Default (autonomous run):

- **Compose**: a `<dialog class="cmt-compose">` opened with `showModal()` — the quote (or heading) as a blockquote preview, one `<textarea>`, Save and Cancel; Ctrl/Cmd+Enter saves, Escape cancels, focus returns to the opener. Empty note → Save disabled.
- **Record panel**: a header icon button (`i-comment` + count) on record pages opens `<dialog class="cmt-sheet">` via `showModal()`: a right-side sheet ≥ 760px, a bottom sheet (max-height 80vh, rounded top, scrolls inside) below 760px. It lists this record's comments: anchor link, quote, note, a "sent" badge, Edit (inline textarea, Save/Cancel) and Delete, then "Copy for the model" and "Clear sent".
- **Site-wide panel**: a page `comments.html` at the site root (JS-populated shell like `search.html`, a no-JS fallback line) listing every comment grouped by record (ref + title linking the page), same item controls, Copy and Clear sent over all. A sidebar entry "My comments" with a count sits after "All records"; the count shows when > 0.
- **Copy** writes the C2 block with `navigator.clipboard.writeText` (file:// is a secure context), falling back to a hidden-textarea `execCommand('copy')`; success marks every copied comment `sent: true` and announces "{n} copied" in `#status`; failure announces a copy error and marks nothing.
- **Clear sent** deletes the panel's comments with `sent: true` and announces "{n} cleared"; disabled when none is sent. Editing a note resets its `sent`.
- **Delete** removes at once and announces "Comment deleted"; no confirm.
- **Storage**: one localStorage key `specs-comments:v1:{site root URL}`, a JSON array of `{id, ref, title, page, anchor, anchorText, kind: span|paragraph|section, quote, note, created, sent}`; every read/write in try/catch — storage unavailable leaves the affordances hidden and the panels showing a "Comments need browser storage" line. Every page re-reads storage on `storage` events, so two open tabs stay in step.

## C6 — the root page — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** What does `{root}/index.html` show, and where does the callout link?

**Answer:**

Default (autonomous run): the Overview landing scoped to the root, rendered by the same macros as `index.html` (value/0003): h1 = the root name, no lead (the site lead is site-level), the callout with that root's counts — `needs` = review rows whose source is this root, `unreviewed`, `open questions` — linking `../review.html#source={root}` (the review page's existing Source facet), scenario cards (`{type}/index.html`, quiet count, scenario line), Recently updated (the root's ten latest). The mark list and the "Records: N" labels go; the now-unused `types_list` macro and, if nothing else reads it, the `records` label are removed (booping:rule/0007). Marks stay reachable from the review page and each record's questions block.

## C7 — Firefox and file:// — answered

**Asked:** 2026-10-16 — research-web

**Question:** Firefox gives each `file://` page its own storage origin, so on a local site the site-wide panel sees only comments made on that one page. Work around it?

**Answer:**

Default (autonomous run): no workaround — a known limitation, stated in `documentation/specs.md` (Chrome/Chromium share one store across `file://`; published sites are unaffected). A workaround would need a server or a shared file, which the request rules out ("no network").

## C8 — approval gate — answered

**Asked:** 2026-10-16 — present

**Question:** Approve the plan for development?

**Answer:**

Default (autonomous run): approved by the run under the owner's instruction "do not wait at review gates — auto-confirm them yourself". No split: the total is under the 35 SP threshold. No plan branch: the run stays on `feat/specs` as instructed.
