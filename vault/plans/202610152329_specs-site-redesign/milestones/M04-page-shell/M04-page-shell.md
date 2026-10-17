---
id: "04"
title: "Page shell — header, theme toggle, sidebar, drawer, crumbs, footer"
sp: 4
status: done
plan: "plans/202610152329_specs-site-redesign/index.md"
---

# M04: Page shell — header, theme toggle, sidebar, drawer, crumbs, footer

Every site page sits in one shell: a skip link, a sticky header with the site title, a phone menu button and the auto/light/dark theme toggle, a left sidebar listing each root's types, a phone drawer, breadcrumbs and a footer — with no flash of the wrong theme and everything reachable without JS.

**Scope**: rewrite `booping-python/src/booping/specs/site/templates/base.html.j2` after the mockup's shell (`../../design/specs-site-mockup.html`, `.app` → `.top`, `.drawer`, `.body`): in `<head>` after `<meta charset>` and viewport, a synchronous inline `<script>` (C8) that reads `localStorage["specs-theme"]` inside `try`, sets `data-theme` on `<html>` when it is `light`/`dark` and adds class `js`; then `<meta name="color-scheme" content="light dark">`, `<link rel="stylesheet" href="{prefix}fonts.css">`, `<link rel="stylesheet" href="{prefix}style.css">`, `<script src="{prefix}site.js" defer>`; `<body>`: `{% include "_icons.html.j2" %}`, `<a class="skip" href="#main">{ui skip}</a>`, `<header class="top">` (menu `<button class="iconbtn menu" aria-expanded="false" aria-controls="drawer" aria-label="{ui menu}">` with `i-menu`, phone only; brand link to `{prefix}index.html` with `site_title`; theme `<button class="iconbtn theme" aria-label="{ui theme_auto}">` with `i-auto`, hidden until `html.js`), `<div class="body">` with `<nav class="side" id="drawer" aria-label="{ui types}">` — Overview link, then per root a group heading (root name) and its types (plural label + record count, current page `aria-current="page"`) — the `main#main` holding the breadcrumbs `<nav class="crumbs" aria-label="breadcrumb">` (`<ol>`, last item `aria-current="page"`, middle items `class="mid"` hidden on phone) and `{% block main %}`, an optional `{% block rail %}` (empty → `.norail`); `<footer>` with `ui generator` (C6, no date). The sidebar's data comes from `build_site` (`pages.py`) as one `nav` context value computed once — `[{root, types: [{type, label, count, href}]}]` — with hrefs made page-relative through the existing `prefix`. New `booping-python/src/booping/specs/site/site.js` (≤ 60 lines, no dependency): theme button cycles auto → light → dark → auto, writes or removes `localStorage["specs-theme"]` (wrapped in `try`), updates `data-theme`, icon (`i-auto i-sun i-moon`) and `aria-label`/`title`; menu button toggles `.drawer-open` on `<body>` and `aria-expanded`, adds a `.scrim` that closes on click, closes on Esc and returns focus to the button, moves focus to the first sidebar link on open. `build_site` and `build_index` add `site.js` to their files. Every existing page template keeps extending `base.html.j2`; `site_index.html.j2` renders without a sidebar (empty `nav`).

Tests (integration): `site_pages_test.py` — every built page has exactly one `<main id="main">`, one skip link targeting it, `<html lang>`, both stylesheet links and the script with a correct relative prefix at depth 0, 1 and 2 (the existing `_Links` checker resolves them to files in the output); the sidebar of a two-root site lists both roots' types with counts and marks the current type page `aria-current`; the head script precedes the first `<link rel="stylesheet">`. Rebaseline `site-*.txtar` and `site-index-*.txtar` goldens and read the diff: only the shell changes.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | `base.html.j2` shell, the `nav` context in `build_site`, crumbs as `<ol>`, the tests, golden rebaseline. | `booping-python/src/booping/specs/site/templates/base.html.j2`, `booping-python/src/booping/specs/site/pages.py`, `booping-python/src/booping/specs/site/index.py`, `booping-python/tests/specs/site_pages_test.py`, `booping-python/e2e/cases/specs/site-*.txtar` | 3 | done |
| 4.2 | `site.js` theme cycle and drawer, shipped in both outputs. | `booping-python/src/booping/specs/site/site.js`, `booping-python/src/booping/specs/site/pages.py`, `booping-python/src/booping/specs/site/index.py` | 1 | done |

## Definition of Done

### Task 4.1

- [x] Without JS every page shows its full content and its sidebar (in flow on narrow screens).
- [x] Keyboard path: Tab from page top reaches skip link, menu (phone), brand, theme toggle, sidebar links, main content in that order.
- [x] The new `site_pages_test.py` cases pass; rebaselined goldens differ only in shell markup.

### Task 4.2

- [x] `site.js` has no `fetch`, no module syntax, no external reference; loads from `file://`.
- [x] Theme choice survives a reload; auto removes the key.
- [x] Esc and scrim close the drawer and restore focus to the menu button.

Return: the list of changed and created files, nothing else.

## References

- `../../design/specs-site-mockup.html` — shell markup and the drawer/scrim behaviour.
- `booping-python/src/booping/specs/site/templates/base.html.j2` — current shell and the `prefix` convention.
- `booping-python/tests/specs/site_pages_test.py` — the `_Links` checker.

## Verify

`cd booping-python && uv run pytest tests/specs e2e -k site -q`
