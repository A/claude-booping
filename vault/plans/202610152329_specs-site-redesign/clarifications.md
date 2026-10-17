# Clarifications

Autonomous run — the owner was unavailable; every question below was settled by the run with a default.

## C1 — source precedence — answered

**Asked:** 2026-10-15 — intake

**Question:** The brief, the approved mockup and the base spec disagree in places (palette hex values, fonts, home page, drawer). Which wins?

**Answer:**

Brief's owner corrections > the approved mockup `specs-site-mockup.html` > the base spec. Where the brief's own Typography hex values differ from the mockup's tokens (light `--bg #f7f8fa` + `--surface #ffffff`, link `#1f56b3`; dark link `#86b3ff`, border `#2c3038`), the mockup's tokens win: the brief says to match the mockup's palette tokens and the owner approved the mockup after the brief's values were written. Type scale, measure and dark text/bg values agree in both.

## C2 — split — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** The whole redesign estimates at ~70 SP, past the 35 SP split threshold. Where is the seam?

**Answer:**

Three plans. This plan (part 1) is the foundation every later page builds on: shipped fonts, labels and `lang`, the theme and icon sprite, the page shell (header, sidebar, drawer, breadcrumbs, skip link, footer), the record model and record page head with state badges and titled relations, type/root/home pages as plain lists instead of concatenated bodies and count matrices, the machine layer, and `site-index` in the same design. Parked siblings, each groomed in its own run: (2) "Specs site — landing, review filter and list filters": the documentation landing with the one "N need you →" link, review as a filter over the list with reason icons and mark anchors, list filter chips and sort with `location.hash` state, the Source (tier) facet, phone cards for lists, tag pages and the tag tree from `tags.yaml`; (3) "Specs site — record reading and search": ToC rail and phone `<details>`, `§` heading anchors, backlinks grouped by type and by section, ADR option cards (chosen first and open), the Cyrillic-aware vanilla search with its index scripts, header search box and phone search overlay. Priority 3 of the base spec (relation graph, hover previews) is skipped.

## C3 — fonts and file:// — answered

**Asked:** 2026-10-15 — research-web

**Question:** The brief asks for woff2 files in the site output. Firefox (`security.fileuri.strict_origin_policy`, default on) blocks a font loaded from a parent or sibling directory of the page under `file://`; record pages sit two directories deep. How are the fonts shipped?

**Options:**

- woff2 files in the output, `url()` from the shared stylesheet — breaks every nested page in Firefox from `file://`
- a fonts directory copied into every directory that holds pages — duplicated bytes per directory
- the woff2 bytes base64-embedded in one shared `fonts.css` — one file, works everywhere

**Answer:**

Vendor the woff2 files once in the repo (`booping-python/src/booping/specs/site/fonts/`): `@fontsource-variable/golos-text@5.3.0` `golos-text-{cyrillic,latin}-wght-normal.woff2` (variable, covers 400–700, 58 KB together — smaller than four static weights) and `@fontsource-variable/jetbrains-mono@5.3.0` `jetbrains-mono-{cyrillic,latin}-wght-normal.woff2` (52 KB), each package's `LICENSE` (OFL 1.1) beside them. The site output carries `fonts.css` with the bytes as `data:font/woff2;base64,` URIs and the packages' `unicode-range` values, `font-display: swap`, plus the two licence texts under `fonts/`. Nothing is fetched at render or view time.

## C4 — labels and lang — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** Where do the UI labels and the locale live?

**Answer:**

In config, so a user adds a locale or labels a tier-own type without touching code (value/0006, rule/0017): `core.specs.site.lang` (default `en`) and `core.specs.site.labels.{lang}` — `ui` (shell and page strings), `types.{type}` (`name`, `plural`, `scenario` — the one-line reading scenario), `statuses.{status}`, `facts.{key}`, `authors.{owner,claude}`, `months` (12 names, the form used after a day number). Core ships `en` and `ru`. A project labels its own types in its vault config (swarmlight: `core.specs.site.labels.ru.types.mechanic`). Lookup falls back key by key to `en`, then to the raw id; an unknown `lang` renders with `en` labels, keeps `<html lang>` as configured and prints one `warning:` line on stderr.

## C5 — site title — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** The header brand, `<title>` and `llms.txt` H1 need a site title; `booping specs site` has none today.

**Answer:**

A new `--title TEXT` flag on `booping specs site`, default the attached project's name (the root-naming fallback the command already uses), `Specs` with no project. Mirrors `site-index --title`.

