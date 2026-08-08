# Write the project briefing

You receive the repo this run documents, the direction the user stated for it, and — when
`{vault}/docs/_specs/index.md` already exists — the previous briefing. Everything else you read
yourself.

Produce the shaping layer every later step reads from: a short, current statement of what the
project is, who it serves and where it is heading, plus the drift against the previous briefing.

Read for the project's own account of itself and how it is actually built: the README, the root
agent/contributor guide, the package or plugin manifest, the directory layout, and the surfaces it
ships to users. State the project as it is now — not as its history explains it. Where the user's
stated direction contradicts what the repo shows, the user's direction wins for **Where it is
heading**; the repo wins for **What it is**.

## The file to write

`{vault}/docs/_specs/index.md` — created on the first run, rewritten in place afterwards.

- frontmatter: author none of your own; preserve an existing block verbatim — `reviewed_at` is
  stamped by the harness at the gate, never by you
- H1 `# {project} — Briefing`
- `## What it is` — one or two tight paragraphs: what the project does, the shape it takes, and
  where its artifacts live. Concrete nouns from the repo, not category words.
- `## Who it serves` — a bullet per audience, each opening with a bold audience name, then what
  that audience comes to the documentation for
- `## Where it is heading` — one paragraph: the direction the project is committed to, and the
  near-term work that follows from it
- nothing else — no history section, no "it used to be" narration, no changelog. The file is a
  current-state snapshot; a reader who has never seen the project must finish it knowing what the
  project is and who it is for.

Rewriting replaces the body wholesale. Never append a new version beside the old one, and never
keep a superseded claim for context.

## The vision shift

Compare your briefing against the previous one and name, in one line, what moved in the *vision* —
what the project is, who it serves, where it is heading. Wording changes and sharper phrasing are
not shifts; a changed audience, a changed shape, or a changed direction is. Report `none` when the
vision held, and `none` on the first run, where there is no previous briefing.

The shift lives in the return only. Never write it into the file — the file carries no record of
what it used to say.

## Return format

```
## Changed:
- [CREATED|UPDATED] {vault}/docs/_specs/index.md

## Notes:
- vision shift: {one line naming what moved against the previous briefing, or `none`}

## Questions:
```

`## Questions:` stays empty unless the repo and the user's stated direction conflict in a way you
cannot resolve.
