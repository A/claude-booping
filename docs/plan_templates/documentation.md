---
name: documentation
description: Authoring or restructuring user-facing documentation — multi-page sites, READMEs, cross-linked guides, with optional static-site build pipeline (MkDocs, Jekyll, Docusaurus, etc.).
---

# Plan Body

## Context

Who the docs are for (end users vs contributors), what they cover, what gap motivates the work. Note any existing documentation that overlaps and how the new content relates to it (replaces / supplements / cross-links).

## Decisions

- **{Topic}**: {decision} — {why}

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

### M1: {Milestone name} — {SP} SP | pending

**Goal**: one sentence — what page(s) or pipeline component lands.

**Verify**: build/serve the site locally and load the affected pages in a browser; check cross-links resolve; on CI changes, push a branch and confirm the workflow runs green.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | ... | `documentation/<page>.md`, `mkdocs.yml` | 2 | pending |

#### Task 1.1 DoD

- [ ] Page renders in the local build with no broken links.
- [ ] Cross-links to/from sibling pages resolve.
- [ ] Code blocks lint cleanly (correct language tags, runnable where applicable).
- [ ] No prose that duplicates content already covered by another page — link instead.

---

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

- [ ] Frontmatter matches [plan frontmatter](${CLAUDE_PLUGIN_ROOT}/docs/template_plan_frontmatter.md).
- [ ] `sp` equals the sum of per-task SP across milestones.

## Content

- [ ] Context names the audience (end users vs contributors) and the gap being closed.
- [ ] Information architecture sketch is present and shows every page with a one-line purpose.
- [ ] Each page is a milestone task or grouped with siblings under one milestone — no orphan pages.
- [ ] DoD bullets are verifiable by loading the rendered page or running the build.
- [ ] Every task lists exact file paths.
- [ ] Every milestone has a `Verify` step that includes a build or local-serve check.
- [ ] Each milestone executable from a fresh session with only the plan as context.

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

## Anti-patterns (must be absent)

- [ ] No "TBD", "TODO", "details to follow" in pages that ship.
- [ ] No mixed audiences in one page (end-user content and contributor content interleaved).
- [ ] No giant single-page dump where multi-page split was the call — and vice versa.
- [ ] No content that restates the schema/code source of truth in prose where a link would do.

## External references validated

- [ ] Every package version, theme name, plugin, image tag, CLI flag, and config option named in the docs is checked against current upstream docs.
- [ ] All cross-links resolve from the rendered site (not just from raw markdown).

## CLAUDE.md impact

- [ ] Any change to top-level layout (new `documentation/` directory, new build target, new CI workflow) is reflected in `CLAUDE.md` via an owning task.
