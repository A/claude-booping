# Clarifications

Autonomous run — the owner was unavailable; every question below was settled by the run with a default. Design sources are part 1's copies: `plans/202610152329_specs-site-redesign/design/` (`brief.md`, `specs-site-design.md`, `specs-site-mockup.html`), precedence brief > mockup > base spec (part 1 C1).

## C1 — scope — answered

**Asked:** 2026-10-16 — intake

**Question:** Which part of the request does this plan take?

**Answer:**

Part 3 exactly as parts 1 and 2 parked it (part 1 C2, part 2 Out of scope): the sticky "On this page" ToC rail and its phone `<details>` together with the record's open questions, `§` heading anchors, backlinks grouped by type and by section, ADR option cards, and the Cyrillic-aware vanilla search (`search-index.js`, `search-body.js`, header box with `/`, phone overlay, `search.html?q=`). This is the last part of the request. Base-spec priority 3 (relation graph, hover previews) stays skipped; git history / source links from a repo URL and tag chips on list pages stay out.

## C2 — headings and `§` anchors — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** What is a section anchor, which headings get one, and what does clicking it do?

**Answer:**

- `render_body` collects every body heading as `Heading(level, text, id, line)` on `Rendered.headings`, in document order; `id` is the slug the heading already carries (part 1 `_unique_slug`), `text` its plain text without marks markup.
- Every body `h2`–`h4`, and the page's own "Referenced by" `h2`, ends with `<a class="anchor" href="#{id}" aria-label="{section_link}: {text}">§</a>` (rustdoc places it on hover; here it follows the text so heading text and ToC stay first). Desktop: visible on heading hover and on focus; `@media (hover: none)`: always visible in `--faint`.
- `site.js`: a click on `.anchor` lets the navigation happen (the hash changes, the link stays a real link without JS) and, when `navigator.clipboard` exists, writes the absolute URL (`location.href` with the new hash) to it and announces `link_copied` in one shared `role="status"` element for 2 s. `file://` is a secure context (MDN, Secure Contexts), so the clipboard works there.
- `site.js` also opens every closed `<details>` that contains the hash target, on load and on `hashchange` — the ADR table links into collapsed option cards (C5) and the ToC links into the phone `<details>` (C3).

## C3 — ToC rail, open questions, phone `<details>` — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** What does the rail hold, when is it shown, and what replaces it on narrow screens?

**Answer:**

- Rail on record pages only, filling part 1's unused `{% block rail %}`. Blocks, top to bottom: `<nav aria-labelledby>` headed `on_this_page` — the body's `h2` entries with their `h3` entries nested, then "Referenced by" — and, when the record has marks, a block headed `open_questions` (the existing plural label with its count) listing each `[clarify]` mark then each `[unknown]` mark, in line order within a kind, as a link to `#L{line}` with the mark's cut text and the kind's icon. The ToC block is rendered when it has ≥ 2 entries; the rail is rendered when either block is.
- Sticky (`position: sticky; top` below the header), own scroll when taller than the viewport. `site.js` marks the rail link of the section in view with `aria-current="location"` through one `IntersectionObserver` over the ToC's target headings with `rootMargin: "0px 0px -70% 0px"` (no scroll handlers): the current section is the last target heading, in document order, whose top has crossed into the top 30% of the viewport; before the first one, none is current. Without JS nothing is marked.
- Rail shown at ≥ 1100px. Below 1100px (phone included) the rail is hidden and the same two blocks render server-side in one `<details class="toc-m">` right after the lead, closed, summary `{on_this_page} · {open_questions with n}` (the second part only when marks exist) — the mockup's `.toc-m`. Departs from the brief's "under the title": it sits under the summary lead, as the base spec says, so the lead stays the first thing read.

## C4 — backlinks by type and by section — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** The base spec says "by section" means which `##` of the citing record links here; the old generator's `backlinks()` groups by the viewed record's heading the link's `#anchor` names. Which one?

**Answer:**

Both, because they answer different questions and both come from data the site already has:

