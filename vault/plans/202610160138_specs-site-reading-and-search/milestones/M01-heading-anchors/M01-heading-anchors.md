---
id: "01"
title: "Headings on Rendered and \u00a7 section anchors"
sp: 3
status: pending
plan: "plans/202610160138_specs-site-reading-and-search/index.md"
---

# M01: Headings on Rendered and § section anchors

Every body heading carries a `§` link to itself, and the renderer hands its headings to the page builder.

**Scope**: `booping-python/src/booping/specs/site/markdown.py` (`Heading(level, text, id, line)` dataclass, `Rendered.headings`, the anchor element appended inside `h2`–`h4`), `templates/record.html.j2` (the anchor on the "Referenced by" `h2`), `site.js` (copy on click, the shared status element, opening a closed `<details>` holding the hash target), `style.css` (`.anchor`), `src/config.yaml` (`section_link`, `link_copied` in `en` and `ru`). Exactly `../../clarifications.md` C2. The anchor is a token appended to the heading's inline children (an `html_inline` token after the text), so the heading `id`, mark anchors (`L{line}`) and table links are unchanged; `Heading.text` is the plain text before the anchor is added.

Tests (integration, `booping-python/tests/specs/site_test.py` via `render_body`): a body with `##`, `###`, `####`, a duplicate `##` title and a `[clarify]` mark in a heading gives hand-derived `headings` (levels, texts, deduplicated ids, lines) and HTML where each of those headings ends with the `§` anchor to its own id and the mark's `L{line}` anchor survives; an `h1` and `h5` get no anchor. Rebaseline `site-*.txtar` goldens and read the diff: anchors on headings only.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | `Heading`, `Rendered.headings`, the anchor in `h2`–`h4` and on "Referenced by"; labels; tests. | `booping-python/src/booping/specs/site/markdown.py`, `booping-python/src/booping/specs/site/templates/record.html.j2`, `src/config.yaml`, `booping-python/tests/specs/site_test.py` | 2 | pending |
| 1.2 | `site.js` copy-link, status element, details-open on hash; `.anchor` CSS; golden rebaseline. | `booping-python/src/booping/specs/site/site.js`, `booping-python/src/booping/specs/site/style.css`, `booping-python/src/booping/specs/site/templates/base.html.j2`, `booping-python/e2e/cases/specs/site-*.txtar` | 1 | pending |

## Definition of Done

### Task 1.1

- [ ] `Rendered.headings` lists every body heading in document order with the id the heading carries.
- [ ] Every body `h2`–`h4` and the "Referenced by" `h2` end with `<a class="anchor" href="#{id}" aria-label="{section_link}: {text}">§</a>`.
- [ ] `section_link` and `link_copied` resolve in `en` and `ru`.

### Task 1.2

- [ ] A click on `.anchor` keeps the navigation and, when `navigator.clipboard` exists, copies the absolute URL and announces `link_copied` in one `role="status"` element for 2 s.
- [ ] On load and on `hashchange`, every closed `<details>` containing the hash target is opened.
- [ ] `.anchor` is visible on heading hover and focus, always visible under `@media (hover: none)`; colour from existing tokens only (`site_contrast_test.py` unchanged and green).
- [ ] `site-*.txtar` goldens rebaselined; their diff is anchors only.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/src/booping/specs/site/markdown.py` — `_html_token`, the `heading_open` branch and the mark-anchor handling the anchor must not disturb.
- `booping-python/src/booping/specs/site/site.js` — script style (one IIFE, no dependencies).

## Verify

`cd booping-python && uv run pytest tests/specs/site_test.py tests/specs/site_contrast_test.py e2e -k site -q`
