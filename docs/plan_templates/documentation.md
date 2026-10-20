---
name: documentation
description: Authoring or restructuring user-facing documentation — multi-page sites, READMEs, cross-linked guides, with optional static-site build pipeline (MkDocs, Jekyll, Docusaurus, etc.).
---

# Plan Body

## Context

Who the docs are for (end users vs contributors), what they cover, what gap motivates the work. Note any existing documentation that overlaps and how the new content relates to it (replaces / supplements / cross-links).

## Decisions

Typical topics: site generator (MkDocs / Jekyll / Docusaurus / plain markdown), theme, where source files live, how the published site is built and hosted (GitHub Pages branch, Netlify, etc.), per-page vs single-page split, what stays in README vs moves to the docs site, lazy-loading from skills if applicable.

## Information architecture

Sketch the page tree with a one-line purpose per page. Call out cross-links between pages and back-links from existing surfaces (README, skill bodies, lazy-load `docs/` fragments).

```
documentation/
├── index.md          # purpose
├── ...
```

## Milestones

Order pages so each milestone produces something reviewable in isolation. A typical shape:

1. **Scaffold** — site generator config, directory layout, build/deploy CI, local-serve target. No content yet.
2. **Foundation pages** — landing/index, walkthrough, primary entry-point pages.
3. **Reference pages** — one milestone per logical group (per-skill, per-command, per-feature).
4. **Cross-references and stale-reference cleanup** — README link, skill lazy-load wiring, project-conventions doc updates.
5. **Reshape** — pause for user IA review against the rendered site; apply prose/structure changes uncovered by reading the built output.

One `### M{nn} — {title}` block per milestone, in the format draft-plan states. Its content:

- **Tasks** — opens with a **Goal** line (one sentence: what page(s) or pipeline component lands) and a **Scope** line (the pages this milestone writes or touches, their place in the page tree, and the surfaces that link to them), then one row per task:

  | Task | Description | Files | SP | Status |
  |------|-------------|-------|----|--------|
  | 1.1 | ... | `documentation/{page}.md`, `mkdocs.yml` | 2 | pending |

- **Definition of Done** — one `Task {n}.{m}` block per task, checkbox bullets only: page renders in the local build with no broken links, cross-links to/from sibling pages resolve, code blocks lint cleanly (correct language tags, runnable where applicable), no prose duplicating another page — link instead.
- **References** — where such files exist, 1–3 existing pages whose structure and voice this milestone copies, by path, plus the path of any style guide or spec it must not go looking for.
- **Verify** — build/serve the site locally and load the pages this milestone changed; check their cross-links resolve. The strict full-site build and the CI workflow run belong in Final Verification.

## Final Verification

- [ ] Local build succeeds with no warnings (`mkdocs build --strict` or equivalent).
- [ ] CI workflow runs green on the sprint branch and the published preview (if any) renders.
- [ ] Every internal cross-link resolves; every external link (package, API, doc) verified against current source.
- [ ] All references invalidated by this work are updated in the same sprint (README links, lazy-load paths, skill bodies, `CLAUDE.md` mentions). No "follow-up sweep" deferred.

## Out of scope

Explicit exclusions — e.g. "no skill-body rewrites", "no new commands documented", "no translation".

## CLAUDE.md impact

Name sections to update (e.g. add `documentation/` to the layout section, distinguish it from `docs/`), or state "No CLAUDE.md changes required — {justification}".

---

# Quality Checklist

## Frontmatter

- [ ] `title` matches the plan's H1 and `type` is the task type chosen at intake.

## Content

- [ ] Context names the audience (end users vs contributors) and the gap being closed.
- [ ] Information architecture sketch is present and shows every page with a one-line purpose.
- [ ] Each page is a milestone task or grouped with siblings under one milestone — no orphan pages.
- [ ] DoD bullets are verifiable by loading the rendered page or running the build.
- [ ] Every milestone's References names 1–3 existing files to copy the shape of where such files exist, or states that none applies.
- [ ] No milestone asks for a deliverable in the worker's report — each is named as a path plus "Create" or "Append to", relative to the repo root or the plan directory.

## Documentation hygiene

- [ ] No prose duplicated across pages — extracted to a single source and linked.
- [ ] Per-page `What it does` / purpose line near the top so the page is skimmable.
- [ ] Code blocks tagged with the correct language; commands runnable as written.
- [ ] No screenshots of text where copy-able text would do.
- [ ] No "coming soon" placeholders in pages that ship.

## Cross-references

- [ ] Every existing surface that should link to the new docs (README, skill bodies, lazy-load fragments) is updated in the same sprint, not deferred.
- [ ] Every existing surface invalidated by the new docs (now-redundant README sections, removed lazy-load files) is cleaned up in the same sprint.
- [ ] `CLAUDE.md` updated to describe the new `documentation/` layout and its relationship to other doc surfaces.

## Reshape milestone

- [ ] A reshape milestone is included if rendered output is likely to expose IA issues only post-build (typical for multi-page sites and cross-linked content).
- [ ] The reshape milestone has explicit DoD: user reads the rendered site, files prose/structure feedback as a list, feedback is applied before the plan transitions out of `in-progress`.

## CLAUDE.md impact

- [ ] Any change to top-level layout (new `documentation/` directory, new build target, new CI workflow) is reflected in `CLAUDE.md` via an owning task.
