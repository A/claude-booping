---
status: awaiting-spec-confirm
---

[← index](../../index.md)

# compact

## Contract

- **Needs** —
  - the destination document as `write` just left it — its path and its full current text,
    because the pass rewrites wording in place and cannot judge a section it has not read whole
  - the audiences that document addresses and the tone and depth each one needs — the voice, the
    depth ceiling, and what that audience is not to be shown, which is what tells a cut from a
    mutilation
  - the clauses the document was required to state — one per change assigned to it, in the wording
    the user confirmed; they are the floor no compaction may cut below
- **Value** — the run's defence against AI slop, and the reason the writing step is allowed to
  write loosely. `write` optimises for saying everything its row assigned; this step optimises for
  saying it in the fewest words that still carry it, and separating the two is what keeps either
  from being done badly. The mechanism is deliberate: **split by section, compact each section
  twice at opposite intensities, then merge**. A radical pass cuts to the bone — every hedge,
  every restatement, every "it is worth noting", every sentence that announces what the next
  sentence says. A gentle pass touches only what is indefensible. Running both and choosing per
  section is what avoids the single-pass failure mode, where one "make this tighter" instruction
  regresses every section to the same middling compression regardless of how bloated it was: a
  section already tight survives the merge unchanged, a section that is 60% padding loses the 60%.
  Per-section rather than whole-document for the same reason a whole-document pass fails — asked
  to compact everything at once a model summarises, and summary is not compaction; it drops
  particulars evenly instead of dropping filler. The floor is absolute: **compaction removes
  words, never facts** — and it is a named floor, not a judgement call, because the instance holds
  the clauses its row required. Every one of them is still stated after the merge, in whatever
  wording survives; a clause that reads like padding is padding the plan asked for, and it stays.
  Nothing is added — no transition sentences, no "as described above", and
  above all no legacy narration, since the verify step's third failure mode is prose that explains
  what the project used to be. Verbatim structures — code fences, tables, frontmatter, link
  targets, command lines — are not prose and pass through byte-identical; a document that arrives
  already tight leaves byte-identical, and that is a successful run, not a skipped one.
- **Output files** —
  - `[UPDATED] {the row's destination document}` — the same markdown file `write` produced,
    rewritten in place: same path, same section order, same headings, same code and tables, fewer
    words. A section the merge left alone is not rewritten
  - nothing else — no other destination is opened (another loop instance owns it), no spec file is
    read or written, and the run record is untouched: the targeting row's Progress column moves to
    `compacted` by the runner, from this step's return, because the vault is the runner's to write
  - no frontmatter is added to the document, and whatever frontmatter it already carries survives
    untouched — including a `title:` or description whose prose looks compactable
- **Harness return** — `## Changed:` names the one destination, annotated with the size before and
  after. `## Notes:` carries one line per section — the heading, which variant the merge took, and
  what class of text went — then a line for the sections left byte-identical, a line naming what
  was held verbatim, and a line confirming every required clause still stands. The runner advances that row's Progress and hands `verify` the same path from
  these lines alone; it never reads the compacted document. `## Questions:` is always empty — the
  step is detached and has no gate to ask into.
- **Review gate** —
  - none — the targeting plan authorised this document's content at `awaiting-targeting-confirm`,
    and compaction changes wording only, so there is nothing new to approve
  - the loop runs straight on to `verify`, which is where a compaction that cost a fact is caught;
    a section this step could not compact without losing something belongs in `## Notes:` as a
    held line, never as a stop
- **Delegation** — detached: `detached: "opus:high"` (the decomposition's `opus-5:high`; `opus` is
  the tier the `detached:` grammar accepts). Three passes over a full document is precisely the
  text the driving context must never hold, and the judgement of what a cut costs is the reason
  the effort is high rather than the loop's cheapest. The instance is briefed with one destination
  path, its audiences' tone and depth needs, and its row's required clauses — the runner resolves
  all three from the confirmed targeting plan, so the agent never reads the run record; it needs no
  repo access beyond that file and no vault access at all.

## Example artifact

The artifact is the destination document rewritten in place. Taking one section of
`documentation/playbook.md` as `write` left it:

````markdown
## Lessons

It is worth noting that lessons are one of the more powerful mechanisms available to playbook
authors. A lesson is essentially a markdown file that lives in either the global lessons directory
or the vault's own lessons directory, and it carries a `targets:` list in its frontmatter. This
list is what determines where the lesson will ultimately be injected. The targeting system
supports four different forms of target, which are `{playbook}`, `{playbook}/{step}`,
`agent:{id}` and `skill:{name}`. As you might expect, a lesson that does not declare any targets
at all will not be injected anywhere, which is an important thing to keep in mind when authoring
lessons for the first time.
````

The radical variant of that section — every hedge, every announcement and every second-person
aside removed:

````markdown
## Lessons

A lesson is a markdown file in `{home_dir}/_lessons/` or `{vault}/_lessons/` carrying a `targets:`
list. Targets take four forms — `{playbook}`, `{playbook}/{step}`, `agent:{id}`, `skill:{name}`.
An untargeted lesson injects nowhere.
````

The gentle variant, which cut the padding but kept the framing sentence:

````markdown
## Lessons

Lessons are a playbook author's project-local shaping mechanism. A lesson is a markdown file in the
global or vault lessons directory, carrying a `targets:` list that decides where it is injected.
The four target forms are `{playbook}`, `{playbook}/{step}`, `agent:{id}` and `skill:{name}`; a
lesson declaring no targets is injected nowhere.
````

The merge takes the radical variant — it lost no fact, and the gentle variant's framing sentence
restates what the section heading already says. Where the radical pass had dropped one of the four
target forms, the merge would keep its wording and restore the missing form from the gentle
variant, never blend the two into a third voice.

The row that produced this section required *"lessons are addressed by a `targets:` list — schema
and the four target forms"*; the merged section still states both, which is what the return's
`clauses:` line reports. Had the radical variant kept only the schema, it would have been repaired
from the gentle variant before the merge was accepted.

A section that is a table, a code fence or a command list passes into the merged document
byte-identical, and its `## Notes:` line reads `held verbatim`.

## Return Format

```markdown
## Changed:
- [UPDATED] {destination path} — compacted, {n} → {m} words across {k} sections

## Notes:
- {section heading} — {radical|gentle|radical + repair}: {what class of text went}
- unchanged: {sections the merge left byte-identical}
- held verbatim: {code fences, tables, frontmatter, link targets — or none}
- clauses: {n} of {n} required clauses still stated

## Questions:
```

One `## Notes:` line per compacted section in document order, then the three summary lines. A
document that came back byte-identical still returns its `## Changed:` line, annotated
`already tight, no change`.
