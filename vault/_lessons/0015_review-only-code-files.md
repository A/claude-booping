---
id: 15
title: Review only code files — skip documentation, plans, and other prose
targets:
  - code-review
retro: null
created: 2026-08-10
---

Scope the review to code files only. Documentation, plans, and other prose in the diff are out of scope — do not surface findings on them.

**Example**: A sprint diff touching `src/` modules plus a plan's `index.md` and a README gets findings only on the `src/` files; the markdown changes pass through unreviewed.