- **By type**: one `h3` per type of the citing records (site type order, plural label), each a list of citing records (`rel_item`: ref, title, status badge) in page order. Each item ends with a `via` line in `--muted`: the labels of the frontmatter relation keys through which the source names this record (e.g. "Rules"), then the `h2` text of each section of the source's body holding a link here — each label once: first the relation labels in the source's frontmatter key order, then the section texts in body order, each text once however many links that section holds; a body link before any `h2` reads as the source record's title. This is the base spec's "which `##` of the citing record links here".
- **By section** (port of shatterlings `backlinks()`): when any incoming body link carries an anchor matching one of this record's heading ids, an `h3` `by_section` lists those headings in document order, each `<a href="#{id}">{heading text}</a> ← {citing refs, linked}`.
- Computed in a new `site/backlinks.py` from `Site.backlinks`, `Site.relations` and the sources' `Rendered.links` + `Rendered.headings` after every body is rendered; `model.py`'s `_backlinks` is not changed. Empty → the existing `nothing_references` line. `index.json` keeps its flat `backlinks` (part 2 C1: machine layer unchanged).

## C5 — ADR option cards — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** How do ADR alternatives render, which option is open, and what happens on the phone?

**Answer:**

- Applies to a record of type `adr` whose body has a `## Alternatives` section holding the options table (`src/specs/schemas/adr.yaml`: Option, Status, Complexity, Reversibility, Verdict; Option cell `[name](#anchor)`) and `###` option sections. The shape matches when the body has exactly one `## Alternatives` `h2` and the first block under it is a table whose header cells are exactly those five names in that order; anything else — no section, no table, other columns — renders as today, never an error and never a partial transform. With a matching table, each `###` under the section becomes a card; rows naming no `###` are ignored.
- Table: kept as the summary, class `alts`; the row of each `accepted` option gets class `chosen` and a `chosen` badge after its status badge.
- Each `###` option section becomes `<details class="opt{ chosen}" {open}>` with `<summary>` holding the option's `h3` (id and `§` anchor kept, so table links and the ToC still work) and a `.meta` row: status badge (`chosen` label for accepted), `complexity: {level}`, `reversibility: {level}` from the table row whose Option anchor equals the heading id; `<div class="in">` holds `<p class="verdict">{verdict}</p>` then the section's own body (paragraph, `**Pros:**` / `**Cons:**` / `**Complexity:**` / `**Reversibility:**` bullets, unchanged). A section with no matching table row gets no meta and no verdict.
- Order: accepted cards first, open; then the rest in written order, closed. The mockup's `.opt` styles (already in `style.css`) are used.
- Below 760px the `alts` table is hidden — the cards carry all its columns (brief: one card per option on the phone).
- Level values `low` / `medium` / `high` and the two names get labels (C8); the record's own `**Pros:**`-style bullet text stays as written (English structure, format guide).

## C6 — search data files — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** booping:rule/0010 asks to lock the exact content of output formats. What do `search-index.js` and `search-body.js` hold?

**Answer:**

- `search-index.js`: `window.SPECS_INDEX = {json};` plus a trailing newline. `{json}` is a list in page order of `{"id": "{root}:{ref}", "ref", "root", "type", "type_label" (singular type label), "title", "summary", "status", "status_label", "tags", "url" (site-root-relative record page path), "flags" (subset of `["unreviewed", "clarify", "unknown"]` in that order)}`; absent values `null`, `tags` `[]`; `json.dumps(…, ensure_ascii=False, separators=(",", ":"))`.
- `search-body.js`: `window.SPECS_BODY = {json};` plus a trailing newline; `{json}` maps each `id` to the plain text of its rendered body — the text of every inline token in document order, joined by single spaces, whitespace collapsed, mark brackets kept as text — same `json.dumps` options, keys in page order.
- Both written at the site root, byte-stable (value/0015). Not produced by `site-index`. `index.json` and `llms.txt` unchanged.

## C7 — search matching and UI — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** The base spec gives the shape (normalise, crude stem, weights, dropdown, `search.html?q=`); the brief adds the phone overlay and forbids Pagefind/lunr. What exactly?

**Answer:**

