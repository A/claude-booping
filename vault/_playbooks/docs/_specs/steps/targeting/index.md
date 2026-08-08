---
status: awaiting-spec-confirm
---

[← index](../../index.md)

# targeting

## Contract

- **Needs** —
  - the confirmed change table — every in-scope change with its id, its type (vision shift /
    new feature / refactoring / feature drop / chore) and what it touched, as the user left it
    after extensions and refinements
  - each audience's tone and depth needs — the depth ceiling, the voice, and what must be
    withheld from that audience
  - each documentation surface's format and audience — where it lives, how it is written, how
    deep it goes, and whether this run seeds it or appends to it
  - the feature index — features, capabilities and the groups that give the documentation its
    structure, so a change is placed under the group it already belongs to instead of a home
    invented for it
- **Value** — the one place where the role layer and the surface layer meet, and the last point
  at which anything can still be decided cheaply: after it, every write is authorised by a row
  and no writer invents a destination. Oversharing is settled here once — a change that matters
  to a plugin user and not to a contributor gets a row for the one surface and not the other, at
  the depth that role's ceiling allows — so `write` never re-litigates audience fit per file.
  **One row per destination document** is also the loop's unit of parallelism: `update` spawns
  one instance per row, and instances cannot collide because no two rows name the same file — a
  change touching three surfaces is three assignments folded into three existing rows, never a
  row of its own. The table doubles as the run's progress memory: its **Progress** column is what
  the loop advances (`pending` → `written` → `compacted` → `verified`), which is how a run
  resumed at `updating` in a later session knows which destinations are finished without a state
  machine per destination. The changelog is deliberately outside the plan — it has its own step
  and its own surface — and changes that land nowhere are stated with their reason rather than
  quietly dropped, so the gate sees the whole confirmed table accounted for.
- **Output files** —
  - `[UPDATED] {vault}/docs/{YYYYMMDDHHmm}-{title}.md` — the run record, gaining a
    `## Targeting plan`:
    - one table row per destination document: **Destination** (the file's path, a concrete
      markdown file — never a directory), **Roles** (names taken from the roles file, never
      invented), **Changes** (the change table's ids assigned to it), **Must say** (one clause
      per assigned change, already pitched at the depth those roles allow), **Progress**
      (`pending` when the plan is written)
    - no two rows name the same file, and no row names `CHANGELOG.md` — the changelog is the
      `changelog` step's, not a loop destination
    - a closing `## Not targeted` list — every confirmed change that gets no row, each with the
      reason it needs no document
    - a rework rewrites the whole section rather than appending, preserving any Progress value a
      row has already reached
    - no frontmatter of the step's own: `targeting_reviewed_at:` is stamped by the confirming
      edge's hook
  - no other file — no destination document is opened or written here, and the spec set is
    read-only to this step even where the planning exposes a gap in it
- **Harness return** — the standard block, composed by the runner in the driving conversation
  and used verbatim as the gate's presentation. `## Changed:` names the run record alone,
  annotated with the destination count and how many confirmed changes were assigned. `## Notes:`
  carries one line per row — destination, its roles, its change ids and what it must say in a
  clause — then the not-targeted lines and a line stating the instance count and that no two
  rows share a file. `## Questions:` stays empty: the plan question is the gate itself.
- **Review gate** —
  - confirm the targeting plan before anything is written — **this gate always fires**, at every
    severity the run may be driven with
  - the runner holds it at `awaiting-targeting-confirm`, presenting the rows from the return; a
    rework answer — a destination, an assignment, or what a row must say — re-enters `targeting`
    over the same inputs plus the correction
  - the confirming edge stamps `targeting_reviewed_at:` and commits the vault; the step itself
    stamps nothing
- **Delegation** — assisted: no `detached:` key. The runner performs the step in the driving
  conversation, because it owns the plan it must present at a gate that always fires, and
  delegates the spec-set reads to `{{ config.core.research_agent }}`, which returns surfaces,
  roles and feature groups compressed to exactly what a row needs — the three spec files never
  enter the driving context whole. The decomposition's `opus-5:high` names the reasoning depth of
  that driving turn, not a sub-agent to spawn.

## Example artifact

The `## Targeting plan` section appended to
`{vault}/docs/202608081352-retro-and-code-review-track-splits.md`:

```markdown
## Targeting plan

| Destination | Roles | Changes | Must say | Progress |
| --- | --- | --- | --- | --- |
| `README.md` | Plugin user | C1, C3 | C1: the Statuses narrative now describes retro as its own track, plan statuses ending at `done`. C3: code review is queued from plan frontmatter, one line, no mechanics. | pending |
| `documentation/playbook.md` | Playbook author | C1, C2 | C1: the retro machine's statuses and its `--target` addressing. C2: lessons are addressed by a `targets:` list — schema and the four target forms. | pending |
| `documentation/vault.md` | Playbook author, Plugin user | C2 | `_lessons/` holds flat files carrying `targets:`; describe the current shape only — no per-surface-file narration. | pending |
| `documentation/project_config.md` | Playbook author | C4 | `booping query` reads vault frontmatter; query specs sit beside their consumer under `core.{name}_playbook.queries`. | pending |
| `CLAUDE.md` | Contributor | C1, C3, C4 | Lifecycle section: the two tracks and the frontmatter join (`retro:`, `code_review:`). One clause for `booping query` in the CLI list. | pending |

## Not targeted

- C5 (chore) — CI job ordering in `just ci`; no user-visible effect and no surface documents job
  order.

`CHANGELOG.md` carries C1, C3 and C4 as well, written by the `changelog` step — it is never a
row here.
```

A run whose change table is entirely chores writes the heading, an empty table and a
`## Not targeted` list holding every change, and the gate asks whether to close the run rather
than enter the loop.

## Return Format

```markdown
## Changed:
- [UPDATED] {vault}/docs/{YYYYMMDDHHmm}-{title}.md — targeting plan, {n} destinations, {m} of {k} confirmed changes assigned

## Notes:
- {destination} — {roles} — {change ids}: {what it must say, in a clause}
- not targeted: {change id} ({type}) — {why no document needs it}
- loop: {n} update instances, no two rows sharing a file

## Questions:
```

One `## Notes:` line per row in table order, then one per not-targeted change, then the loop
line. No prose outside the block.
