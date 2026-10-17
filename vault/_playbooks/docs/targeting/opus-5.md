# Plan the role × surface writes

You perform this step yourself, in the driving conversation: you own the plan you present at the
gate that follows, and that gate always fires.

You have the workdir (`{vault}/docs/`), the run record whose change table the user has just
extended and confirmed, the feature index below, and spec records `sync-specs` has already folded
those changes into. Read the change table directly — each change's id, its type, what it touched,
and the record its spec-set effect names. Hand the record reads to `booping:booping-researcher`,
one brief covering the surfaces record `{vault}/reference/0003-documentation-surfaces.md`
and the audience record `{vault}/reference/0001-audience.md`, and ask for exactly what a row
needs back: per surface its path, format, audience, depth and whether this run seeds it or appends
to it; per role its depth ceiling, its voice and its withheld set. The two records never enter the
driving context whole; the documentation's structure comes from the surfaces record.

## The feature index

{% set features = 'core.docs_playbook.queries.features' | query -%}
{% if features -%}
| Story | Summary | Status | Path |
| --- | --- | --- | --- |
{% for f in features -%}
| {{ f.title }} | {{ f.summary }} | {{ f.status }} | {{ f.path }} |
{% endfor -%}
{%- else -%}
_No story records._
{%- endif %}

A story `sync-specs` created this run is not in the index above — its path is in `sync-specs`'
return.

## The section to write

`{vault}/docs/_runs/{YYYYMMDDHHmm}-{title}.md` gains a `## Targeting plan`. Nothing else — no
destination document is opened or written here, and the spec records are read-only to you even
where the planning exposes a gap in them.

One table row per destination document:

| Column | Holds |
| --- | --- |
| **Destination** | the file's path — a concrete markdown file, never a directory |
| **Roles** | names taken from the audience record, never invented |
| **Changes** | the change table's ids assigned to this file |
| **Must say** | one clause per assigned change, already pitched at the depth those roles allow |
| **Progress** | `pending` |

- **No two rows name the same file.** Rows are the loop's unit of parallelism — `update` spawns
  one instance per row — so a change touching three surfaces is folded into three existing rows,
  never given a row of its own.
- No row names `CHANGELOG.md`: the changelog has its own step and its own surface.
- Oversharing is settled here once. A change that matters to a plugin user and not to a
  contributor gets a row for the one surface and not the other, at that role's ceiling, so `write`
  never re-litigates audience fit per file.
- A change is placed under the story it moves — for a new-feature row, the story `sync-specs`
  created for it. A change no story covers is placed by surface alone, its **Must say** clause
  opening `no story —`; never a home invented for it.
- A closing `## Not targeted` list names every confirmed change that gets no row, each with the
  reason it needs no document. Changes that land nowhere are stated, never quietly dropped.
- Write no frontmatter: `targeting_reviewed_at:` is the confirming edge's hook.
- A rework rewrites the whole section rather than appending, preserving any Progress value a row
  has already reached.

```markdown
## Targeting plan

| Destination | Roles | Changes | Must say | Progress |
| --- | --- | --- | --- | --- |
| `README.md` | Plugin user | C1, C3 | C1: the Statuses narrative now describes retro as its own track, plan statuses ending at `done`. C3: code review is queued from plan frontmatter, one line, no mechanics. | pending |
| `documentation/vault.md` | Playbook author, Plugin user | C2 | `specs/rule/` records carry `targets:`; describe the current shape only — no per-surface-file narration. | pending |

## Not targeted

- C5 (chore) — CI job ordering in `just ci`; no user-visible effect and no surface documents job order.
```

A change table that is entirely chores gets the heading, an empty table and a `## Not targeted`
list holding every change — then the gate asks whether to close the run rather than enter the loop.

Write the section, then compose the return: it is the gate's presentation verbatim, so the user
confirms the rows from it without opening the file.

## Return format

```markdown
## Changed:
- [UPDATED] {vault}/docs/_runs/{YYYYMMDDHHmm}-{title}.md — targeting plan, {n} destinations, {m} of {k} confirmed changes assigned

## Notes:
- {destination} — {roles} — {change ids}: {what it must say, in a clause}
- not targeted: {change id} ({type}) — {why no document needs it}
- loop: {n} update instances, no two rows sharing a file

## Questions:
```

One `## Notes:` line per row in table order, then one per not-targeted change, then the loop line.
`## Questions:` stays empty — the plan question is the gate itself. No prose outside the block.
