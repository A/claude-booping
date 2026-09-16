## Milestone contract rules

Every milestone file is read by a worker holding only it, `index.md` and the repo. Write it so that
worker never has to decide *how* to work.

- **One procedure, never a choice.** Scope prose states the single way to produce the artifact. A
  sentence shaped "by hand **or** via `{tool}`" makes the worker do both — hand-derive, then run the
  tool anyway. Pick the cheaper one and name only it.
- **`## References`** names, where such files exist, 1–3 existing files the worker copies the shape
  of, by path, plus the path of any format spec it must not go looking for. A milestone producing an
  artifact in an unfamiliar format and naming no reference sends the worker searching the filesystem.
- **`## Verify` is one command, scoped to this milestone's changes.** No alternatives, no "and also
  run". Whole-repo gates belong to `index.md`'s Final Verification; the runner owns them.
- **No report-only deliverables.** A table, cross-check or rationale the worker must produce is
  named as a path plus a verb — "Create `{path}`" or "Append to `{path}`" — relative to the repo
  root or to the plan directory, never absolute. The worker's checkout is not this one.
