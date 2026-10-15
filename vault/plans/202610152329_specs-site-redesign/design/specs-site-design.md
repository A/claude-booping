# booping specs site — redesign spec

Requested by the owner on 2026-10-15 after looking at the swarmlight site: "read design/UX guides and make a normal, convenient site for this task". Research: NN/g (information scent, navigation, search, scanning, breadcrumbs, ToC), the GOV.UK Design System (tags, tables, layout), Diátaxis, rustdoc, MDN, Obsidian Publish, log4brains, llmstxt.org, WCAG 1.4.3. The old shatterlings generator (`shatterlings/crates/specs/src/site.rs` at tag `poc-final`) already has several of these pieces. Port them rather than reinvent.

## Users and tasks

1. **Owner review.** "What needs me": records without `reviewed`, `[clarify]` / `[unknown]` marks, open conflicts, `proposed` ADRs, `open` ideas, open items.
2. **Owner lookup.** "How does X work and why": find by topic (tag), by type, or by text. Follow relations: ADR → values, rules, mechanics, and what supersedes it.
3. **LLM agents.** A machine layer: `llms.txt`, `index.json`, `.md` copies.

Content: 50–500 records, 3 tiers (project, global, core), any language (swarmlight writes Russian text under English structure).

## Audit of the current site (what to fix)

