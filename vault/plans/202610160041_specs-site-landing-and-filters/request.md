# Request

**Request**

> Request — redesign the specs site per the brief /tmp/claude-1000/-home-anton-Dev--A-hermes-pet/36dbf90d-0102-4f43-add1-4a69775c2e2f/scratchpad/site/brief.md and the base spec specs-site-design.md beside it (read both fully; the brief's owner corrections win). Code: booping-python/src/booping/specs/site and site-index. Priorities from the base spec: 1 hygiene + theme + machine layer, 2 home/review filter/list tables + filters/record page/tags/search, 3 skip graph and hover previews.

(Continuation run: groom the next part the previous plan of this request left parked. Run directives — autonomous, worktree, snapshot policy, speed — are in the session prompt and not repeated here.)

**Task type** — `feature`: the site gains capability it lacks after part 1 — a documentation landing with one "needs you" link, review as a filter over the record list, filter chips and sort with shareable `location.hash` state, a Source (tier) facet, phone cards and tag pages from `tags.yaml`. Not `bug`: part 1 shipped what its plan promised; plain lists were the agreed interim (part 1 C10), not a divergence. Not `refactoring`: the pages and what a reader can do on them change visibly.

**Problem** — After part 1 (`plans/202610152329_specs-site-redesign`, done) the site has the mockup's shell, theme, fonts, record page head and machine layer, but its home page is an H1 plus per-root type lists, type pages are plain row lists with no filter or sort, there is no way to see "what needs me" across the set, tags render as plain text with no pages, and the tier is the top of the hierarchy rather than a facet. The owner wants (brief): a documentation landing — framing line, types as reading scenarios, recently updated, and ONE «N need you →» link; review as a filter over the list with chips (unreviewed, has [clarify], has [unknown], open conflicts, proposed ADRs, open ideas/items), each row saying why it is listed by icon and linking to the mark's anchor; list chips and sort whose state lives in `location.hash`; tiers as a Source facet; phone cards; tag tree and tag pages from `tags.yaml`.

**Clarifications and Decisions** (autonomous run — each a default, logged in `clarifications.md`)

- Scope is part 2 exactly as part 1 parked it (part 1 C2); part 3 (ToC rail, `§` anchors, grouped backlinks, ADR option cards, search) stays parked; priority 3 (graph, hover previews) stays skipped.
- Design sources are part 1's copies under `plans/202610152329_specs-site-redesign/design/` — referenced, not copied again (value/0003); precedence brief > mockup > base spec (part 1 C1).
