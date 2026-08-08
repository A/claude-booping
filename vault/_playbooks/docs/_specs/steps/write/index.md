---
status: awaiting-spec-confirm
---

[← index](../../index.md)

# write

## Contract

- **Needs** —
  - one destination markdown document — its path and its current content, read whole, because a
    change is folded into the wording that is already there rather than appended to the end
  - the changes assigned to that destination and what each one must say — the clauses settled at
    the targeting gate, already pitched at the depth the destination's audience allows
  - the roles that destination addresses, with each one's depth ceiling, tone and withheld set
  - the destination surface's format and conventions — how it is built and published, how long its
    entries run, how it links and heads its sections — so the fold reads as part of the file
- **Value** — the step where an assigned change becomes prose on a real surface. Everything it
  could get wrong was decided upstream and is deliberately not re-opened here: the destination is
  the targeting row's, the audience fit is the row's, the depth ceiling is the roles file's, and a
  fact is the change table's. Re-deciding any of them behind a gate that already fired is the
  failure mode this contract exists to prevent — the step writes what its row says, and anything
  it cannot write faithfully goes in the return instead of being improvised into the file. Its
  second discipline is **one file**: the loop spawns one instance per row and rows never share a
  destination, so instances are safe to run in parallel exactly as long as no instance opens a file
  outside its own row. What lands is a current-state snapshot — a changed behaviour replaces the
  sentence that described the old one, a dropped capability leaves the document rather than being
  annotated as removed, and no "this used to work differently" narration survives the fold. The
  draft is judged on being correct and complete at its depth, not on being tight: `compact` runs
  next and is the pass that cuts, so a fact stated twice is cheap and a fact missing is not — which
  is not a licence to pad, only the reason not to trade coverage for brevity here.
- **Output files** —
  - `[CREATED|UPDATED] {the targeting row's destination path}` — a repo-relative markdown file, the
    single file this instance may write; `[CREATED]` only when the row names a page that does not
    exist yet under a documented directory, in which case the surface's conventions shape the new
    file's skeleton
  - the fold edits sections in place and keeps the file's own structure — heading style, link form,
    entry length, ordering — adding a section only when no existing one owns the change
  - frontmatter the file already carries survives untouched, and the step adds none of its own
  - never a source file: the destination set is markdown by construction and code-level docs stay
    with `develop`
  - nothing else is written — not the run record (the runner advances the row's **Progress** column
    from this return), not the spec set, not another row's destination, not `CHANGELOG.md`
- **Harness return** — `## Changed:` the single destination line, annotated with the change ids that
  landed in it. `## Notes:` one line per assigned change — the id, the section it landed in and
  whether that section was created, rewritten or extended — then a `dropped legacy:` line for
  outdated wording the fold removed, and a `not written:` line for anything the row asked for that
  could not be written faithfully. The runner holds what this destination now says from these lines
  alone and never opens the file. `## Questions:` stays empty: the step has no gate to ask into,
  and a blocker is a `not written:` line.
- **Review gate** —
  - none — the targeting plan was confirmed at `awaiting-targeting-confirm`, and that confirmation
    is this instance's authorisation to write
  - the `update` subgraph declares no machine, so no transition fires on this return; the runner
    marks the row `written` in the targeting-plan table and hands the file to `compact`
- **Delegation** — detached: `detached: "fable:medium"` (the decomposition's `fable-5:medium`;
  `fable` is the tier the `detached:` grammar accepts). A generic sub-agent fetches this body and
  performs the whole fold, so the destination's full current content — the bulk of the reading —
  never enters the runner's context, which receives the path and the digest. The agent's bootstrap
  needs the row verbatim (destination, assigned change ids, **Must say** clauses), the role entries
  that row names, and the destination's surface row; it needs no source reading — fact-checking
  against code is `verify`'s.

## Example artifact

The destination for the targeting row `documentation/vault.md` | Playbook author, Plugin user | C2 |
"`_lessons/` holds flat files carrying `targets:`; describe the current shape only — no
per-surface-file narration."

The file's `## _lessons/` section, rewritten in place:

```markdown
## `_lessons/`

Flat markdown files, one lesson per file, at the vault root and at `{home_dir}/_lessons/` for
lessons that apply to every project.

Each file carries a `targets:` list naming where it applies:

| Target form | Injected into |
| --- | --- |
| `{playbook}` | every step of that playbook |
| `{playbook}/{step}` | that step alone |
| `agent:{id}` | that agent's rendered body |
| `skill:{name}` | that skill's rendered body |

A lesson with no `targets:` list injects nowhere. `learn` writes here and to the attached repo's
own `CLAUDE.md` — nowhere else.
```

The section above it, listing the vault's directories, gains one clause on the same fold; the rest
of the file is untouched. What the fold removed rather than rewrote: the paragraph explaining that
lessons were once kept in one file per surface — legacy narration has no place on a snapshot, and
it is reported as `dropped legacy:` in the return, not marked in the document.

## Return Format

```markdown
## Changed:
- [CREATED|UPDATED] {destination path} — {change ids that landed}

## Notes:
- {change id} → {section}: {created|rewritten|extended}, {what it now says in a clause}
- dropped legacy: {outdated wording removed, or none}
- not written: {what the row asked for that could not be written faithfully, or none}

## Questions:
```

One `## Notes:` line per assigned change, in the row's order, then the two summary lines. No prose
outside the block.
