---
id: "02"
title: "Comment export builder and its node test"
sp: 3
status: done
plan: "/home/anton/Dev/@A/claude-booping-specs/vault/plans/202610160336_specs-site-review-comments/index.md"
---

# M02: Comment export builder and its node test

The "Copy for the model" markdown block exists as one pure, shipped function whose exact output a test pins.

**Scope**: create `booping-python/src/booping/specs/site/comments-format.js` — vanilla ES5-style JS like `site.js`, no DOM access, defining `formatComments(comments, siteRoot)` and assigning it to `globalThis.SpecsComments = { format: formatComments }`. `comments` is an array of stored comments (`{id, ref, title, page, anchor, anchorText, kind, quote, note, created, sent}`, `../../clarifications.md` C5); `siteRoot` is the absolute site root URL ending in `/`. It returns the block exactly as C2 locks it: records by `ref` (code-unit compare), comments by `created` then `id`; anchor line `[§ {anchorText}]({siteRoot}{page}#{anchor})`, or `[{title}]({siteRoot}{page})` when `anchor` is empty; in the anchor id, ` `, `(`, `)` and `%` are percent-encoded, nothing else; quote lines trimmed, empty ones dropped, each prefixed `> `; note with trailing whitespace trimmed; one blank line between parts; exactly one trailing `\n`; an empty array returns `""`. Add `comments-format.js` to the files `pages.py` ships verbatim (beside `site.js`, `filter.js`, `search.js`), no `<script>` tag yet (M03 adds it).

Tests (integration, create `booping-python/tests/specs/site_comments_format_test.py`): a helper runs `node` with a short inline script that loads the file's text from `booping.specs.site` package data into `vm.runInNewContext` and prints `SpecsComments.format(...)` for JSON passed on stdin; `node` missing → the test fails with a clear message, never skips. Cases, each with the full expected string written by hand: two records given in reverse ref order with two comments on one (created out of order) → grouped and ordered per C2; a section comment (quote = heading text); a comment with empty `anchor` → title link, no `#`; a multi-line quote with blank and indented lines; a note with trailing spaces and an inner line break; a Cyrillic title and anchor (anchor kept raw) and an anchor holding `(`; the empty array → `""`. One more assertion: `build_site` output holds `comments-format.js` byte-identical to the source file.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | `comments-format.js` per C2; shipped by `pages.py`. | `booping-python/src/booping/specs/site/comments-format.js`, `booping-python/src/booping/specs/site/pages.py` | 1 | done |
| 2.2 | Node-run unit tests with hand-derived expected blocks. | `booping-python/tests/specs/site_comments_format_test.py` | 2 | done |

## Definition of Done

### Task 2.1

- [x] `formatComments` matches every C2 bullet; the file touches no DOM, `window` or storage.
- [x] The built site holds `comments-format.js`; `index.json`, `llms.txt` and the search files do not mention it.

### Task 2.2

- [x] Every case above is a test with its full expected string; all pass under `node`.
- [x] Without `node` on PATH the test fails with a message naming `node`.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/src/booping/specs/site/site.js` — the JS style (`var`, no build step, no modules).
- `booping-python/tests/specs/site_search_test.py` — test module shape for the site package.
- `../../clarifications.md` — C2 (format), C5 (stored comment shape).

## Verify

`cd booping-python && uv run pytest tests/specs/site_comments_format_test.py -q`
