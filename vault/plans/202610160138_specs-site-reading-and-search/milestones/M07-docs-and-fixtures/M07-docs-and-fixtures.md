---
id: "07"
title: "Docs and the Russian fixture"
sp: 2
status: done
plan: "plans/202610160138_specs-site-reading-and-search/index.md"
---

# M07: Docs and the Russian fixture

The user docs describe the reading features and the search, and the Russian fixture exercises them.

**Scope**: `documentation/specs.md` (`### booping specs site`: extend the record-page bullet of **Pages** with the rail, `§` anchors, grouped backlinks and ADR option cards; add `search.html` to the page list; a new **Search.** paragraph beside **Filters.** — box, `/`, dropdown keys, phone overlay, `search.html?q=`, how matching works, `search-index.js` / `search-body.js` and their lazy loading, `file://`); `booping-python/e2e/cases/specs/site-renders-russian-labels-and-a-tier-own-type.txtar` (add a Russian ADR with an Alternatives table and two options, a Russian record that cites another from a named `##`, and assertions on the Russian `chosen`, `by_section`, `on_this_page` and search labels). Audience filter (booping:rule/0008): only what a reader of the site or the person publishing it touches — no module names, no internal churn.

Tests: the extended txtar case is the test (e2e tier).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | Docs for record reading and search. | `documentation/specs.md` | 1 | done |
| 7.2 | Russian fixture extension and its golden. | `booping-python/e2e/cases/specs/site-renders-russian-labels-and-a-tier-own-type.txtar` | 1 | done |

## Definition of Done

### Task 7.1

- [x] Every C2–C7 behaviour a reader sees is documented once in `documentation/specs.md`; nothing internal; `just docs` builds.

### Task 7.2

- [x] The Russian case renders the ADR cards, grouped backlinks with a `via` section, the rail and the search box with Russian labels, and passes.

Return: the list of changed and created files, nothing else.

## References

- `documentation/specs.md` — the existing **Filters.** and **Review.** paragraphs for voice and depth.
- `booping-python/e2e/cases/specs/site-renders-russian-labels-and-a-tier-own-type.txtar` — the case to extend.

## Verify

`cd booping-python && uv run pytest e2e -k site-renders-russian -q`
