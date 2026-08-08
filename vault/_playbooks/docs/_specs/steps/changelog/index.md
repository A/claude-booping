---
status: awaiting-spec-confirm
---

[← index](../../index.md)

# changelog

## Contract

- **Needs** —
  - what this run landed and what each item does for a user — every confirmed change with its id,
    its type (vision shift / new feature / refactoring / feature drop / chore) and its effect
    stated in the project's own vocabulary, as the user left it after the change gate; the effect
    clause is the raw material of a bullet, so nothing beyond it — no diff, no file list, no plan
    body — is needed or wanted
  - the chronological history's existing format and latest entries — its heading grammar, how an
    entry is scoped (release, date, or a standing unreleased section), the tense and voice its
    bullets use, how deep they go and how they group; and, when the project has no history file
    yet, the format its surface declaration names for it, so a seeded file starts in the grammar
    the surface set already promised rather than one invented here
- **Value** — the project's memory, and the single exception to the playbook's own anti-legacy
  rule. Every other surface this run writes is a snapshot of the present with "it used to be like
  this" narration stripped out; the history is where that narration is not merely allowed but
  required, and **past tense is correct here and nowhere else**. Keeping it in its own step, after
  the loop rather than inside it, is what makes the rule stateable: no targeting row ever names the
  history file, so no `write` instance ever has to decide whether the surface it holds is the
  exception. The entry is derived from **what the project shipped, not from what this run
  documented** — a change whose destination documents were dropped still shipped and still earns a
  bullet, and the run's documentation work never appears in the history at all. The filter is
  user-visibility, applied per row: a chore and a refactoring nobody outside the repo can observe
  get no bullet and are reported as omitted, so every confirmed change is provably accounted for
  without padding the history with churn. Depth is the surface's, not the change table's — an
  existing user checking what moved wants the effect in one line, never the rationale, the file
  paths or the internal names the row happens to carry. History is **append-at-top and immutable**:
  this run's bullets join the current section, earlier entries are never reworded, re-scoped or
  re-narrated, and a factual error found in an old entry is reported rather than silently fixed.
  A run whose whole table is chores writes nothing and says so — the exit edge fires on the return,
  not on a file having changed.
- **Output files** —
  - `[CREATED|UPDATED] CHANGELOG.md` at the **attached repo's root** — the project's chronological
    history, seeded when the repo carries none
    - one entry for this run: its bullets join the file's current top section — the standing
      unreleased section when the format keeps one, otherwise a new dated section opened above the
      newest existing entry. A second run before a release folds into the same section rather than
      opening a rival one for the same version
    - bullets grouped the way the file already groups them (added / changed / removed, or whatever
      grammar is in force), one bullet per user-visible change, past tense, no rationale, no file
      paths, no internal module names, no change ids
    - a seeded file carries a title, one lead line naming the format it obeys, and this run's
      section — earlier releases are **not** reconstructed: the step is given what this run landed
      and has no reading of what came before, and a backfill is its own scope decision, raised in
      the return rather than improvised
    - no frontmatter: a repo-root markdown surface carries none, and one is never added
    - the file is left **uncommitted** in the working tree — `commit-docs` stages the vault alone,
      and the repo-side documentation this playbook writes is committed by the user, never by the
      playbook
  - nothing else — the run record is `record`'s to close, the spec set is not opened, and no other
    documentation surface is touched even where a bullet exposes a gap in one
- **Harness return** — the standard block. `## Changed:` names the history file alone, annotated
  with whether it was seeded or appended, the bullet count and the section they landed under; a run
  with no user-visible change returns it empty. `## Notes:` carries one line per bullet written —
  its group, the bullet in a phrase, and the change id behind it — then an `omitted:` line per
  change that earned no bullet with the reason it is not user-visible, and a line naming the format
  it followed. The runner holds what the history now says from those lines and never opens the
  file; `record` composes its landed row from the same `## Changed:` line.
- **Review gate** —
  - none — the bullets are already the effects the user confirmed at the change gate, and
    re-asking would re-litigate a settled table in the history's voice
  - `writing-changelog → recording` fires on the return alone, including an empty one; a wording
    the user wants different is a direct edit to a repo file they own, or a re-run of this step
- **Delegation** — detached: `detached: "opus:medium"` (the decomposition's `opus-5:medium`; `opus`
  is the tier the `detached:` grammar accepts). The history file is read whole to match its grammar
  and rewritten with a section on top, which is reading the runner must not carry. The agent's
  bootstrap needs the confirmed change rows verbatim, the changelog surface's declared format, and
  the attached repo path; it needs no code access — the user-visible effects were compressed once,
  at `research`, and are not re-derived here.

## Example artifact

`CHANGELOG.md` at the repo root, seeded on the first run — the repo carried none, and the change
table held three new features, one refactoring and one chore:

````markdown
# Changelog

Notable user-visible changes, newest first. Bullets are grouped Added / Changed / Removed; cutting
a release renames the `Unreleased` heading to the version.

## Unreleased

### Added

- Retrospectives became their own artifact with their own status track: a plan reaches `done` and
  stays there, and the retro queue is read from plan frontmatter.
- Code review moved onto its own frontmatter field, so review and retro no longer compete for one
  status.
- `booping query` reads vault frontmatter — any config mapping can act as a query spec.

### Changed

- A lesson is now addressed with a `targets:` list — playbook, step, agent or skill. Lessons that
  target nothing are injected nowhere.
````

On a later run the file already exists: the four `### Added` / `### Changed` groups under
`## Unreleased` gain this run's bullets in place, nothing above or below that section is opened,
and the lead line is left exactly as the file carries it. A run whose confirmed table is entirely
chores writes no file at all and returns an empty `## Changed:` with one `omitted:` line per row.

## Return Format

````markdown
## Changed:
- [CREATED|UPDATED] CHANGELOG.md — {seeded|appended}, {n} bullets under {section}

## Notes:
- {group}: {the bullet in a phrase} ({change id})
- omitted: {change id} ({type}) — {why it is not user-visible}
- format: {matched the file's existing grammar | seeded from the changelog surface's declaration}

## Questions:
````

One `## Notes:` bullet line per bullet written, in the order they appear in the entry, then one
`omitted:` line per change that earned none, then the format line. A run that wrote nothing keeps
`## Changed:` empty and still carries its `omitted:` lines.
