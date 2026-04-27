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

### M1: {Milestone name} — {SP} SP | pending

**Goal**: one sentence — what changes in the UI after this milestone.

**Verify**: exact commands (typecheck, tests, visual check) or observable outcomes.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | ... | `src/components/Foo.tsx` | 2 | pending |

#### Task 1.1 DoD

- [ ] Component renders with all documented props.
- [ ] States: loading / empty / error / success covered.
- [ ] Typecheck + test commands pass.

---

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

- [ ] Frontmatter matches [plan frontmatter](../../docs/template_plan_frontmatter.md).
- [ ] `sp` equals the sum of per-task SP across milestones.

## Content

- [ ] Context names the user-visible outcome, not "implement X component".
- [ ] DoD bullets are observable in the browser or a test runner.
- [ ] Every task lists exact files.
- [ ] Every task DoD uses checkboxes, not prose.
- [ ] Every milestone has a `Verify` step.
- [ ] Each milestone executable from a fresh session with only the plan as context.

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
