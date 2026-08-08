---
status: awaiting-spec-confirm
---

[← index](../../index.md)

# briefing

## Contract

- **Needs**
  - the repo's self-description and architecture — what the project presents itself as, how it is
    built, and which surfaces it ships
  - the direction the user states for the project — near-term intent and anything that has moved
  - the previous briefing, when one exists
- **Value** — the shaping layer every later step reads from: a short, current statement of what the
  project is, who it serves and where it is heading, plus the named drift against the previous
  briefing that tells the run whether the vision itself moved rather than only the code.
- **Output files**
  - `[CREATED|UPDATED] {vault}/docs/_specs/index.md` — the project briefing, a current-state
    snapshot; created on the first run, rewritten in place afterwards
- **Harness return** — `## Changed:` naming the briefing file, and `## Notes:` carrying a single
  `vision shift:` line — what moved against the previous briefing, or `none` — which the runner
  presents at the gate. The shift is named in the return, never accumulated in the file.
- **Review gate**
  - present the briefing and stop — the user confirms what the project is, who it serves and where
    it is heading
  - a named vision shift must be acknowledged in the answer; silence never counts
- **Delegation** — `detached`, `fable:high` (the decomposition's `fable-5:high`; `fable` is the
  tier the `detached:` grammar accepts).

## Example artifact

```markdown
---
reviewed_at: 2026-08-08 14:12
---
# booping — Briefing

## What it is

A Claude Code plugin that grooms and executes work across a user's projects. One shipped skill,
`/playbook`, drives everything procedural; each procedure is a playbook — a manifest, a step graph,
and one prompt per step, rendered through Jinja against the merged project context. Run artifacts
live in a per-project vault (`~/Claude/{project}/`, or a repo-local directory via the `.booping`
marker), never in the plugin repo.

## Who it serves

- **Solo developers and small teams** running plan-driven work inside Claude Code — grooming,
  development, review, retro and learning arrive as one connected track.
- **Playbook authors** extending booping for their own project — the vault's `_playbooks/`,
  `_lessons/` and `config.yaml` are the entire extension surface.
- **Readers evaluating the plugin** — README and the public docs site are their entry points.

## Where it is heading

Playbooks as the only extension unit: new procedures ship as playbooks rather than skills, and
project-specific shaping stays in vault lessons instead of forked bodies. Near-term work
consolidates the learn track's targets and moves structured data out of prose into
`src/config.yaml`.
```

## Return Format

```
## Changed:
- [CREATED|UPDATED] {vault}/docs/_specs/index.md

## Notes:
- vision shift: {one line naming what moved against the previous briefing, or `none`}

## Questions:
```
