# Enumerate the documentation surfaces

You receive the confirmed briefing — what the project is, who it serves, where it is heading —
the attached repo's path, and the run workdir `{vault}/docs/`. Describe the project's own parts
in the briefing's vocabulary.

Read the repo yourself: every markdown documentation surface it carries today, and the
conventions each one follows — where it lives, how it is built and published, how long its
entries run, how it links, what it habitually omits. Read `{vault}/docs/_specs/targets.md`
first when it exists: a run refreshes that file, it never regenerates it.

Audience is described from the surface itself — who reaches for this file and why — never by
role id. The role vocabulary is being authored in parallel; surfaces and roles meet later, at
targeting.

## The file to write

`{vault}/docs/_specs/targets.md`:

- no frontmatter of your own — the confirming edge stamps `reviewed_at:`, and an existing
  file's frontmatter survives untouched
- an H1 naming the project and the file: `# {project} — Documentation surfaces`
- a lead of one or two lines naming the rule the set obeys: markdown surfaces only, one row per
  destination file or per documented directory
- one table, columns `Surface | Format & conventions | Audience | Depth`
  - **Surface** — the backticked path or root
  - **Format & conventions** — how it is built, published and written: generator, link style,
    entry length, heading habits
  - **Audience** — who reaches for it and why, in plain description
  - **Depth** — how much detail belongs there, and what is out of place on it
- a `CHANGELOG.md` row always, marked as introduced by this playbook; when the repo carries no
  `CHANGELOG.md` yet, say so in the row, so the changelog step knows it seeds rather than appends
- a closing `## Not surfaces` section naming what was considered and excluded, each with its
  reason — source files, module headers and inline comments (owned by `develop`), build
  artefacts, generated reports, non-markdown assets — so no later wave re-litigates the boundary
- on a refresh: keep the rows that still hold in their existing hand-made wording, and rewrite
  only what the repo moved. A surface that no longer exists leaves the file and is named in your
  return — never dropped silently.

The set is closed by construction: markdown only, so a source file can never become a
destination. Write no other file — you enumerate surfaces, never edit one, and never touch the
sibling `_specs/` files being written in the same wave, whatever your reading suggests about them.

## Return format

```
## Changed:

- [UPDATED] {vault}/docs/_specs/targets.md — 5 surfaces, 1 new

## Notes:

- `README.md` — evaluating engineer; what it is, install, one example
- `documentation/` — MkDocs site for users and playbook authors; the deep reference
- `docs/` — plugin-internal fragments read by agents mid-run; route-specific detail only
- `CHANGELOG.md` — new surface, repo has none yet: the changelog step seeds rather than appends
- `CLAUDE.md` — session-loaded project guide for agents; the map, not the data
- added since the previous file: `CHANGELOG.md`
- dropped: `documentation/roadmap.md` — no longer in the repo
```

`[CREATED]` on a first run, annotated with the surface count and how many are new. One
`## Notes:` line per surface — path, then its audience and depth in a few words — then a line
naming what was added and what was dropped since the previous file, and a line stating whether
the repo already has a `CHANGELOG.md`. The runner presents the surfaces at the gate from these
lines alone and never opens the file.
