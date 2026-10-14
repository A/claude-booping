# Enumerate the documentation surfaces

You receive the attached repo's path and the run record
`{vault}/docs/_runs/{YYYYMMDDHHmm}-{title}.md`; its `## Briefing` — what the project is, who it
serves, where it is heading — is confirmed. Describe the project's own parts in the briefing's
vocabulary.

Read the surfaces record `{vault}/specs/reference/0003-documentation-surfaces.md` first: a run
refreshes it, it never regenerates it. Then read the repo yourself: every markdown documentation
surface it carries today, and the conventions each one follows — where it lives, how it is built
and published, how long its entries run, how it links, what it habitually omits.

Audience is described from the surface itself — who reaches for this file and why — never by
role id. The audience record reference/0001 is being refreshed in parallel and is not a source
here; surfaces and roles meet later, at targeting.

## The record to refresh

The surfaces record's `## Facts` section, rewritten in place. Nothing else is written.

- One fact per bullet, in the bullet style the record uses today: one bullet per destination file
  or documented directory, opening with the backticked path, then who reaches for it and why, its
  depth ceiling — how much detail belongs there and what belongs elsewhere — and its conventions:
  generator, link style, entry length, heading habits.
- A `CHANGELOG.md` bullet always, marked as introduced by this playbook; when the repo carries no
  `CHANGELOG.md` yet, say so in the bullet, so the changelog step knows it seeds rather than
  appends.
- A spec-set bullet always: the project specs tier records the docs playbook reads — the value
  records, reference/0001–0003 (audience, glossary, surfaces) and the story records. Its audience
  is **Claude itself**, which reads them to learn the product's values, audiences, vocabulary,
  surfaces and features before writing any other destination, so a stale record mis-aims
  everything downstream. Its ceiling is the project's model of itself — never how-to prose, run
  history or implementation detail. Its convention is one typed record per subject, in the shape
  `booping specs check` enforces. Describe it like any other surface; you still never edit
  another record from here.
- A closing "Not surfaces" bullet naming what was considered and excluded, each with its reason —
  source files, module headers and inline comments (owned by `develop`), build artefacts,
  generated reports, non-markdown assets — so no later wave re-litigates the boundary.
- On a refresh: keep the bullets that still hold in their existing wording, and rewrite only what
  the repo moved. A surface that no longer exists leaves the record and is named in your return —
  never dropped silently.
- A default you chose that the repo and the briefing do not settle is marked `[clarify]` with one
  sentence on what to settle (rule/0002).
- Frontmatter stays untouched except `updated_at`, set to today. `reviewed` is the owner's alone —
  never add or change it.
- The H2 order the record shape enforces stays as it is: `## Facts`, then `## How to check?` when
  present.

The set is closed by construction: markdown only, so a source file can never become a
destination. Write nothing else — you enumerate surfaces, never edit one, and never touch
reference/0001, whatever your reading suggests about it.

## Return format

```
## Changed:

- [UPDATED] the surfaces record — 5 surfaces, 1 new

## Notes:

- `README.md` — evaluating engineer; what it is, install, one example
- `documentation/` — MkDocs site for users and playbook authors; the deep reference
- `docs/` — plugin-internal fragments read by agents mid-run; route-specific detail only
- `CHANGELOG.md` — new surface, repo has none yet: the changelog step seeds rather than appends
- `CLAUDE.md` — session-loaded project guide for agents; the map, not the data
- added since the previous facts: `CHANGELOG.md`
- dropped: `documentation/roadmap.md` — no longer in the repo
```

The `## Changed:` line is annotated with the surface count and how many are new. One `## Notes:`
line per surface — path, then its audience and depth in a few words — then a line naming what was
added and what was dropped since the previous facts, and a line stating whether the repo already
has a `CHANGELOG.md`. The runner presents the surfaces at the gate from these lines alone and
never opens the record.
