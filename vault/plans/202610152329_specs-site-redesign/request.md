# Request

**Request**

> Request — redesign the specs site per the brief /tmp/claude-1000/-home-anton-Dev--A-hermes-pet/36dbf90d-0102-4f43-add1-4a69775c2e2f/scratchpad/site/brief.md and the base spec specs-site-design.md beside it (read both fully; the brief's owner corrections win). Code: booping-python/src/booping/specs/site and site-index. Priorities from the base spec: 1 hygiene + theme + machine layer, 2 home/review filter/list tables + filters/record page/tags/search, 3 skip graph and hover previews.

(Run directives — autonomous, worktree, snapshot policy, speed — are in the session prompt and not repeated here.)

**Task type** — `feature`: the site gains user-facing capability it lacks today — a navigation shell, a theme toggle, shipped fonts, a review filter, list filters, tag pages, client search and a machine layer (`llms.txt`, `index.json`, `.md` copies). Not `bug`: `booping specs site` renders what its docs promise; the brief asks for a different product, not a divergence from a stated one. Not `refactoring`: the rendered output and the reading experience change visibly, so the no-behaviour-change test fails.

**Problem** — Today `booping specs site` renders a tier × type count matrix at the root, type pages that concatenate full record bodies, raw frontmatter keys, bare relation codes, no `lang`, no navigation, search, theme toggle, mobile patterns or machine layer (base spec, audit items 1–12). The owner reads it as documentation and finds it badly thought out for its scenarios. After the redesign the site is a reading-first documentation site in the approved mockup's look: shipped Golos Text / JetBrains Mono fonts, a header with search and a theme toggle, a sidebar with the types as reading scenarios, a home landing with one "needs you" link, review as a filter over the list, state icons on every record, record pages with relations, backlinks, ToC and ADR option cards, tag pages from `tags.yaml`, a vanilla Cyrillic-aware search, a phone layout, and `llms.txt` / `index.json` / `.md` copies for agents; `booping specs site-index` follows the same design.

**Clarifications and Decisions** (autonomous run — each a default, logged in `clarifications.md`)

- Source precedence: brief's owner corrections > approved mockup (`specs-site-mockup.html`) > base spec.
- Fonts are vendored into the repo once (woff2 + OFL) and copied into every site output; nothing fetched at render or view time.
- Priority 3 (relation graph, hover previews) is out of scope.
- Split decision deferred to draft-plan, made on the estimate against the 35 SP threshold.