1. The root is a tier × type count matrix. It doesn't answer "what needs me", and `[clarify]` texts are hidden one level down.
2. There is no global navigation: no sidebar, no search, no footer, no skip link.
3. Type pages concatenate full record bodies (`adr/index.html` is 83 KB for 12 ADRs and won't scale). Bodies render twice, the outline breaks (record h2 sits next to body h2s), and there is no sort or filter.
4. Tags are dumped raw in a `dl`. `tags.yaml` is not read, so there is no tag tree and no tag pages.
5. Relation links are bare `<code>value/0003</code>`: no title, no status. Per NN/g information scent, a link needs a title, summary and status.
6. `<html lang>` is not set, which breaks hyphenation, spellcheck and screen readers for non-English text.
7. Metadata shows raw keys (`created_by`, `updated_at`) in frontmatter order.
8. Backlinks are a flat list. Supersession is not computed both ways.
9. ADR alternatives render as a plain table plus paragraphs. The accepted option is not distinguished.
10. Lines are ~80+ chars wide. Dark mode follows the system only, with no toggle.
11. There is no machine layer: no `llms.txt`, no JSON index, no `.md` copies.
12. There are no mobile patterns: tables scroll sideways and there is no ToC.

## Constraints

- Static output. No network at render or view time. Deterministic, byte-stable output for the same input.
- Python + Jinja as today. No JS framework and no build step. Small vanilla JS is fine for search, filters and theme. Everything must degrade: without JS, all content and full lists stay visible.
- Must work from `file://`. Load the search index with `<script src>` (`window.SPECS_INDEX = …`), not `fetch()` of JSON.
- UI labels come from a small label table keyed by English ids. The locale comes from config (e.g. `core.specs.site.lang: ru`). `<html lang>` takes the same value. Record structure stays English, as the format guide requires.
- System font stack, no web fonts. Text column ≤ ~68ch at 17px. Contrast ≥ 4.5:1 in both themes.
- Status is always a text label, never colour alone (GOV.UK Tag). Badges are not links.

## Page skeleton (every page)

- **Header.** Site name, a search input (always visible, focus with `/`), a theme toggle (auto / light / dark).
- **Left sidebar.**
  - Overview, Review (with count), Types (with counts), Tags (tree), All records, `llms.txt`.
  - Tiers appear as a "Source" facet (chips), not as the top of the hierarchy: people search by topic, not by tier.
  - On mobile the sidebar collapses behind a burger (the CSS checkbox hack from the old generator).
- **Breadcrumbs.** `Overview › tier › type › record` (hierarchy, not history). On narrow screens show only the last level.
- **Skip link** to main content. **Footer** with build date and generator.

## Pages

### Overview (root `index.html`): "Needs you"

- **Cards with counts, each linking to a pre-filtered list:** unreviewed, open `[clarify]`, `[unknown]`, open conflicts, `proposed` ADRs, `open` ideas, open items (when the vault has them).
- **Below the cards:** the first 5 `[clarify]` texts inline, each with record title and anchor, plus a link "all marks →".
- **"Recently updated":** the last 10 by `updated_at`.
- **Compact overview:** a type grid with counts and the top-level tags with descriptions.

### Review (`review.html`)

- **"Unreviewed":** records without `reviewed`. Rows show ref, title, summary, `created_by`, `updated_at`. Sort: `created_by: claude` first, then oldest first.
- **"Marks":** every `[clarify]` / `[unknown]` text, grouped by tag area. Each links to the record line (`#L{n}`, as in the old `review_page`).
- **"Open items":** id, title, source, direction, record link (read from `open-items/` when the vault has it).

### Lists (type page, tag page, "All records")

- **Table, never full bodies.**
  - Columns: ref, title + summary (two lines), status badge, tier, tags, updated, flags (unreviewed, clarify count, unknown count).
  - Each row carries `data-*` attributes: type, status, tier, tags, updated, flags.
- **Filters:** chips for status, tier, tag, "unreviewed", "has clarify". **Sort:** number, updated, title.
- **Filter state lives in `location.hash`** (`#status=open&unreviewed=1`), so a filtered view is a link. The overview cards link to these hashes.
- **Below 640px** the rows become cards.

### Record page

- **Head:**
  - H1 title;
  - a row of text badges: type, status, tier, "unreviewed", clarify / unknown counts;
  - the summary as a lead paragraph.
- **Facts panel**, with labels from the label table:
  - author (`created_by`), created, updated, reviewed;
  - tags (links to tag pages);
  - sources;
  - "source `.md`" link and git history link when a repo URL is configured.
- **Relations block.** Each link shows title and status badge:
  - Serves values (`values`);
  - Rules (`rules`);
  - Supersedes (`supersedes`);
  - Superseded by (computed);
  - Mechanics and other typed refs of tier-own types.
- **"Referenced by" (backlinks):** grouped by type, plus a "by section" sublist (which `##` of the citing record links here). Port `backlinks()`.
- **Right rail:**
  - sticky "On this page" ToC (`##` / `###`);
  - "Open questions" listing this record's marks.
  - On narrow screens both collapse into `<details>` under the summary.
- **Anchors:** every heading gets a `§` anchor that copies its link (rustdoc style).
- **ADR alternatives:**
  - The options table stays as the summary, with the accepted row marked by a badge.
  - Each `###` option renders as `<details>`: the accepted one open with a "chosen" badge, rejected and proposed ones collapsed.
  - Pros, Cons, Complexity and Reversibility keep their text labels.
  - `###` anchors must survive, because the table links to them.

### Tags

- **Read the tier's `tags.yaml`.**
  - `tags/index.html`: the tree, where `a` contains `a:*`. Each node shows its description and record count.
  - `tags/{a.b}.html`: description, child tags, then the list table of records tagged with it or any descendant.
- **Port** `tag_tree` / `tag_page` / `tagged` from the old generator.

### Search

- **Index.**
  - `search-index.js`: `{ref, tier, type, title, summary, status, tags, url, flags}` per record.
  - `search-body.js`: plain-text bodies, loaded on first query.
- **Matching.**
  - Normalise: lowercase, `ё→е`, split into words.
  - Prefix match on a crude stem (drop the last 2–3 letters for words longer than 5).
  - Weights: title > tags > summary > body.
  - ~80 lines of own code. lunr and similar English stemmers don't fit Cyrillic.
- **UI.**
  - Dropdown under the header input: ref, title, badge; arrow keys and Enter.
  - `search.html?q=` for the full result list.

### Machine layer

- **`llms.txt`** per llmstxt.org: H1, a blockquote, then an H2 per type with `- [ref title](url.md): summary (status; tags)`.
- **`index.json`:** all metadata and resolved relations, including backlinks and superseded-by.
- **`.md` copies** beside every HTML page, with `<link rel="alternate" type="text/markdown">`.
- **`404.html`** with `<base href>`, from the old `not_found`.

### Theme

- **Three states:** auto, light, dark.
  - Applied as `data-theme` on `<html>`, stored in localStorage.
  - An inline `<head>` script prevents the flash of the wrong theme.
  - `color-scheme: light dark`.
- **Badge colours** pass 4.5:1 in both themes.

## Data the pages need

- **Frontmatter:** `type`, `title`, `summary`, `status`, `kind`, `created_by`, `created_at`, `updated_at`, `reviewed`, `tags`, `values`, `rules`, `supersedes`, `sources`, plus ref-list keys of tier-own types (e.g. `mechanics`).
- **Body:**
  - headings for the ToC and the "by section" backlinks;
  - relative links between records, for backlinks;
  - `[clarify]` / `[unknown]` marks with line numbers;
  - ADR alternatives: table rows and `###` blocks with the status cell.
- **Tier `tags.yaml`:** descriptions and the tree.
- **Vault `open-items/`:** for the overview and the review page, when present.
- **Config:** site language and an optional repo URL for "source" and "history" links.

## Priorities

1. **Small, do first.**
   - Hygiene: `lang`, ~68ch column, 17px, `color-scheme`, skip link, header and sidebar, fact labels.
   - Theme toggle.
   - `llms.txt` + `index.json` + `.md` copies.
2. **Medium, the core of the owner's ask.**
   - Overview "Needs you" + `review.html`.
   - List tables with filters and hash state instead of concatenated bodies.
   - Tags from `tags.yaml`.
   - Record page: relations with titles, backlinks, ToC, ADR alternatives.
   - Client search.
3. **Later or skip.** Relation graph and hover previews: at 500 records, backlinks and the relations block give more for less.

## References the owner can compare against

- rustdoc (any `docs.rs` crate page): sidebar, `/` search, `§` anchors, theme toggle.
- MDN reference pages: breadcrumbs, sidebar tree, "In this article" rail, status badges, last-modified line, "View on GitHub".
- Obsidian Publish sites: backlinks under each page.
