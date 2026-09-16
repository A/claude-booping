# clarifications.md format

Sidecar beside `index.md` in the plan directory, holding every question a run could not answer itself. Seeded by the groom scaffold with its H1 and nothing else. Posted to the tracker verbatim, so it is plain markdown with no frontmatter.

## Shape

One H2 per question, in the order they were raised:

```
## C{n} — {topic} — open|answered
```

- `C{n}` — the question id, numbered from `C1` across the whole file and never reused.
- `{topic}` — a few words naming what the question is about.
- `open` | `answered` — the state marker, the last segment of the heading.

Under the heading, in this order:

- `**Asked:** {YYYY-MM-DD} — {step}` — the date and the step that raised it. Required.
- `**Question:** {one paragraph}` — required.
- `**Options:**` — optional, a bullet per candidate answer when the question is a choice.
- `**Answer:**` — required; free markdown from the end of the label to the next H2 or the end of the file. Lists, paragraphs and fenced code all belong here as-is: nothing is escaped, and no line needs a continuation marker.

An open question carries the `**Answer:**` label with an empty body.

## Answered test

A question is answered when **both** hold:

1. its H2 ends in `answered`, and
2. its `**Answer:**` body is non-empty — at least one non-blank line before the next H2.

A heading that says `answered` over an empty body is not answered, and neither is a filled body under an `open` heading. Both are malformed and the question stays open.

## Example

```markdown
# Clarifications

## C1 — retention window — answered

**Asked:** 2026-08-14 — draft-plan

**Question:** How long should exported archives be retained before the cleanup job removes them?

**Options:**

- 7 days — cheapest, matches the temp-file convention
- 30 days — covers a monthly support cycle
- Never expire — user deletes them by hand

**Answer:**

30 days, with one caveat.

The cleanup job should skip any archive that has been downloaded at least once in the last week — support tends to re-share a link days after the ticket closes, and a hard 30-day cut would break those.

For archives above 1 GB, drop to 7 days regardless:

- storage cost is dominated by a handful of large exports
- the ones that big are always one-off migrations, never re-downloaded

## C2 — teams without a billing contact — open

**Asked:** 2026-08-14 — draft-plan

**Question:** Which address receives the export notice when a team has no billing contact set?

**Answer:**
```
