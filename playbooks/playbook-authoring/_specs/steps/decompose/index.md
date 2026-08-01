---
status: spec-ing
---

# decompose

[← index](../../index.md)

## Contract

- **Needs** —
  - a clear playbook goal and success-result vision
  - the artifacts working path
  - the user's wishes and suggestions
  - any other valuable input the user provided
- **Value** — a light, high-level index the user can model against: reorder steps, redraw
  boundaries, answer scope questions — before any per-step detail exists. Detail lives in the
  step specs; this file stays small enough to review in one sitting, so nothing under the
  graph restates what the graph or the table already says.
- **Output files** —
  - `[CREATED] <slug>/_specs/index.md`, sections in order:
    - a one-paragraph intro
    - `## Graph` — a yaml fence where a node whose value is a LIST is a step (the list is its
      dependencies) and a node whose value is a MAPPING is a subgraph (`dependencies:` +
      `graph:` required, `repeat:` prose optional)
    - `## Steps` — table: step | summary | inputs | artifact | gate | model | spec — inputs
      the INFORMATION the step consumes, compact and `;`-separated, artifact-blind (never
      upstream step names or file paths; the user reviews the information flow here and the
      step specs seed their Needs from these cells), model as `model:effort` (default
      `opus-5:medium`, deviate only where another tier clearly fits), spec linking the
      future `steps/<step>/index.md`
    - `## Questions` — checklist of everything the user must settle before step specs are
      written
    - no `## Decisions` section — settled items (the brief's wishes, the state-machine
      persistence-tier verdict `state machine: <ephemeral|minimal|rich> — <rationale>`)
      travel as `decision:` lines in the harness return; the runner records them via
      `record-decision`; an open verdict is a `## Questions` item instead
- **Harness return** — `## Changed:` list, the count of open questions, and one
  `decision: <summary>` line per settled item.
- **Review gate** —
  - the user answers the Questions in-file, edits the table and graph directly where they
    disagree, and confirms at the gate

## Example artifact

```markdown
# mod-review — Decomposition

Review a module: findings gathered per changed file, composed into one report the user signs
off.

## Graph

    graph:
      sweep-pipeline:
        dependencies: []
        repeat: once per changed file; instances may run in parallel
        graph:
          sweep: []
      compose: [sweep-pipeline]

## Steps

| Step    | Summary                          | Inputs                                          | Artifact                     | Gate             | Model           | Spec                           |
| ------- | -------------------------------- | ----------------------------------------------- | ---------------------------- | ---------------- | --------------- | ------------------------------ |
| sweep   | collect findings per file        | one changed file's path and content             | `_review/<file>.md` findings | none             | sonnet-5:medium | [spec](steps/sweep/index.md)   |
| compose | compose findings into the report | the target module name; the sweep findings      | `_review/review.md` report   | confirm findings | opus-5:medium   | [spec](steps/compose/index.md) |

## Questions

- [ ] Does sweep cover only changed files, or the whole module?
- [ ] Is the report one document or one per severity?
```

## Return Format

```markdown
## Changed:

- [CREATED] mod-review/_specs/index.md

## Notes:

- 2 question(s) open
- decision: findings stay per-file on disk; only the composed report is gated
- decision: state machine: minimal — single deliverable, one confirm gate, no cross-playbook handoff
```
