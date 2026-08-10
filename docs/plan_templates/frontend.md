---
name: frontend
description: Frontend feature work — UI components, state, routing, styling, accessibility. Stack-agnostic (React, Svelte, Leptos, Vue, vanilla).
---

# Plan Body

## Context

Why this work now. Current UI state, user-visible gap or bug, scope of this plan.

## Decisions

Non-obvious design choices: component decomposition, state location, styling approach, routing shape.

- **{Topic}**: {decision} — {why}

## Architecture

How the new UI fits the component tree, state flow, and data-loading boundaries. Integration points with backend APIs. Reference concrete files.

## Milestones

Generated table — one row per milestone file, projected with `core.plans.milestones.table_columns` by `booping query`. Derived output: no hand-written rows, no milestone bodies in this file.

## Milestone files

One file per milestone in the plan directory's `milestones/`, seeded by `booping scaffold core.groom_playbook.milestone_scaffold` — the seed owns the file's frontmatter keys and its required headings. Write the body into that skeleton:

- **Goal** — one sentence directly under the H1: what changes in the UI after this milestone.
- **Scope** — the components, routes and state owners in play and the files this milestone touches, plus where new components mount.
- `## Tasks` — one row per task:

  | Task | Description | Files | SP | Status |
  |------|-------------|-------|----|--------|
  | 1.1 | ... | `src/components/Foo.tsx` | 2 | pending |

- `## Definition of Done` — one `### Task {n}.{m}` block per task, checkbox bullets only: component renders with all documented props, loading / empty / error / success states covered, typecheck + test commands pass.
- `## Verify` — exact commands (scoped tests, a component's typecheck, a visual check) or observable outcomes, limited to what this milestone changed. Whole-repo gates (full test suite, repo-wide lint/typecheck, an aggregate `ci` target) run once in `index.md`'s Final Verification, never per milestone.

## Final Verification

- [ ] End-to-end user flow reproduces expected behavior in the browser / device.
- [ ] Typecheck clean.
- [ ] Unit / component tests pass.
- [ ] Visual regression / accessibility spot check if applicable.

## Accessibility & interaction *(when adding interactive UI)*

- [ ] Keyboard navigation paths enumerated.
- [ ] Screen-reader labels / roles specified where they differ from defaults.
- [ ] Focus management for dialogs / transitions called out.
- [ ] Reduced-motion / high-contrast considerations if relevant.

## Responsive & cross-browser *(when visual layout changes)*

- [ ] Breakpoint behavior specified.
- [ ] Browser / device matrix the change is verified against.

## Out of scope

Explicit exclusions — e.g. "no design-system-wide token changes", "desktop only for now".

## CLAUDE.md impact

Name sections to update, or state "No CLAUDE.md changes required — {justification}".

---

# Quality Checklist

## Frontmatter

- [ ] `title` matches the plan's H1 and `type` is the task type chosen at intake.
- [ ] `sp` equals the sum of the milestone files' `sp`.

## Content

- [ ] Context names the user-visible outcome, not "implement X component".
- [ ] DoD bullets are observable in the browser or a test runner.
- [ ] Every task lists exact files.
- [ ] Every task DoD uses checkboxes, not prose.
- [ ] Every milestone is a file in `milestones/` carrying its own goal, tasks, DoD and Verify — no milestone body in `index.md`.
- [ ] `index.md`'s milestone table has one row per milestone file and matches their frontmatter.
- [ ] Every milestone file's `## Verify` is scoped to what that milestone changed — no whole-repo gate (full suite, repo-wide lint/typecheck, aggregate `ci` target); those belong to `index.md`'s Final Verification.
- [ ] Each milestone file executable from a fresh session with only it and `index.md` as context.

## Anti-patterns (must be absent)

- [ ] No "TBD", "TODO", "implement later", "styling TBD", "handle states later".
- [ ] No task spanning unrelated concerns (component + API + state store in one row).
- [ ] No task that adds a component without also specifying its props, states, and where it mounts.
- [ ] No "match the design" without linking the source of truth (Figma, mockup, existing component).

## External references validated

- [ ] Package / library versions confirmed against registry.
- [ ] API endpoints the UI consumes are verified to exist (or the backend task creating them is a dependency).

## Frontend-specific

- [ ] Accessibility section filled in for interactive UI, or marked N/A.
- [ ] Responsive / cross-browser section filled in for layout changes, or marked N/A.
- [ ] State placement decision (local / shared / URL) is explicit for any new stateful behavior.

## CLAUDE.md impact

- [ ] Names sections to update with an owning task, or explicitly states "No CLAUDE.md changes required".
