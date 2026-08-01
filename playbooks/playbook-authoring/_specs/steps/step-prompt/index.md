---
status: spec-ing
---

# step-prompt

[← index](../../index.md)

## Contract

- **Needs** —
  - the target step name
  - the target step's confirmed contract and example
  - the confirmed manifest
  - the target model
- **Value** — the step itself: a minimal prompt body a fresh, context-isolated consumer can
  execute. Seed quality on purpose — refinement runs through eval confirmation later. The
  body's document contract comes from the step's confirmed spec: the contract bullets and the
  example artifact.
- **Output files** —
  - `[CREATED] <name>/<step>/<model>.md`: what the step receives, the artifact, the document
    contract (matching the confirmed example, including any backlink obligation from Output
    files), the harness return. No frontmatter, no harness tokens.
  - `[CREATED] <name>/<step>/prompt.md`: the Jinja wrapper — frontmatter `summary`,
    `agent: <model>:<effort>`, `review_gate` reproduced from the spec (or `null`),
    `inputs:` (one `{what, from?}` entry per Needs bullet — `what` is the information,
    artifact-blind; `from` only when the source is outside prior step returns) and
    `outputs:` (plain strings from Output files + harness return). No `name:` — the dir
    name is the step name. Body exactly the include of the body file.
- **Harness return** — `## Changed:` list; `## Notes:` with the free check
  `just verify-wrapper <playbook> <step> <model>.md`.
- **Review gate** —
  - the user reads the body and confirms the contract it states

## Example artifact

```markdown
---
summary: Compose sweep findings into one review report the user signs off.
agent: opus:medium
review_gate: "User confirms findings before anything is filed"
inputs:
  - what: the target module name
  - what: the sweep findings, one line each
outputs:
  - _review/review.md — the signed-off review report
  - index.md updated with a link to the report
---

{# prompt.md body is exactly the include of opus-5.md #}
```