- One vanilla `search.js` (no dependencies, one IIFE, ≤ ~160 lines including UI), loaded `defer` on every page with the shell. The index loads lazily by inserting `<script src="{prefix}search-index.js">` on the first focus of the box or `/`; the body file on the first non-empty query after the index is in. `search.html` loads both at once. `<script src>`, never `fetch`, so `file://` works.
- Normalise: lowercase, `ё` → `е`, split on `/[^\p{L}\p{N}]+/u`, drop empties. Stem: a word longer than 7 drops its last 3 letters, longer than 5 its last 2, otherwise unchanged. A query term matches a field when the stem of the term is a prefix of a normalised word of that field. A record matches when every query term matches some field (AND across terms). Score = sum over terms of the best weight the term matched: `ref` 10 (the query term is a substring of the normalised ref), `title` 8, `tags` 4, `summary` 2, body 1. Order: score descending, then page order. Body matches count only once `search-body.js` has loaded. While the index is loading the list stays closed (`aria-expanded="false"`); a query typed meanwhile runs when the index arrives. When the body file arrives the current query re-runs; the active option is kept when its record is still listed, otherwise none is active.
- Header: `<form class="search" role="search" action="{prefix}search.html">` with `<input type="search" name="q" role="combobox" aria-autocomplete="list" aria-expanded aria-controls="search-list" placeholder="{search_placeholder}">`, a `<kbd>/</kbd>` hint, and `<ul id="search-list" role="listbox">`. Dropdown: up to 8 results, each `role="option"` with mono ref, title, status badge; a last option `{search_all} →` linking `search.html?q={q}`. Keys per WAI-ARIA APG combobox: Down/Up move `aria-activedescendant` (wrapping), Enter opens the active option or, with none active, submits to `search.html?q=`; Esc closes the list, a second Esc clears and blurs. `/` focuses the box unless focus is in an input, textarea, select or contenteditable, or a modifier key is held.
- Phone (< 760px): the box is hidden and a search `.iconbtn` (sprite icon `i-search`, label `search`) in the header opens it as a full-screen overlay — the same form gets class `open` on `<html>` (`search-open`), the input is focused; Esc or a close button closes it and returns focus to the search button. No second form.
- `search.html`: shell page, H1 `search`, the same form pre-filled from `?q=`, results as part 2's list rows (ref, title, summary, status badge) rendered by `search.js`, a `role="status"` count with the plural label `search_results`, `search_none` when empty. Without JS the page says `search_needs_js` with a link to `records.html`, and the header form still submits there.
- `site-index` pages carry no search box (they hold no records).
- Verified in the browser by the runner (Final Verification), as part 2 C9 did for `filter.js`; `just ci` stays Python-only and pytest owns the data files and markup.

## C8 — labels — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** Which UI strings are new?

**Answer:**

Under `core.specs.site.labels.{en,ru}.ui`, both languages: `section_link` (Link to this section / Ссылка на раздел), `link_copied` (Link copied / Ссылка скопирована), `by_section` (By section / По разделам), `via` (via / через), `complexity` (complexity / сложность), `reversibility` (reversibility / обратимость), `level_low` / `level_medium` / `level_high` (low, medium, high / низкая, средняя, высокая), `search` (Search / Поиск), `search_placeholder` (Search the specs / Поиск по спекам), `search_all` (All results / Все результаты), `search_results` (plural: `{n} result`, `{n} results` / `{n} результат`, `{n} результата`, `{n} результатов`), `search_none` (Nothing found / Ничего не найдено), `search_needs_js` (Search needs JavaScript. / Для поиска нужен JavaScript.). Reused, already shipped: `close`, `on_this_page`, `chosen`, `open_questions`, `referenced_by`, `nothing_references`. Key-by-key fallback to `en` as part 1 C4.

## C9 — snapshots and goldens — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** What output drift is expected?

**Answer:**

No playbook source is edited, so `just snapshots` is expected clean; booping:rule/0013 holds — any drift is reported, and only drift this plan describes may be accepted under the owner's standing permission for this feature (2026-10-14). The `booping-python/e2e/cases/specs/site-*.txtar` goldens are test fixtures rebaselined (`just e2e -k site --txtar-update`) by each milestone that changes output, the diff read against that milestone's stated markup.

## C10 — review gates — answered

**Asked:** 2026-10-16 — intake, present

**Question:** The intake scope gate and the present approval gate need the owner.

**Answer:**

Auto-confirmed by the run per the owner's autonomous-run instruction: scope as C1; plan approved whole at 22 SP (under the 35 SP split threshold, no split). Cross-review (Codex): the CRITICAL (no JS test in `just ci`) is deferred in `index.md`'s Risk register — it reverses C7 and part 2 C9 — with a worker-run headless check added to M06; the four RISKs folded in — scroll-spy rule (C3), `via` dedup order (C4), the exact ADR shape match (C5), search state while data loads (C7); NOTEs dismissed (the swarmlight fixture and Chromium exist on this machine; milestones run in id order).
