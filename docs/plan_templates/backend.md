---
name: backend
description: Backend feature work — APIs, data models, services, migrations, background jobs, protocols. Stack-agnostic.
---

# Plan Body

## Context

Why this work now. Cover two beats:
- **Motivation** — why this change is needed.
- **Scope** — what this plan covers, and explicitly what it does NOT.

## Decisions

Non-obvious design choices.

## Architecture

How this change fits the existing system.

## Milestones

One `### M{nn} — {title}` block per milestone, in the format draft-plan states. Its content:

- **Tasks** — opens with a **Goal** line (one sentence: what changes in the system after this milestone) and a **Scope** line (the modules, endpoints or tables in play and the files this milestone touches), then one row per task:

  | Task | Description | Files | SP | Status |
  |------|-------------|-------|----|--------|
  | 1.1 | ... | `path/to/file.ext` | 2 | pending |
  | 1.2 | ... | `path/to/other.ext` | 1 | pending |

- **Definition of Done** — one `Task {n}.{m}` block per task, checkbox bullets only: a specific verifiable criterion, the test / verification command that proves it. A code sketch belongs here when the shape is non-obvious — interface only, `...` in method bodies:

  ```
  class NewThing:
      def method(self):
          ...
  ```

- **References** — where such files exist, 1–3 existing modules, migrations or tests whose shape this milestone copies, by path, plus the path of any schema or contract it must not go looking for.
- **Verify** — the command (or observable outcome) confirming this milestone: a targeted test path, one invocation, a diff.

## Implementation Order *(when milestones have dependencies)*

```
M1 ──┐
     ├── M3
M2 ──┘
        ↓
     M4
```

Note which milestones may run in parallel.

## Key Files Reference

Files that span multiple milestones or orient a reader.

| File | Role |
|------|------|
| `path/to/file.ext` | why it matters for this plan |

## Final Verification

- [ ] End-to-end acceptance criterion.
- [ ] Test command — all tests pass.
- [ ] Lint / typecheck command — clean.
- [ ] Any project-specific final checks.

## Testing Strategy *(required when correctness is statistical, subjective, or emergent — LLM pipelines, search/ranking, ML, heuristics, ETL over real data, performance-critical paths)*

Answer three questions:

1. **Business-goal acceptance** — how does a human confirm the feature does its job beyond "tests pass"? Name the concrete criterion.
2. **Fast debug loop** — which dataset + command lets a developer iterate on quality in seconds, not minutes? Include dataset path, command, expected runtime.
3. **User-facing validation** — which preview / dry-run / comparison view lets a non-engineer confirm output quality before ship?

For pure-deterministic work (CRUD, refactor), a single line stating "N/A — deterministic" is sufficient.

## Deployment / config impact *(when new env vars, external services, or infra changes)*

| Env var / config | docker-compose / deploy | terraform / infra | CI workflow |
|------------------|-------------------------|-------------------|-------------|
| `NEW_VAR_NAME` | present | present | present |

## Authorization / data access *(when touching endpoints, querysets, or tenant-scoped data)*

- [ ] Every queryset / query scopes to the authenticated actor (or is documented as public).
- [ ] Authorization is verified across the full API surface in scope, not just per-endpoint.
- [ ] No endpoint exposes data from other users / tenants.

## Out of scope

Explicit list of things intentionally not done in this sprint. At least one bullet; prevents "anything goes" interpretation.

## CLAUDE.md impact

Either name specific sections to update with an owning task, or state "No CLAUDE.md changes required — {one-line justification}".

| Section | Change | Owning task |
|---------|--------|-------------|
| `## {section}` | {what to add/change} | M{n}.{task} |

---

# Quality Checklist

## Frontmatter

- [ ] `title` matches the plan's H1 and `type` is the task type chosen at intake.
- [ ] `summary` is set (non-empty, single line, ≤ ~120 chars) for `feature` and `refactoring` plans.

## Content

- [ ] Context explains "why now", not just "what".
- [ ] For features and refactorings: `summary` is phrased as the user/internal-visible outcome, not engineering output.
- [ ] Definition of Done bullets are testable (verifiable by command or inspectable output).
- [ ] Decisions table lists real alternatives — no empty "Alternative considered" rows.
- [ ] Every milestone's References names 1–3 existing files to copy the shape of where such files exist, or states that none applies.
- [ ] No milestone asks for a deliverable in the worker's report — each is named as a path plus "Create" or "Append to", relative to the repo root or the plan directory.
- [ ] Every task DoD uses checkboxes, not prose.
- [ ] Code sketches use `...` in method bodies — agents implement from interfaces, not by copying literal code.

## Out of scope

- [ ] Out-of-scope section present; at least one excluded concern named.

## Backend-specific

- [ ] Authorization / data-access checks section filled in if endpoints are touched, or marked N/A with justification.
- [ ] Deployment / config impact section filled in if env vars / infra change, or marked N/A.
- [ ] Testing Strategy answered if the work is quality-dependent, or marked N/A for pure deterministic work.

## CLAUDE.md impact

- [ ] Either names the specific sections/bullets to update (with an owning task) or explicitly states "No CLAUDE.md changes required" with justification.
- [ ] If the sprint introduces a registry / builder / harness, changes a public data shape, or relocates a "how to add X" procedure, there is a concrete task for the CLAUDE.md update — not deferred to retro.
