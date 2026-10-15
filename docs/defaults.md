# defaults.md format

Sidecar beside the run artefact, holding every gate and question an `autonomous` run (`core.autonomy`) settled itself instead of asking the user: in the plan directory for groom and develop, in the review's `codereviews/{dir}/` for code-review — shared by that directory's reviews. Plain markdown, no frontmatter, seeded with `# Defaults` on the first entry.

`booping defaults add` is its only writer — flags in `booping defaults add --help`. A run with no artefact writes no sidecar: it lists its defaults in its final report instead.

## Shape

One H2 per entry, in the order logged:

```
## D{n} — {step} — {YYYY-MM-DD HH:MM}
```

- `D{n}` — the entry id, numbered from `D1` across the whole file; the next is the highest plus one, never reused.
- `{step}` — the `{playbook}/{step}` the default was taken in, verbatim.
- `{YYYY-MM-DD HH:MM}` — local date and time of logging.

Under the heading, in this order, each value on one line:

- `**Asked:**` — the gate or question the run settled.
- `**Default:**` — what it decided.
- `**Why:**` — the reason, or `not stated`.
- `**Artifact:**` — a link to the run artefact, relative to the sidecar.

## Example

```markdown
# Defaults

## D1 — develop/provision — 2026-10-15 16:40

**Asked:** Confirm the branch name `feat/autonomy-modes`?

**Default:** `feat/autonomy-modes`, the proposed name

**Why:** core.autonomy is autonomous; the proposal follows the branch conventions

**Artifact:** [index.md](index.md)
```
