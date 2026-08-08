# Write the run's entry in the project's chronological history

You receive the attached repo's path, the confirmed change rows verbatim — each with its id, its
type (vision shift / new feature / refactoring / feature drop / chore) and its user-visible effect
stated in the project's own vocabulary — and the changelog surface's declared format from the
surfaces file.

The rows are the only authority. You read no diff, no file list, no plan body and no source: the
effects were compressed once, at `research`, and the user settled them at the change gate, so
re-deriving them here would re-litigate a closed table. The one file you open is the history itself.

## The file to write

`CHANGELOG.md` at the attached repo's root — the project's chronological history, seeded when the
repo carries none. Read it whole before writing: its heading grammar, how an entry is scoped
(release, date, or a standing unreleased section), the tense and voice of its bullets, how deep they
go and how they group are what this run's entry must match.

- one entry for this run. Its bullets join the file's current top section — the standing unreleased
  section when the format keeps one, otherwise a new dated section opened above the newest existing
  entry. A second run before a release folds into that same section rather than opening a rival one
  for the same version.
- one bullet per user-visible change, grouped the way the file already groups them (added / changed
  / removed, or whatever grammar is in force). **Past tense is correct here** — every other surface
  this run writes is a present-state snapshot, and the history is the one place where "it used to be
  like this" narration is required rather than stripped.
- depth is the surface's, not the change table's: an existing user checking what moved wants the
  effect in one line. No rationale, no file paths, no internal module names, no change ids.
- the filter is user-visibility, applied per row. A chore or a refactoring nobody outside the repo
  can observe earns no bullet and is reported as omitted, so every confirmed row is provably
  accounted for without padding the history with churn.
- the entry is derived from what the project **shipped**, not from what this run documented. A
  change whose destination documents were dropped still shipped and still earns its bullet, and the
  run's own documentation work never appears in the history at all.
- history is append-at-top and immutable. Earlier entries are never reworded, re-scoped or
  re-narrated; a factual error you spot in an old entry is a return line, never a silent fix.
- a seeded file carries a title, one lead line naming the format it obeys, and this run's section.
  Earlier releases are **not** reconstructed — you hold only what this run landed, and a backfill is
  a scope decision raised in the return rather than improvised.
- no frontmatter: a repo-root markdown surface carries none, and you add none.
- leave the file **uncommitted** in the working tree — repo-side documentation is committed by the
  user, never by the playbook.
- nothing else is written: not the run record, not the spec set, not another documentation surface,
  even where a bullet exposes a gap in one.

A run whose whole table is chores writes no file at all and says so — an empty `## Changed:` with an
`omitted:` line per row is the outcome, not a failure.

## Return format

```markdown
## Changed:
- [CREATED|UPDATED] CHANGELOG.md — {seeded|appended}, {n} bullets under {section}

## Notes:
- {group}: {the bullet in a phrase} ({change id})
- omitted: {change id} ({type}) — {why it is not user-visible}
- format: {matched the file's existing grammar | seeded from the changelog surface's declaration}

## Questions:
```

One `## Notes:` bullet line per bullet written, in the order they appear in the entry, then one
`omitted:` line per change that earned none, then the format line. A run that wrote nothing keeps
`## Changed:` empty and still carries its `omitted:` lines. `## Questions:` stays empty — the step
has no gate to ask into. The runner holds what the history now says from these lines alone and never
opens the file. No prose outside the block.
