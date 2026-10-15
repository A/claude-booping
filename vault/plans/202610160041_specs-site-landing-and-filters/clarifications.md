# Clarifications

Autonomous run — the owner was unavailable; every question below was settled by the run with a default. Design sources are part 1's copies: `plans/202610152329_specs-site-redesign/design/` (`brief.md`, `specs-site-design.md`, `specs-site-mockup.html`), precedence brief > mockup > base spec (part 1 C1).

## C1 — scope — answered

**Asked:** 2026-10-16 — intake

**Question:** Which part of the request does this plan take?

**Answer:**

Part 2 exactly as part 1 parked it (part 1 C2): the documentation landing with one "N need you →" link, review as a filter over a record list, list filter chips and sort with `location.hash` state, the Source (tier) facet, phone cards, the tag tree and tag pages from `tags.yaml`. Part 3 (ToC rail, `§` anchors, grouped backlinks, ADR option cards, search) stays parked; base-spec priority 3 (graph, hover previews) stays skipped. The machine layer from part 1 C9 is not changed: every review reason is derivable from `index.json`'s existing fields.

## C2 — pages and paths — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** Where do the new pages live, given part 1 kept root-scoped paths?

**Answer:**

Part 1's paths stay. New: `records.html` (all records of every root, the list the type facet filters), `review.html` (the review filter), `{root}/tags/index.html` (that root's tag tree) and `{root}/tags/{tag}.html` with every `:` in the tag replaced by `.`. Tags stay per root because each tier owns its own `tags.yaml` (`src/specs/README.md`, Tier schemas). No `.md` copies for any of these — `llms.txt` is the machine form of lists.

## C3 — filter facets, hash format, sort — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** booping:rule/0010 asks to lock the exact state format. The base spec's example `#status=open&unreviewed=1` gives each flag its own key; the mockup ANDs one flat chip set and keeps no hash. What are the facets, their semantics and the hash?

**Answer:**

