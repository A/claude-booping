---
status: awaiting-spec-confirm
---

[← index](../../index.md)

# sync-specs

## Contract

- **Needs** —
  - the confirmed change table — one typed row per delivered item (vision shift, new feature,
    refactoring, feature drop, chore), each carrying the effect on the spec set the user settled,
    with every extension and refinement made at the gate already folded in
  - the four spec statements as they currently stand — the project briefing, the roles, the
    documentation surfaces and the feature index — read in full, because a fold rewrites their
    wording in place rather than appending to it
- **Value** — the moment the spec set stops describing the repo as it was and starts describing it
  as it is. Everything after this step — the targeting plan, every document written, every
  verification — resolves "what does this project ship, for whom, at what depth" against these four
  files, so folding the confirmed table in here once is what keeps a dozen later reads consistent
  instead of each one re-deriving the delta from the table. Its discipline is narrow by
  construction: the table is the only authority, no source is read (research already did that
  reading, and re-reading would re-litigate a settled decision behind the user's back), and nothing
  the table does not say gets written — a fold that "notices" something else reports it in the
  return and leaves the file alone. What lands is a current-state snapshot: a dropped feature leaves
  the index rather than being annotated as removed, a shifted vision replaces the old sentence
  rather than sitting beside it, and the drift itself is reported to the runner, never narrated in
  the file. Every spec file exists by the time this step runs — both routes into `researching`
  guarantee it — so this is always a fold, never an authoring pass.
- **Output files** — the four spec files, each rewritten in place only when a row targets it; a file
  no row touches is left byte-identical and is not listed in the return
  - `[UPDATED] {vault}/docs/_specs/index.md` — the briefing; takes vision-shift rows: what the
    project is, who it serves, where it is heading
  - `[UPDATED] {vault}/docs/_specs/roles.md` — the roles; takes rows that move who reads this
    project or what an audience may be shown — a new audience, a depth ceiling that moved, a
    withheld set that changed
  - `[UPDATED] {vault}/docs/_specs/targets.md` — the surfaces; takes rows that add, drop or
    re-scope a markdown destination, or change a surface's format, audience or depth
  - `[UPDATED] {vault}/docs/_specs/features.md` — the feature index; takes new-feature, feature-drop
    and refactoring rows as capability additions, removals, rewordings and regroupings
  - each file keeps the shape its own step's contract defines — the fold edits rows and sentences
    inside that shape, never restructures it
  - no frontmatter of the step's own, and whatever frontmatter a file carries survives untouched
  - nothing else is written: not the run record, not the ledger, not a single repo file — chore
    rows and rows the table marks as having no spec effect are simply carried forward untouched for
    `targeting` to route
- **Harness return** — `## Changed:` one line per file actually rewritten, each annotated with what
  moved in a few words; a run where the table's rows all resolve to no spec effect returns an empty
  `## Changed:`. `## Notes:` carries one line per change-table row — the row, the file it landed in,
  and the edit in a phrase — then a `no spec effect:` line naming the rows that touched nothing, and
  a `not written:` line for anything the fold noticed but the table did not authorise. The runner
  holds the post-change spec set from these lines alone and never re-reads the four files.
- **Review gate** —
  - none — the change table was confirmed at `awaiting-changes-confirm`, and that confirmation is
    this step's authorisation; the runner does not stop after the return
  - `syncing-specs → targeting` fires on the return alone, so a fold that could not be made
    faithfully belongs in `## Notes:` as a `not written:` line rather than in a stop the state
    machine has no edge for
- **Delegation** — detached: `detached: "opus:medium"` (the decomposition's `opus-5:medium`; `opus`
  is the tier the `detached:` grammar accepts). The four files are read whole and rewritten whole,
  which is exactly the reading the runner must not carry. The agent's bootstrap needs the confirmed
  change table verbatim and the `{vault}/docs/` workdir; it needs no repo access at all.

## Example artifact

The artifact is the touched subset of the four files, rewritten in place. Folding a confirmed table
whose rows are a vision shift (playbooks became the only extension unit), a new feature (lessons
addressed by `targets:`), a feature drop (per-surface lesson files) and a chore (CI ordering):

`_specs/index.md` — the "Where it is heading" paragraph replaced, the rest of the briefing untouched:

```markdown
## Where it is heading

Playbooks are the only extension unit: a new procedure ships as a playbook, never as a skill, and
project-specific shaping stays in vault lessons rather than forked bodies. The skill surface is
closed at one — `/playbook` — and everything procedural is authored against the manifest schema.
```

`_specs/features.md` — one capability added under an existing group, one dropped, one reworded:

```markdown
## Learning

| Capability | What it does |
| --- | --- |
| Targeted lessons | A lesson file's `targets:` list addresses playbooks, steps, agents and skills; an untargeted lesson injects nowhere |
| Lesson injection | Rendered into playbook steps, agent bodies and skill bodies at render time |
| Retro → learn track | A retrospective becomes lessons and project-guide edits, the only two destinations learn writes |
```

`_specs/targets.md` — the `CLAUDE.md` row's Depth re-scoped by the same vision-shift row:

```markdown
| `CLAUDE.md` | repo root, loaded into every session; schema-over-prose | any agent starting work in this repo | the map — layout, commands, conventions; playbook authoring is the docs site's, not this file's |
```

`_specs/roles.md` — no row touched the audiences, so the file is not opened and does not appear in
`## Changed:`. The chore row lands nowhere and is reported as `no spec effect:`.

## Return Format

```markdown
## Changed:
- [UPDATED] {vault}/docs/_specs/{file}.md — {what moved, in a few words}

## Notes:
- {row} ({type}) → {file}: {the edit in a phrase}
- no spec effect: {rows that touched nothing}
- not written: {what the fold noticed that the table does not authorise, or none}

## Questions:
```

One `## Notes:` row line per change-table row, in table order, then the two summary lines. A file
that no row targeted is absent from `## Changed:` entirely — never listed with a "no change" note.
