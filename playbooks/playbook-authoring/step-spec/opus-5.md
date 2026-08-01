# Write one step's spec

The input names the target step and carries the confirmed decomposition plus the original
procedure description. Produce the step's **working spec**: the full contract and a concrete
example of its artifact, in a file the user refines and confirms directly — the example
replaces chat back-and-forth, and it later becomes the source the step's smoke tier pins.

## The file to write

`<name>/_specs/steps/<step>/index.md`:

- frontmatter: write none of your own — the file may already exist with harness-owned keys
  (`status:`, stamps); preserve them untouched
- the single H1, right after the backlink: `# <step>`
- `## Contract` — five bold bullets: **Needs** / **Value** / **Output files** /
  **Harness return** / **Review gate**. Needs, Output files and Review gate are themselves
  lists. Needs is INFORMATION the step consumes, artifact-blind — never upstream step names
  or artifact paths; the harness decides where each item comes from, and ordering lives in
  the graph alone. Seed Needs from the step's Inputs cell in the decomposition table,
  refining wording only — where the cell seems wrong, raise a `## Questions` item, never
  diverge silently. Output files stay concrete paths with `[CREATED|UPDATED]` markers.
- `## Example artifact` — a compact, fenced example of the document the step produces; what
  it shows is what the suite will pin.
- `## Return Format` — the step's harness return, verbatim.
- no other sections — the file is a clean artifact: questions never live in it, they go in
  your own harness return below.

When the decomposition index's spec link for this step is not yet live, update the index so
every spec is reachable from it.

## Return format

```
## Changed:
- [CREATED] <name>/_specs/steps/<step>/index.md

## Questions:
```

`## Questions:` stays empty unless the decomposition truly under-determines the step.
