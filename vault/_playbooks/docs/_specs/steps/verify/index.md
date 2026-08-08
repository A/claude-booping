---
status: awaiting-spec-confirm
---

[← index](../../index.md)

# verify

## Contract

- **Needs** —
  - the destination document as it now stands — its path and its full text, read whole, because a
    claim is only judged in the passage that makes it and a depth breach is only visible against
    the section around it
  - the code and behaviour the document describes — the commands, paths, config keys, statuses,
    names and defaults the repo actually carries, read from source at check time rather than from
    memory or from the document's own confident tone
  - the audiences this document addresses and the tone and depth each one needs — the voice, the
    depth ceiling, and what that audience is not to be shown
  - the surface's purpose and conventions — what this destination is for, what belongs on it and
    what is out of place there
- **Value** — the last hand on the document, and the only step in the loop that opens the source it
  describes. Three failure modes, checked in one pass because they are entangled: a claim that the
  repo does not support, a passage pitched past its audience's ceiling, and legacy narration —
  prose that explains what the project used to be instead of stating what it is. Fact-checking is
  the reason the step exists at all: `write` works from a targeting row's clause and `compact`
  never opens the repo, so a plausible-sounding command, a renamed config key or a status that no
  longer exists survives both untouched, and a documentation surface asserting something false is
  worse than one saying nothing. **Source is read, never edited** — where document and code
  disagree the document yields, and a suspected bug in the code is reported to the runner, not
  fixed here; markdown is this loop's only write. Corrections are surgical: the wrong value is
  replaced, the over-deep passage cut to its ceiling, the legacy sentence rewritten in the present
  — a broader rewrite would undo the compaction pass that just ran, so a document whose wording
  merely reads awkwardly is left alone. Nothing is added that the targeting plan did not authorise:
  a gap this step notices is a finding, not licence to write a new section the user never
  confirmed. What cannot be settled from source — a claim no reading confirms or refutes, a
  contradiction between what the surface is for and what its audience may see — is left in place
  and surfaced as an unresolved finding, because a silent guess in a document nobody reviews again
  is exactly what this step is here to prevent.
- **Output files** —
  - `[UPDATED] {the row's destination document}` — the same markdown file, corrected in place: same
    path, same section order, same headings, only the passages a check failed rewritten. A document
    that passes every check is left byte-identical, and that is a pass, not a skipped run
  - no source file, ever — repo code, templates and configuration are opened read-only, and a
    discrepancy that looks like a code bug leaves the step as a note
  - no other destination document (another loop instance owns it) and no spec file — a fact the
    check proves stale in the briefing, roles, surfaces or feature index is a note, not an edit
  - the run record is not opened here: unresolved findings reach it through the return, the runner
    appending them and moving the targeting row's Progress to `verified`, because the vault is the
    runner's to write and loop instances run in parallel against that single file
  - no frontmatter is added to the document, and whatever frontmatter it already carries survives
    untouched — a `title:` or description is checked for stale facts like any other text
- **Harness return** — `## Changed:` names the one destination, annotated with the correction count
  split by class. `## Notes:` carries one line per correction — its class (`fact`, `depth`,
  `legacy`), the passage, and what replaced it, a fact line naming the source that settled it —
  then one `unresolved:` line per finding the step could not settle, and a closing line naming the
  checks that found nothing. The runner records the unresolved lines on the run record and advances
  the row from these lines alone; it never reads the verified document. `## Questions:` is always
  empty — the step is detached and has no gate to ask into.
- **Review gate** —
  - none — this document's content was authorised at `awaiting-targeting-confirm` and verification
    only removes what fails, so there is nothing new to approve
  - the row leaves the loop on the return; the loop's own exit gate is the `updating →
    writing-changelog` transition (`each row's progress column reads verified, or dropped with its
    reason`), which the runner satisfies from these returns
  - a finding serious enough that the document should arguably not ship belongs in `## Notes:` as an
    `unresolved:` line — the run has no edge that stops here, and the runner is the one who raises
    it with the user
- **Delegation** — detached: `detached: "opus:high"` (the decomposition's `opus-5:high`; `opus` is
  the tier the `detached:` grammar accepts). Checking a document claim by claim against the repo is
  the run's second-heaviest read after `research`, and it is exactly the reading the driving context
  must never hold; the effort is high because deciding whether a passage overshoots its audience,
  and whether a sentence narrates history or states the present, is judgement rather than lookup.
  The instance is briefed with one destination path, the attached repo path for read-only source
  access, its audiences' tone and depth needs and the surface's purpose; it needs no vault access at
  all.

## Example artifact

The artifact is the destination document corrected in place. Taking a section of `README.md` as the
compaction pass left it:

````markdown
## Statuses

A plan moves through `groomed`, `ready-for-dev`, `in-progress` and finally `retro`, where the
retrospective is written before it can close. Previously each plan carried its retrospective inline,
which turned out to be unworkable once reviews were added, so the retro was split out into its own
document — a change that also required reworking how the develop playbook resolves its milestone
loop, since the loop had been reading the retro section's checkboxes to decide what was left.

Run `bin/booping playbook-state --plan {path}` to see where a plan stands.
````

The same section after verification — one stale fact corrected against `playbooks/develop/playbook.yaml`
and `src/config.yaml`, one legacy paragraph rewritten as current state, one implementation passage
cut to the reader's ceiling:

````markdown
## Statuses

A plan moves through `grooming`, `ready-for-dev`, `in-progress` and `done`. Retrospectives are their
own track: a retrospective is a standalone document, and the retro queue is read off plan
frontmatter rather than a plan status.

Run `bin/booping playbook-state --target {path}` to see where a plan stands.
````

Three corrections, one per class: `fact` — the status list named `retro`, which no machine declares,
and the command's flag was `--plan` where the CLI takes `--target`; `legacy` — the "previously each
plan carried its retrospective inline" paragraph replaced by a present-tense statement; `depth` — the
develop loop's milestone-resolution mechanics removed, being contributor detail on a surface written
for an evaluating engineer.

The unresolved findings the runner then records on the run record:

```markdown
## Verification findings

- `README.md` — the install block pins the plugin to a marketplace name that no file in the repo
  states; no source settles which name is correct, so the line is left as written.
```

A document that passes every check returns its `## Changed:` line annotated `no corrections` and
contributes no findings line at all.

## Return Format

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
clean line. A document corrected nowhere still returns its `## Changed:` line.
