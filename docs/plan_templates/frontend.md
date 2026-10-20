---
name: frontend
description: Frontend feature work — UI components, state, routing, styling, accessibility. Stack-agnostic (React, Svelte, Leptos, Vue, vanilla).
---

# Plan Body

## Context

Why this work now. User-visible gap or bug, scope of this plan.

## Decisions

Non-obvious design choices: component decomposition, state location, styling approach, routing shape.

## Architecture

How the new UI fits the component tree, state flow, and data-loading boundaries. Integration points with backend APIs.

## Milestones

One `### M{nn} — {title}` block per milestone, in the format draft-plan states. Its content:

- **Tasks** — opens with a **Goal** line (one sentence: what changes in the UI after this milestone) and a **Scope** line (the components, routes and state owners in play and the files this milestone touches, plus where new components mount), then one row per task:

  | Task | Description | Files | SP | Status |
  |------|-------------|-------|----|--------|
  | 1.1 | ... | `src/components/Foo.tsx` | 2 | pending |

- **Definition of Done** — one `Task {n}.{m}` block per task, checkbox bullets only: component renders with all documented props, loading / empty / error / success states covered, typecheck + test commands pass.
- **References** — where such files exist, 1–3 existing components, stories or tests whose shape this milestone copies, by path, plus the path of any design token or API contract it must not go looking for.
- **Verify** — exact commands (scoped tests, a component's typecheck, a visual check) or observable outcomes, limited to what this milestone changed.

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

## Content

- [ ] Context names the user-visible outcome, not "implement X component".
- [ ] DoD bullets are observable in the browser or a test runner.
- [ ] Every task DoD uses checkboxes, not prose.
- [ ] Every milestone's References names 1–3 existing files to copy the shape of where such files exist, or states that none applies.
- [ ] No milestone asks for a deliverable in the worker's report — each is named as a path plus "Create" or "Append to", relative to the repo root or the plan directory.

## Frontend-specific

- [ ] Accessibility section filled in for interactive UI, or marked N/A.
- [ ] Responsive / cross-browser section filled in for layout changes, or marked N/A.
- [ ] State placement decision (local / shared / URL) is explicit for any new stateful behavior.

## CLAUDE.md impact

- [ ] Names sections to update with an owning task, or explicitly states "No CLAUDE.md changes required".
