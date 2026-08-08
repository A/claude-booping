---
status: spec-ing
---

# interview

[← index](../../index.md)

## Contract

- **Needs** — the user's description of the desired playbook, verbatim; answers to any
  previously returned questions; the brief a prior iteration wrote, if any.
- **Value** — the answers every later step builds on — playbook slug, goal, success shape,
  artifact home — inferred from what the user already gave instead of interrogating them,
  with the user asked ONLY about real gaps.
- **Output files** — `[CREATED|UPDATED] <slug>/_specs/brief.md`, written once the slug is
  settled: sections `## Goal` (one paragraph), `## Success result` (one paragraph),
  `## Artifact home` (a single path, nothing else), optional `## Wishes` (bullet list of
  desires to address — review points, decomposition suggestions). The file is a clean
  artifact — questions never live in it.
- **Harness return** — `## Changed:` list and `## Questions:` — numbered, each answerable in
  one line, none answerable from the inputs. The slug question offers candidate slugs plus a
  free-input option. Empty Questions means the interview is complete; the return then carries
  slug, goal, success shape and artifact home verbatim, so the caller needs nothing but the
  return. An answered question is never asked again.
- **Review gate** — while Questions come back: the user answers them. Once complete: the user
  refines the brief in-file and confirms at the gate.

## Example artifact

```markdown
# mod-review — Brief

## Goal

Review a module's changed files against the project checklist and produce one signed-off
findings report per module.

## Success result

`review.md` in the module dir: findings grouped by severity, each with file:line and a fix
sketch; the user confirms it before anything is filed.

## Artifact home

`<module>/_review/`

## Wishes

- Review gate after findings, before filing.
```

## Return Format

Mid-interview:

```markdown
## Changed:

## Questions:
1. Slug: `mod-review`, `module-review`, or your own?
2. Where should the report live — inside the module dir or a top-level `_reviews/`?
```
