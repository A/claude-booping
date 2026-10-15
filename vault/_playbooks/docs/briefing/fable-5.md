# Write the project briefing

You receive the repo this run documents, the direction the user stated for it, and the run record
`{vault}/docs/_runs/{YYYYMMDDHHmm}-{title}.md`. Everything else you read yourself.

Produce the shaping layer every later step reads from: a short, current statement of what the
project is, who it serves and where it is heading, plus the drift against the previous briefing.

## The values

{% set values = 'core.docs_playbook.queries.values' | query -%}
{% if values -%}
| Value | Kind | Summary | Path |
| --- | --- | --- | --- |
{% for v in values -%}
| {{ v.title }} | {{ v.kind }} | {{ v.summary }} | {{ v.path }} |
{% endfor -%}
{%- else -%}
_No value records._
{%- endif %}

Read reference/0001 (audience) under the project specs tier root, then the project's own account
of itself and how it is actually built: the README, the root `CLAUDE.md`, the package or plugin
manifest, the directory layout, and the surfaces it ships to users. Open a value record only when
its summary leaves a claim unsettled. State the project as it is now — not as its history explains
it. Where the user's stated direction contradicts what the repo shows, the user's direction wins
for **Where it is heading**; the repo wins for **What it is**.

## The section to write

A `## Briefing` section in the run record — added after `## Scope` on the first pass, rewritten in
place on a rework. Nothing else in the record is touched.

- `### What it is` — one or two tight paragraphs: what the project does, the shape it takes, and
  where its artifacts live. Concrete nouns from the repo, not category words.
- `### Who it serves` — a bullet per audience in reference/0001, each opening with a bold audience
  name, then what that audience comes to the documentation for
- `### Where it is heading` — one paragraph: the direction the project is committed to, and the
  near-term work that follows from it
- nothing else — no history, no "it used to be" narration. A reader who has never seen the project
  must finish it knowing what the project is and who it is for.

Nothing under `specs/` is written: the records are the owner's model, and this section reads them.

## The vision shift

The baseline is the `## Briefing` section of the newest earlier run record under
`{vault}/docs/_runs/` that has one. Name, in one line, what moved in the *vision* — what the
project is, who it serves, where it is heading. Wording changes and sharper phrasing are not
shifts; a changed audience, a changed shape, or a changed direction is. Report `none` when the
vision held, and `none` when no earlier record carries a briefing.

A shift that contradicts a value record is named in the note with that value's path; the value
itself is never edited. The shift lives in the return only, never in the section.

## Return format

```
## Changed:
- [UPDATED] {vault}/docs/_runs/{YYYYMMDDHHmm}-{title}.md

## Notes:
- vision shift: {one line naming what moved against the baseline briefing, with the path of any value it contradicts, or `none`}

## Questions:
```

`## Questions:` stays empty unless the repo and the user's stated direction conflict in a way you
cannot resolve.