- Facets, in this order: `type`, `source` (the root name), `status`, `flag`. `flag` values: `unreviewed`, `clarify`, `unknown` on every list; the review page adds `conflict` (an `open` conflict), `proposed` (a `proposed` ADR) and `open` (an `open` idea or open item).
- Semantics: OR within a facet, AND across facets (standard faceted search; the mockup's flat AND makes two status chips always empty). No chip active in a facet = that facet does not filter.
- Hash: `#{key}={v},{v}&{key}={v}` — keys in the facet order above, then `sort={value}` when the sort is not the page default; values in the page's chip order, each through `encodeURIComponent`. Written with `history.replaceState` on every change (no history entry per click); no active chip and default sort writes the bare path. Read on load and on `hashchange`. Unknown keys and values are ignored.
- Sort, one `<select>`: `number` (page order — default on every list but review), `updated` (`updated_at` newest first), `title` (`localeCompare` in the site `lang`); review adds `review` (its default: `created_by: claude` first, then oldest `updated_at`, then page order). Every sort breaks ties by page order; a record without `updated_at` sorts last under `updated` and `review`.
- Chips and counts are server-rendered: a chip's count is the number of rows on the page carrying that value, independent of other active chips (mockup). A chip with count 0 is not rendered; a facet with fewer than two chips is not rendered (`type` on a type page, `source` with one root) — except `flag`, rendered with one or more chips.
- Departs from the base spec's per-flag keys: one `flag` key keeps OR-within-facet uniform.

## C4 — review pool and reasons — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** What is on the review list, why, and where does each row link?

**Answer:**

- A record is on `review.html` when it has at least one reason: `unreviewed` (`booping.specs.records.unreviewed`), `clarify` / `unknown` (at least one such mark), `conflict`, `proposed`, `open` (C3). Page order = the record order of `records.html`; default sort `review`.
- Open items: items with `status: open` from `{vault}/{core.specs.open_items.dir}/OI-*.md`, read only when the site renders its default roots with a vault attached (never with `--root`). An item row: mono id, its title, flag `open`, no `source` value (a `source` chip hides it), linked to the record page when its `record:` resolves, otherwise unlinked.
- Each row shows why it is listed with the part-1 state badges (icon + text): the status badge, the clarify badge linking `{record page}#L{line}` of the record's first `[clarify]` mark, the unknown badge linking its first `[unknown]` mark, the unreviewed hollow dot. The anchor scheme is part 1's `L{line}` (markdown.py), not the mockup's hand-made `#q1`.
- No chip is active on entry; the page is already the "needs you" pool. Departs from the mockup, which pre-selects "unreviewed".
- "N need you" = the number of rows on `review.html` (records plus open items).

## C5 — home landing — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** What exactly is on the landing?

**Answer:**

Top to bottom (mockup `home()`, brief): H1 site title; `<p class="lead">` the summary of the first value record of the first root that has one — the same source as `llms.txt`'s blockquote — omitted when none; a `.callout` only when N > 0: the link `{N} need you →` (plural label) to `review.html`, then ` · {M} open questions` (plain text, M = `[clarify]` marks across all records, clause omitted when 0); the scenario grid — one card per type that has records, in site type order across all roots, name + count + scenario line, linking `records.html#type={type}`; H2 "Recently updated" with the 10 records of greatest `updated_at` (ties in page order, records without `updated_at` left out), each row ref + title link + localised date. The per-root type lists leave the home page; roots stay reachable from the sidebar's Sources group and their root pages.

## C6 — sidebar — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** Part 1's sidebar lists roots with their types. What does it hold once tiers become a facet?

**Answer:**

In order: Overview (home); Review with its count N; All records with its count; Types — every type with records, across roots, with count, linking `records.html#type={type}`; Tags — per root that has any tag, its top-level tags with descendant-inclusive counts linking their tag pages, plus a link to the root's tag tree, the root name as sub-heading only when more than one root has tags; Sources — each root linking its root page, with its record count; `llms.txt`. Base spec's sidebar, with the review count.

## C7 — tag tree — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** `tags.yaml` is flat (`tag: description`), may be absent, and records may use tags it lacks. What is the tree?

**Answer:**

Per root: nodes = the keys of `tags.load(root.path)` ∪ every tag the root's records carry ∪ each of those tags' ancestors (`a` for `a:b`). A node's children are the nodes one `:` segment deeper with it as prefix; order by tag id. A node's count is the number of the root's records carrying it or any descendant (port of shatterlings `tagged()`). Description from the dictionary, empty otherwise. A malformed `tags.yaml` (`MalformedDictionary`) is one site warning on that file and the tree is built from used tags. Tag ids render as written (no label translation). Tag page: crumbs Overview › root › Tags › each ancestor › tag; H1 the tag; the description as lead; the children as a list with counts; then the tagged records (descendants included) as a filterable list. Record pages' tags become links to their tag pages.

## C8 — no tag facet on lists — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** The base spec lists a tag chip facet on list pages; the brief does not.

**Answer:**

Not added. Tags are per tier and may run to dozens; tag pages carry the tag navigation. Departs from the base spec.

## C9 — JavaScript and its verification — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** Where does the filter code live, and how is it tested with no JS test runner in `just ci`?

**Answer:**

A new vanilla `filter.js` beside `site.js`, loaded only by pages carrying a filter bar. Without JS (`<html>` lacks class `js`) the filter bar is hidden and every row stays visible. `just ci` stays Python-only: pytest asserts the server-rendered data — each row's `data-*` attributes, chip sets and counts, sort keys. The behaviour (hash in → visible rows, chip click → hash out, sort) is checked by the runner in Final Verification with headless Chromium, as part 1 did its visual check.

## C10 — phone layout — answered

**Asked:** 2026-10-16 — draft-plan

**Question:** What are "phone cards"?

**Answer:**

Part 1's single 760px breakpoint. Below it a list row becomes a card (border, radius, padding; ref first, then title, badges, summary — mockup `@container` rules), the chips form one horizontally scrolling line, the sort `<select>` takes the full width, the scenario grid is one column. Tap targets ≥ 44px.
