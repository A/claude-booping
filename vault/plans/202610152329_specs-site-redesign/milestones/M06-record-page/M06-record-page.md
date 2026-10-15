---
id: "06"
title: "Record page — state badges, labelled facts, titled relations, marks"
sp: 3
status: pending
plan: "plans/202610152329_specs-site-redesign/index.md"
---

# M06: Record page — state badges, labelled facts, titled relations, marks

A record page opens like the mockup's record: title, a row of state badges, tags, the summary as a lead, a labelled facts panel in a fixed order with localised dates, relations shown by title and status instead of bare codes, and marks in the body drawn as icon-labelled callouts.

**Scope**: `booping-python/src/booping/specs/site/templates/record.html.j2`, `_macros.html.j2` (`record_block` rewritten for the page only — the type page stops embedding bodies in M07), `pages.py` (`_block`, `_fact_items`), `markdown.py` (mark markup). Head, in order: H1 title; `<div class="badges">` = `state_badges(state)` (M03) with the clarify badge an `<a href="#{first_mark}">` wrapper — the one badge that is a link, because it jumps to the question — and the unreviewed badge; tags as `<span class="tag">#{tag}</span>` (tag pages come in part 2, so no link); `<p class="lead">` summary. Facts `<dl class="facts">` in this order, each row only when it has a value, labels from `labels.fact`: `created_by` (`labels.author`), `created_at`, `updated_at` (`labels.date`, `<time datetime>`), `reviewed` (date, or `ui not_reviewed`), `sources` (relative paths as text, `://` entries as links). Relations `<section class="relations">` after facts: one `<dl>` row per `Site.relations` key (label `labels.fact(key)`, falling back to the key) plus `superseded_by` (`ui superseded_by`), each item `<a href>` with the target's title, its mono ref and its status badge (`state_badges` with only `status`), cross-root items prefixed by root name; unresolved refs stay mono text with the existing `unresolved` class and warning. Raw keys outside these lists (e.g. `targets`, `brief`, `kind`) render after the relations in frontmatter order with the raw key as label — nothing is dropped. Body: `markdown.py` wraps a `[clarify]` mark as `<mark class="mk mk-clarify" id="L{n}">` + `icon("i-clarify")` + the literal `[clarify]` text, `[unknown]` likewise with `i-unknown` — the literal tag stays visible so the record reads the same as its source; ids unchanged. Backlinks keep today's flat "Referenced by" list (grouping comes in part 3) but each item shows title, mono ref and status badge. The page passes `rail` empty (`.norail`).

Tests (integration): `site_pages_test.py` — a record with `created_by: claude`, `updated_at: 2026-10-15`, no `reviewed`, `values: [value/0001]`, `tags: [robot]`, one `[clarify]`, in ru: facts in the order Автор, Изменено, Ревью with «агент», «15 октября 2026», `not_reviewed`; the relations row links value/0001 by its title; the clarify badge links to the mark's `L{n}` and that id exists in the body; a superseded ADR shows the superseder under `superseded_by`; `targets` still renders. Rebaseline `site-*.txtar` goldens and read the diff: only record pages change.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | Record head, facts order and labels, relations block with titles and status, raw-key rows, backlink items. | `booping-python/src/booping/specs/site/templates/record.html.j2`, `booping-python/src/booping/specs/site/templates/_macros.html.j2`, `booping-python/src/booping/specs/site/pages.py` | 2 | pending |
| 6.2 | Mark callout markup with icons; the tests; golden rebaseline. | `booping-python/src/booping/specs/site/markdown.py`, `booping-python/tests/specs/site_pages_test.py`, `booping-python/tests/specs/site_test.py`, `booping-python/e2e/cases/specs/site-*.txtar` | 1 | pending |

## Definition of Done

### Task 6.1

- [ ] No record page shows a raw `created_by`/`updated_at` key or a bare relation code without its title.
- [ ] Every frontmatter key of the record is still visible somewhere on its page.

### Task 6.2

- [ ] Mark anchors `L{n}` are unchanged, so existing links into marks keep working.
- [ ] The new tests pass; rebaselined goldens differ only on record pages.

Return: the list of changed and created files, nothing else.

## References

- `../../design/specs-site-mockup.html` — `record()` markup: badges, tags, lead, facts, `.mark`.
- `booping-python/src/booping/specs/site/pages.py` — `_block` and `_fact_items`, the code being reshaped.

## Verify

`cd booping-python && uv run pytest tests/specs e2e -k site -q`
