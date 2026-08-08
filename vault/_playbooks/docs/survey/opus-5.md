# Survey the spec set and the undocumented work

You receive the workdir (`{vault}/docs/`), the attached repo, and — on a re-survey — the scope
answer that sent the run back here and the name of the run record already on disk. A run has
exactly one record: reuse that name, never open a second.

Two cheap sweeps, then the record. Read no work item's body and no source file: this step settles
what is worth reading, it does not do the reading.

## Sweep 1 — the spec set

Four files under `_specs/`, each judged **by shape alone** — `present`, `incomplete`, `missing`:

- `_specs/index.md` — the briefing: what the project is, who it serves, where it is heading
- `_specs/roles.md` — one section per audience, each with its depth, tone and withheld set
- `_specs/targets.md` — one entry per markdown surface, with format, audience and depth
- `_specs/features.md` — features, their capabilities, their groups

`incomplete` means the file exists but is missing sections its own heading structure requires, or
carries a section with no content under it. Never judge a file by whether its content looks dated
— content drift is the change table's business, in `research`. These three words are also what the
run's exit edges read, so use no others.

## Sweep 2 — the undocumented work

The project's delivered work items are the plans — `{vault}/plans/*/index.md` — whose status is the
plan track's terminal one. From each, take only its path, its status, the date it landed (the
completion stamp in its frontmatter) and a one-line headline. Nothing more: what the item actually
changed is `research`'s job, in its own sub-agents.

The undocumented set is those items minus the rows of the ledger `_specs/documented.md`. Membership
is by absence from the ledger, never by date, so a long-postponed item developed late surfaces in
the run after it lands rather than never.

## The file to write

`{vault}/docs/_runs/{YYYYMMDDHHmm}-{title}.md` — `{YYYYMMDDHHmm}` is the clock at open, `{title}` a kebab
headline for the undocumented set as a whole (`nothing-to-document` when it is empty).

- frontmatter: `title:` — the same headline in sentence case — and nothing else. `status:` is
  `playbook-transition`'s, `started:` and `commit:` the surveying edge's hooks', every later stamp
  its own edge's. Write none of them.
- H1 repeating the title.
- `## Spec set` — a `File | State | Gap` table, one row per spec file in the order above, `—` in
  Gap when the state is `present`, otherwise the precise absence. Closed by one prose line: `{n} of
  4 usable`, which files need the spec waves, and which are complete.
- `## Undocumented work` — a `Work item | Status | Landed | Headline` table, one row per item.
  Closed by one prose line: the count, the date range, and how many rows the ledger holds with its
  most recent one. An empty set keeps the heading and replaces the table with a single line
  (`nothing has landed since the ledger's last row`).
- `## Scope` — the heading plus exactly one placeholder line, verbatim:
  `_Not yet confirmed — the runner writes the settled scope here at the scope gate._`
  Never fill it — you have no confirmed answer to write. On a re-survey, leave whatever this
  section already holds untouched.

Nothing else is written. `_specs/` is read-only here, the ledger is appended by the
`close-documented` hook at `record`, and no work item's own file is touched. A re-survey rewrites
the two tables of the same record in place.

The record and the return must be decisive enough for the runner to see which route out of the
scope gate the user's answer can take: some spec file needs work, the spec set is current and the
spec waves are skipped, or there is nothing to do at all.

You never stop for the user: write the record, return, and the scope gate is the runner's.

## Return format

```markdown
## Changed:
- [CREATED|UPDATED] {vault}/docs/_runs/{YYYYMMDDHHmm}-{title}.md

## Notes:
- spec set: {n} of 4 usable — {one clause per file: name, state, the gap when not present}
- undocumented: {n} items outside the ledger, {earliest} → {latest}
- route: {spec waves needed | spec set current, straight to research | nothing to do}

## Questions:
```

`## Questions:` is always empty — the scope question is the runner's gate, and you never ask for a
decision you would only hand back. No prose outside the block.