## C6 — footer build date — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** The base spec's footer carries a build date; the output must be byte-stable for the same input.

**Answer:**

No date. The footer names the generator (`booping specs site`) only — a date would break the byte-identical rebuild (value/0015, rule/0027). Recency is shown per record from `updated_at`.

## C7 — phone drawer without JS — answered

**Asked:** 2026-10-15 — research-web

**Question:** The base spec ports the old generator's CSS checkbox hack; the mockup uses a JS drawer; content must stay reachable without JS.

**Answer:**

A real `<button aria-expanded aria-controls>` opens the drawer (scrim, Esc and scrim tap close it, focus moves into it) through `site.js`; the checkbox hack is dropped for its keyboard and screen-reader failures. The inline head script adds class `js` to `<html>`; without it, the narrow layout shows the sidebar in the normal flow after the main content, so nothing hides behind JS.

## C8 — theme toggle — answered

**Asked:** 2026-10-15 — research-web

**Question:** How does the auto/light/dark toggle behave?

**Answer:**

One `<button>` in the header cycles auto → light → dark → auto; its `aria-label` and `title` name the current state (labels `theme_auto`/`theme_light`/`theme_dark`). The choice is `localStorage["specs-theme"]`, auto is the absence of the key. A synchronous inline script in `<head>`, before the stylesheets, sets `data-theme` on `<html>` from it — no flash. CSS: `:root` light tokens, `:root[data-theme=dark]` and `@media (prefers-color-scheme: dark) { :root:not([data-theme=light]) }` dark tokens, `color-scheme` set per theme. Without JS the system preference applies.

## C9 — machine layer formats — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** Rule booping:rule/0010 asks to lock the exact content of output formats. What exactly do `llms.txt`, `index.json`, the `.md` copies and `404.html` hold?

**Answer:**

- `llms.txt`: `# {title}`; a blank line; `> {summary of the first value record of the first root that has one}` (omitted when none); then per root in order, per type in the site's type order, `## {type plural label} — {root}` and one line per record `- [{ref} {title}]({record page path with .md}): {summary} ({status label}; {tags joined by ", "})` — the parenthetical drops an empty part and disappears when both are empty; `[`, `]` in a title are backslash-escaped; a record with no summary ends after the link. Paths are site-root-relative. Ends with one newline.
- `index.json`: `{"title", "lang", "records": [...]}`, records in page order, each `{"id": "{root}:{ref}", "root", "ref", "type", "title", "summary", "status", "kind", "tags", "created_by", "created_at", "updated_at", "reviewed", "url", "md", "marks": {"clarify": n, "unknown": n}, "relations": {"{key}": [id, …]}, "superseded_by": [id, …], "backlinks": [id, …]}`; absent frontmatter values are `null` (lists `[]`); relations hold every frontmatter ref-list key that resolves, in key-sorted order; `json.dumps(…, ensure_ascii=False, indent=1)` plus a trailing newline.
- `.md` copies: beside each record page, `{stem}.md` holding the record's source file bytes verbatim; the record page carries `<link rel="alternate" type="text/markdown" href="{stem}.md">`. Generated list pages get none — `llms.txt` is their machine form.
- `404.html`: written only when `--site-url URL` is given; the page shell with a "not found" message and a link home, and `<base href="{path of URL with a trailing slash}">` right after `<meta charset>`, so its relative links work at any depth GitLab Pages serves it. The shipped Pages template passes `--site-url "$CI_PAGES_URL"`.

## C10 — what part 1 does with list pages — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** Type pages concatenate full record bodies and the root is a count matrix; filters and the landing are part 2. What do those pages show in part 1?

**Answer:**

Plain lists. A type page lists its records as rows — mono ref, linked title, summary, state badges — and the second, id-prefixed body render goes away. A root page lists its types (plural label, scenario line, count) and its marks. The home page drops the tier × type matrix: H1 title, then per root the same type list. Part 2 turns these into the landing and the filterable lists.

## C11 — dates — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** The mockup shows "15 октября 2026"; frontmatter holds `YYYY-MM-DD`.

**Answer:**

Facts render `{day} {months[month-1]} {year}` from the labels (`15 октября 2026`, `15 October 2026`) inside `<time datetime="YYYY-MM-DD">`; a value that is not a `YYYY-MM-DD` date renders as given. `reviewed` empty renders the `not_reviewed` label.
