---
status: spec-ing
---

# states

[← index](../../index.md)

## Contract

- **Needs** —
  - the confirmed decomposition — graph and Steps table
  - the state-machine persistence-tier verdict from `_specs/DECISIONS.md` (or the user's
    override of it)
  - the brief
- **Value** — the run's state chart in final vocabulary, reviewed as tables the user can edit
  in place; `manifest` translates it into `playbook.yaml` verbatim, so this is the single
  place machine granularity is decided.
- **Output files** —
  - `[CREATED] <slug>/_specs/states.md`:
    - H1 `# <slug> — State machines`, then per machine a `## <name>` heading, an
      `artifact:` line (run-workdir-relative; outer machine `index.md`, per-instance
      `steps/{instance}/index.md`), an inventory table only when superstates or terminals
      exist, and a transitions table `State | To | When | Gates | Hooks` — no transition
      names, terminals `ᵗ`, Hooks cells machine-readable only (`;`-separated when a cell
      carries more than one hook)
    - every exit from an `awaiting-*-confirm` status stamps `reviewed_at=@now` on what the
      user reviewed, one hook per reviewed file, always the explicit-path form
      `frontmatter-update <path> reviewed_at=@now` — path relative to the run workdir, even
      when the reviewed file IS the machine's own artifact. No gate is exempt. A reviewed
      subject that cannot legally carry frontmatter — a directory, or a YAML file a loader
      parses — stamps a subject-keyed `frontmatter-update <path> <subject>_reviewed_at=@now`
      on the machine's own artifact instead; that is the only compromise. No `*_confirmed` /
      `smoke_green` / `completed` stamps — the status transition carries fact and time; keys
      carrying run data are unaffected
    - the file itself is design documentation, not a state artifact; it carries no `status:`,
      only the `reviewed_at` its own review gate stamps
  - `[UPDATED] <slug>/_specs/index.md`:
    - a plain link line right after the graph fence — no new section heading:
      `State machines: [<machine>](states.md#<machine>) · …`
    - frontmatter preserved — the index re-enters review through the harness's transition
  - on an ephemeral verdict without user override: no file change, skip note in the return
- **Harness return** — `## Changed:` list; `## Notes:` machine count + tier, or the skip
  note.
- **Review gate** —
  - the user confirms machine granularity — statuses, gates, hooks, artifacts — in-file and
    re-confirms the index at the gate

## Example artifact

`mod-review/_specs/states.md`:

```markdown
# mod-review — State machines

## main

artifact: `index.md`

| Superstate | States |
| -- | -- |
| terminal | `done`ᵗ |

| State | To | When | Gates | Hooks |
| -- | -- | -- | -- | -- |
| `none` | `sweeping` | run starts | | |
| `sweeping` | `awaiting-report-confirm` | report composed | every file's findings on disk | |
| `awaiting-report-confirm` | `done`ᵗ | user confirms the report | explicit confirmation captured | `frontmatter-update report.md reviewed_at=@now` |
```

and the link line the index picks up, right after its graph fence:

```markdown
State machines: [main](states.md#main)
```

## Return Format

```markdown
## Changed:
- [CREATED] mod-review/_specs/states.md
- [UPDATED] mod-review/_specs/index.md

## Notes:
- 1 machine(s), tier minimal
```
