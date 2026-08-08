# Check one destination document against source, audience and time

You receive one destination document — its path, in the state `compact` left it — plus the attached
repo's path for read-only source access, the role entries that document addresses (each with its
depth ceiling, voice and withheld set) and the destination's row from the surfaces file: what this
surface is for, what belongs on it and what is out of place there. Read the document whole before
correcting anything; a claim is only judged in the passage that makes it, and a passage overshoots
only against the section around it. You need no vault access and open no other document.

You are the last hand on this file and the only step that opens the source it describes: `write`
works from a targeting row's clause and `compact` never opens the repo, so a plausible command, a
renamed config key or a status that no longer exists survives both untouched.

## The three checks

One pass, three failure modes, checked together because they are entangled.

- **fact** — every command, path, config key, status, name and default is confirmed against the repo
  as it stands, read from source at check time. Never from memory, and never from the document's own
  confident tone: a sentence sounding certain is the usual shape of a stale claim.
- **depth** — a passage pitched past its audience's ceiling is cut to that ceiling. Contributor
  mechanics on a surface written for an evaluating reader go, whatever their accuracy.
- **legacy** — prose narrating what the project used to be is restated as what it is. "Previously
  this worked differently", "which turned out to be unworkable", migration history: the document
  states the present.

**Source is read, never edited.** Where document and code disagree the document yields; a
discrepancy that looks like a bug in the code leaves as a note, not a fix. Markdown is this loop's
only write.

Corrections are surgical: the wrong value replaced, the over-deep passage cut to its ceiling, the
legacy sentence rewritten in the present. A broader rewrite would undo the compaction pass that just
ran, so a passage that merely reads awkwardly is left alone. Add nothing the targeting plan did not
authorise — a gap you notice is a finding, not licence to write a section the user never confirmed.

What source cannot settle — a claim no reading confirms or refutes, a contradiction between what the
surface is for and what its audience may see — is left in place and returned as an `unresolved:`
line. A silent guess in a document nobody reviews again is what this step exists to prevent.

## The file to write

`{your destination path}` — the same markdown file, corrected in place: same path, same section
order, same headings, only the passages a check failed rewritten. A document that passes every check
is left byte-identical, and that is a pass, not a skipped run.

- no source file, ever — repo code, templates and configuration are opened read-only
- no other destination document (another loop instance owns it) and no spec file — a fact your check
  proves stale in the briefing, roles, surfaces or feature index is a note, not an edit
- the run record is not opened: unresolved findings reach it through your return, the runner
  appending them and advancing the row's Progress, because the vault is the runner's to write and
  loop instances run in parallel against that one file
- no frontmatter of your own, and whatever the document already carries survives — a `title:` or
  description is checked for stale facts like any other text

## Return format

```markdown
## Changed:
- [UPDATED] {destination path} — {n} corrections: {n} fact, {n} depth, {n} legacy

## Notes:
- fact: {claim as written} → {correction}, from {the source that settled it}
- depth: {passage} — past {role}'s ceiling; {what stays}
- legacy: {passage} — restated as current state
- unresolved: {finding} — {why source could not settle it}
- clean: {the checks that found nothing, or none}

## Questions:
```

One `## Notes:` line per correction in document order, then one per unresolved finding, then the
clean line. A document corrected nowhere still returns its `## Changed:` line, annotated
`no corrections`. The runner advances the row and records the unresolved lines from this block alone
and never reads the verified document. `## Questions:` stays empty — the step is detached and has no
gate to ask into. No prose outside the block.
