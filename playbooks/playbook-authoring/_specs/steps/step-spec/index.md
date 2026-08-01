---
status: spec-ing
---

# step-spec

[← index](../../index.md)

## Contract

- **Needs** —
  - the target step name
  - the confirmed decomposition
  - the original procedure description
- **Value** — the per-step working spec: the full five-bullet contract plus a concrete example
  of the step's artifact, in a file the user refines and confirms directly — the example
  replaces chat back-and-forth and later becomes the source of the smoke-tier contract.
- **Output files** —
  - `[CREATED] <name>/_specs/steps/<step>/index.md`:
    - the five-bullet contract (Needs / Value / Output files / Harness return / Review gate —
      Needs is INFORMATION the step consumes, artifact-blind: the harness decides where each
      item comes from, and ordering lives in the graph alone; Needs seeds from the step's
      Inputs cell in the decomposition table, refined in wording only — a disagreement with
      the confirmed cell is a `## Questions` item, never a silent divergence; Needs, Output
      files and Review gate are themselves lists)
    - an `## Example artifact` section holding a compact, fenced example of the document the
      step produces
    - a `## Return Format` section showing the step's harness return verbatim
  - `[UPDATED] <name>/_specs/index.md` — the step's spec link is live (backlink rule: every
    spec is reachable from the index)
- **Harness return** — `## Changed:` list.
- **Review gate** —
  - the user refines the spec in-file and confirms at the gate: the contract bullets
    and, for a markdown artifact, the example — what the example shows is what the suite will
    pin

## Example artifact

```markdown
# compose

[← index](../../index.md)

## Contract

- **Needs** — the target module name; sweep's findings on disk.
- **Value** — one report the user signs off instead of raw per-file findings.
- **Output files** — `[CREATED] review.md`; `[UPDATED] index.md` — link to the report.
- **Harness return** — `## Changed:` list.
- **Review gate** — user confirms findings before anything is filed.

## Example artifact

    # mod-review — auth

    ## Findings
    - [HIGH] token expiry uses `<` … (auth/session.py)
```
