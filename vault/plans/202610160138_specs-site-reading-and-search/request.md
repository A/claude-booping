# Request

**Request**

> Request — redesign the specs site per the brief /tmp/claude-1000/-home-anton-Dev--A-hermes-pet/36dbf90d-0102-4f43-add1-4a69775c2e2f/scratchpad/site/brief.md and the base spec specs-site-design.md beside it (read both fully; the brief's owner corrections win). Code: booping-python/src/booping/specs/site and site-index. Priorities from the base spec: 1 hygiene + theme + machine layer, 2 home/review filter/list tables + filters/record page/tags/search, 3 skip graph and hover previews.

(Continuation run: groom the next part the previous plans of this request left parked. Run directives — autonomous, worktree, snapshot policy, speed — are in the session prompt and not repeated here.)

**Task type** — `feature`: the record page and the site gain reading and finding capability they lack after parts 1 and 2 — an "On this page" rail, `§` heading anchors, backlinks grouped by type and by section, ADR option cards, and a client-side search. Not `bug`: parts 1 and 2 shipped what their plans promised; part 3 was parked by design (part 1 C2, part 2 C1), not a divergence. Not `refactoring`: what a reader sees and can do on a record page and in the header changes visibly.

**Problem** — After parts 1 and 2 (`plans/202610152329_specs-site-redesign`, `plans/202610160041_specs-site-landing-and-filters`, both done) the site has the shell, theme, landing, review filter, filterable lists and tag pages, but a record page is still one long column: no "On this page" navigation, no way to link a heading, backlinks as one flat list that does not say which section of the citing record points here, ADR alternatives as a plain table followed by paragraphs with the chosen option not distinguished, and no search at all — the base spec's "find by text" task (owner lookup) has no surface. The owner wants (brief, base spec): a sticky ToC rail that collapses with the record's open questions into `<details>` under the title on the phone; rustdoc-style `§` anchors; backlinks by type and by section; ADR options as cards, chosen first and open, others collapsed, one card per option on the phone; and the base spec's own Cyrillic-aware vanilla search loaded via `<script src>` so `file://` works — header box focused with `/`, a full-screen overlay on the phone, `search.html?q=` for the full list — never Pagefind or lunr.

**Clarifications and Decisions** (autonomous run — each a default, logged in `clarifications.md`)

- Scope is part 3 exactly as parts 1 and 2 parked it; base-spec priority 3 (relation graph, hover previews) stays skipped; git history / source links from a repo URL stay out. This is the last part — the request ends with it.
- Design sources are part 1's copies under `plans/202610152329_specs-site-redesign/design/` — referenced, not copied again (value/0003); precedence brief > mockup > base spec (part 1 C1).
- The intake scope gate is auto-confirmed per the owner's autonomous-run instruction.
