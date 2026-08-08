# Compact one destination document

You receive one destination path as `write` just left it, the roles that document addresses — each
with its voice, depth ceiling and withheld set — and, verbatim, the Must-say clauses the targeting
row assigned to it. The runner resolved all three from the confirmed targeting plan; you open no run
record and no spec file. Read the destination whole before touching it — a section you have not read
whole cannot be judged.

`write` optimised for saying everything its row assigned. This step optimises for saying it in the
fewest words that still carry it, and keeping the two apart is what stops either being done badly.

## The method

Split the document by section, then work one section at a time:

1. **radical** — cut to the bone: every hedge, every restatement, every "it is worth noting", every
   sentence that announces what the next sentence says, every second-person aside
2. **gentle** — touch only what is indefensible
3. **merge** — take the variant that lost no fact, preferring the radical. Where the radical dropped
   a particular the gentle kept, keep the radical's wording and restore that particular from the
   gentle. Never blend the two into a third voice.

Per section, not per document. Asked to compact everything at once a model summarises, and summary
is not compaction — it drops particulars evenly instead of dropping filler, and regresses every
section to the same middling compression however bloated it was. Section by section, a section
already tight survives the merge unchanged and a section that is 60% padding loses the 60%.

**Compaction removes words, never facts.** The clauses you were handed are the floor: every one of
them is still stated after the merge, in whatever wording survives. A clause that reads like padding
is padding the plan asked for, and it stays. This is a named floor, not a judgement call — you hold
the clauses, so you can check.

Tone and depth are the roles' — a cut that drops below an audience's depth ceiling, or exposes what
that role is withheld, is a mutilation rather than a compaction.

## The file to write

`{the row's destination path}` — the same markdown file, rewritten in place: same path, same section
order, same headings, same code and tables, fewer words.

- a section the merge left alone is not rewritten
- verbatim structures pass through byte-identical: code fences, tables, frontmatter, link targets,
  command lines. They are not prose.
- nothing is added — no transition sentences, no "as described above", and above all no legacy
  narration; prose explaining what the project used to be is what `verify` fails a document for
- frontmatter the file already carries survives untouched, including a `title:` or description whose
  prose looks compactable, and you add none of your own
- a document that arrives already tight leaves byte-identical — a successful run, not a skipped one
- nothing else is opened: no other destination (another instance owns it), no spec file, no run
  record. The runner moves your row's Progress from your return alone.

A section you cannot compact without losing something is a `held verbatim` line in the return, never
a stop.

## Return format

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
`already tight, no change`. The runner advances the row and hands `verify` the same path from these
lines alone; it never reads the compacted document. `## Questions:` stays empty — the step is
detached and has no gate to ask into. No prose outside the block.
