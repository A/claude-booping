---
status: spec-ing
---

# manifest

[← index](../../index.md)

## Contract

- **Needs** —
  - the confirmed decomposition — its `graph:` mapping is copied verbatim, and the machines in
    `_specs/states.md` (when the index links one) translated verbatim
  - the target model (default `opus:medium`)
  - the destination root
- **Value** — the playbook's structure and identity as two small files; where the target
  model and destination root become concrete before any step dir carries them.
- **Output files** —
  - `[CREATED] <name>/playbook.yaml`:
    - `graph:` exactly as the confirmed decomposition orders it
    - when the decomposition carries `_specs/states.md`: top-level `state:` naming the outer
      machine, `state:` inside each subgraph node the file assigns one, and `states:`
      translated row-for-row (`artifact`, `initial` from the `none` row, per-state
      `transitions: [{to, when, gates, hooks}]` copied verbatim — Hooks cells are already
      machine-readable, never paraphrased — `terminal: true` for `ᵗ` states, superstate rows
      as `superstates`); no `states.md` → graph-only
  - `[CREATED] <name>/playbook.md`:
    - frontmatter: `name`, `title`, `summary`, `trigger` (user's terms, never internal step
      names), `jinja: true`; `requires_project: true` only when steps write into a booping
      project; never `graph:` — playbook.yaml owns structure
    - body: minimalistic — the renderer injects the execution graph, step summaries and gates
      from the graph and step frontmatter, so the body never lists steps, waves or gates; it
      carries only the lead, fan-out/one-at-a-time instructions, orchestrator decisions, and
      the eval-run rules (who runs which tier; steps themselves never launch one)
- **Harness return** — `## Changed:` with the two created paths; `## Notes:` optional.
- **Review gate** —
  - the user confirms name, trigger, graph, states (when present), target model and
    destination root before any per-step file is written

## Example artifact

`mod-review/playbook.yaml`:

```yaml
state: main
graph:
  sweep: []
  compose: [sweep]
states:
  main:
    artifact: index.md
    initial: sweeping
    statuses:
      sweeping:
        transitions:
          - to: awaiting-report-confirm
            when: report composed
            gates: ["every file's findings on disk"]
      awaiting-report-confirm:
        transitions:
          - to: done
            when: user confirms the report
            gates: ["explicit confirmation captured"]
            hooks: ["frontmatter-update report.md reviewed_at=@now"]
      done: {terminal: true}
```

`mod-review/playbook.md`:

```markdown
---
name: mod-review
title: Module Review
summary: Review a module file by file and compose one signed-off report.
jinja: true
trigger: reviewing a module; auditing a directory of code into a report
---

# Module Review

Your goal is one confirmed review report per module. `sweep` works per file — one sub-agent
per file, spawned in a single message, each given its subject as a **Target: <file>** line.

Eval runs are proposed, never launched — the user triggers them.
```
