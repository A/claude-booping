# Fold one destination document's assigned changes

You receive one row of the confirmed targeting plan, verbatim: the destination path, the roles it
addresses, the change ids assigned to it, and the **Must say** clause for each — already pitched at
the depth those roles allow. With it come the role entries that row names, each with its depth
ceiling, voice and withheld set, and the destination surface's row from the surfaces file: how the
file is built and published, how long its entries run, how it links and heads its sections. Read the
destination whole before writing — a change is folded into the wording already there, never appended
to the end.

Nothing the row settled is re-opened here. The destination is the row's, the audience fit is the
row's, the depth ceiling is the roles file's, and a fact is the change table's; the gate that
confirmed the plan is your authorisation to write. Anything you cannot write faithfully goes in the
return as `not written:` rather than being improvised into the file. Read no source to check a
claim — fact-checking against code is `verify`'s step, and this one writes what its row says.

**One file.** The loop runs one instance per row in parallel and rows never share a destination, so
instances stay safe exactly as long as you open nothing outside your own row's file.

## The file to write

`{your row's destination path}` — the repo-relative markdown file the row names, the single file you
may write.

- rewrite in place the section that owns each assigned change; extend a section the change only adds
  to; create a section solely when no existing one owns it
- keep the file's own structure — heading style, link form, entry length, ordering — so the fold
  reads as part of the file rather than as a patch
- what lands is a current-state snapshot: a changed behaviour replaces the sentence describing the
  old one, a dropped capability leaves the document instead of being annotated as removed, and no
  "this used to work differently" narration survives the fold. Removed legacy wording is reported in
  the return, never marked in the document.
- frontmatter the file already carries survives untouched, and you add none of your own
- `[CREATED]` only when the row names a page that does not exist yet under a documented directory —
  then the surface's conventions shape the new file's skeleton
- never a source file: the destination set is markdown by construction, and code-level docs stay
  with `develop`
- nothing else is written — not the run record, not the spec set, not another row's destination, not
  `CHANGELOG.md`

Judge the draft on being correct and complete at its depth, not on being tight. `compact` runs next
and is the pass that cuts: a fact stated twice is cheap, a fact missing is not — which is not a
licence to pad, only the reason never to trade coverage for brevity here.

## Return format

```markdown
## Changed:
- [CREATED|UPDATED] {destination path} — {change ids that landed}

## Notes:
- {change id} → {section}: {created|rewritten|extended}, {what it now says in a clause}
- dropped legacy: {outdated wording removed, or none}
- not written: {what the row asked for that could not be written faithfully, or none}

## Questions:
```

One `## Notes:` line per assigned change, in the row's order, then the two summary lines. The runner
holds what this destination now says from these lines alone and never opens the file. `## Questions:`
stays empty — the step has no gate to ask into, and a blocker is a `not written:` line. No prose
outside the block.
