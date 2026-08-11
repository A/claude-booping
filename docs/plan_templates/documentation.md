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

The table below is generated — one row per milestone file, projected with `core.plans.milestones.table_columns` by `booping query`. Derived output: no hand-written rows, no milestone bodies in this file.

## Milestone files

One file per milestone directory under the plan directory's `milestones/`, named after that directory and seeded by `booping scaffold core.groom_playbook.milestone_scaffold` — the seed owns the file's frontmatter keys and its required headings. Write the body into that skeleton:

- **Goal** — one sentence directly under the H1: what page(s) or pipeline component lands.
- **Scope** — the pages this milestone writes or touches, their place in the page tree, and the surfaces that link to them.
- `## Tasks` — one row per task:

  | Task | Description | Files | SP | Status |
  |------|-------------|-------|----|--------|
  | 1.1 | ... | `documentation/{page}.md`, `mkdocs.yml` | 2 | pending |

- `## Definition of Done` — one `### Task {n}.{m}` block per task, checkbox bullets only: page renders in the local build with no broken links, cross-links to/from sibling pages resolve, code blocks lint cleanly (correct language tags, runnable where applicable), no prose duplicating another page — link instead.
- `## Verify` — build/serve the site locally and load the pages this milestone changed; check their cross-links resolve. Whole-repo gates — a strict full-site build, a pushed branch confirming the CI workflow green, an aggregate `ci` target — run once in `index.md`'s Final Verification, never per milestone.

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
- [ ] `sp` equals the sum of the milestone files' `sp`.

## Content

- [ ] Context names the audience (end users vs contributors) and the gap being closed.
- [ ] Information architecture sketch is present and shows every page with a one-line purpose.
- [ ] Each page is a milestone task or grouped with siblings under one milestone — no orphan pages.
- [ ] DoD bullets are verifiable by loading the rendered page or running the build.
- [ ] Every task lists exact file paths.
- [ ] Every milestone is a file in `milestones/` carrying its own goal, tasks, DoD and Verify — no milestone body in `index.md`.
- [ ] `index.md`'s milestone table has one row per milestone file and matches their frontmatter.
- [ ] Every milestone file's `## Verify` includes a build or local-serve check of the pages that milestone changed — no whole-repo gate (strict full-site build, CI-workflow run, aggregate `ci` target); those belong to `index.md`'s Final Verification.
- [ ] Each milestone file executable from a fresh session with only it and `index.md` as context.

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
