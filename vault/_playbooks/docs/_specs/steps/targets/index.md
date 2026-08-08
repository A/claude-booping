---
status: awaiting-spec-confirm
---

[← index](../../index.md)

# targets

## Contract

- **Needs** —
  - the project's shape and direction as the briefing states it — what it is, who it serves,
    where it is heading; the vocabulary the briefing uses for the project's own parts is the
    vocabulary the surfaces are described in
  - the markdown documentation surfaces the repo carries today and the conventions each one
    follows — where it lives, how it is built and published, how long its entries run, how it
    links, what it habitually omits
  - the previous surfaces file when one exists — its rows and the hand-made wording in them,
    which a re-enumeration refreshes rather than regenerates
- **Value** — the closed set of markdown destinations the rest of the run works against. Later
  waves choose destinations from these rows instead of inventing them, and a writer opens a file
  already knowing its format, its reader and how deep to go — so two instances writing different
  surfaces in the same run cannot drift on tone or depth, and nobody re-derives the repo's
  conventions per file. The set is closed by construction: markdown only, so a source file can
  never become a destination; and it carries the changelog whether or not the repo has one yet,
  which is how a surface this playbook introduces gets planned for before it exists. Audience is
  described from the surface itself — who reaches for this file and why — never by role id: the
  role vocabulary is authored in the same wave, and surfaces and roles meet later, at targeting.
- **Output files** —
  - `[CREATED|UPDATED] {vault}/docs/_specs/targets.md` — the surface enumeration
    - no frontmatter of the step's own: the confirming edge stamps `reviewed_at:`, and an
      existing file's frontmatter survives untouched
    - a lead of one or two lines naming the rule the set obeys — markdown surfaces only, one row
      per destination file or per documented directory
    - one table row per surface: its path or root, **Format & conventions** (how it is built,
      published and written — generator, link style, entry length, heading habits), **Audience**
      (who reaches for it, in plain description), **Depth** (how much detail belongs there, and
      what is out of place on it)
    - a changelog row always, marked as introduced by this playbook, and flagged when the repo
      carries no `CHANGELOG.md` yet so the changelog step knows it seeds rather than appends
    - a closing `## Not surfaces` section naming what was considered and excluded with its reason
      — source files, module headers and inline comments (owned by `develop`), build artefacts,
      generated reports, non-markdown assets — so no later wave re-litigates the boundary
    - a refresh keeps rows that still hold, in their existing wording, and rewrites only what the
      repo moved; a surface that no longer exists leaves the file and is named in the return
      rather than deleted silently
  - no other file — the step enumerates surfaces and never edits one, and never writes the
    spec-set files its wave-mates own even when the reading suggests something about them
- **Harness return** — `## Changed:` with the single `targets.md` entry, annotated with the
  surface count and how many are new. `## Notes:` carries one line per surface — path, then its
  audience and depth in a few words — plus a line naming what was added and what was dropped
  since the previous file, and a line stating whether the repo already has a `CHANGELOG.md`. The
  runner presents surfaces at the gate from these lines alone and never reads the file to do it.
- **Review gate** —
  - the step itself stops at nothing: it returns and the wave continues while roles and
    feature-index are still writing
  - the gate is the runner's, once roles, targets and feature-index have each written their file
    — surfaces are presented **together with roles** and confirmed or refined as a pair
  - a refine answer sends the run back to spec-building and this step runs again over the same
    inputs plus the user's correction; the confirming edge stamps `reviewed_at:` on
    `_specs/targets.md`, which is never this step's write
- **Delegation** — detached: `detached: "fable-5:medium"` — a generic sub-agent fetches this
  step's body itself (`booping render-playbook docs --step targets`) and performs it; the runner
  never reads the repo's documentation surfaces, only the returned lines. The agent needs repo
  reads plus the one write into the vault's `docs/_specs/`; its bootstrap carries the attached
  repo path, the `{vault}/docs/` workdir and the confirmed briefing.

## Example artifact

`{vault}/docs/_specs/targets.md`, on a first run against this repo:

```markdown
# claude-booping — Documentation surfaces

Markdown only, one row per destination file or documented directory. Nothing outside this table
is written by a documentation run.

| Surface | Format & conventions | Audience | Depth |
| --- | --- | --- | --- |
| `README.md` | one GitHub-rendered page; badges, install block, a single worked example; the Statuses section is hand-maintained narrative | an engineer deciding whether to install the plugin | what it is, why, how to install, one example — mechanics link out to the docs site |
| `documentation/` | MkDocs source, one page per subject, published to gh-pages on push to `master`; reference tables over prose | a user setting booping up or authoring playbooks against it | the deepest surface — full mechanics, every config key, every frontmatter field |
| `docs/` | plugin-internal fragments lazy-loaded by skills via `${CLAUDE_PLUGIN_ROOT}/docs/{name}.md`; no build step, no preamble | the agent itself, mid-run, already inside a task | only the route-specific detail the caller lacks; no motivation, no restated context |
| `CHANGELOG.md` | **new — introduced by this playbook**; the repo has none yet, so the first run seeds it. Reverse-chronological, one entry per release, past tense | an existing user checking what moved | one line per user-visible change; no rationale, no file paths, no internal refactors |
| `CLAUDE.md` | repo root, loaded into every session; schema-over-prose, structured data referenced not restated | any agent starting work in this repo | the map — layout, commands, conventions, principles; never a copy of what `src/config.yaml` already holds |

## Not surfaces

- `src/`, `booping-python/` — source, docstrings and inline comments; code-level documentation
  stays with `develop`
- `skills/`, `agents/` — build artefacts rendered from `src/files/`; reachable only through their
  templates
- `playbooks/*/_reports/output.md` — generated snapshots, written by `just snapshots-accept`
- `mkdocs.yml`, `.claude-plugin/` — configuration, not documentation
```

## Return Format

```markdown
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
