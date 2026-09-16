---
name: backend
description: Backend feature work — APIs, data models, services, migrations, background jobs, protocols. Stack-agnostic.
---

# Plan Body

## Context

Why this work now. Cover three beats:
- **Current state** — what exists today, what's missing or broken.
- **Motivation** — why this change is needed.
- **Scope** — what this plan covers, and explicitly what it does NOT.

## Decisions

Non-obvious design choices. One bullet per decision: **topic**, the decision, and a one-sentence justification.

- **{Topic}**: {decision} — {why}

## Architecture

How this change fits the existing system. Integration points. Reference concrete files and functions. One diagram when the flow is non-trivial.

## Milestones

Generated table — one row per milestone file, projected with `core.plans.milestones.table_columns` by `booping query`. Derived output: no hand-written rows, no milestone bodies in this file.

## Milestone files

One file per milestone directory under the plan directory's `milestones/`, named after that directory and seeded by `booping scaffold core.groom_playbook.milestone_scaffold` — the seed owns the file's frontmatter keys and its required headings. Write the body into that skeleton:

- **Goal** — one sentence directly under the H1: what changes in the system after this milestone.
- **Scope** — the modules, endpoints or tables in play and the files this milestone touches, so it executes without reading another milestone.
- `## Tasks` — one row per task:

  | Task | Description | Files | SP | Status |
  |------|-------------|-------|----|--------|
  | 1.1 | ... | `path/to/file.ext` | 2 | pending |
  | 1.2 | ... | `path/to/other.ext` | 1 | pending |

- `## Definition of Done` — one `### Task {n}.{m}` block per task, checkbox bullets only: a specific verifiable criterion, the test / verification command that proves it. A code sketch belongs here when the shape is non-obvious — interface only, `...` in method bodies:

  ```
  class NewThing:
      def method(self):
          ...
  ```

- `## References` — where such files exist, 1–3 existing modules, migrations or tests whose shape this milestone copies, by path, plus the path of any schema or contract it must not go looking for.
- `## Verify` — exact commands (or observable outcomes) confirming this milestone: a targeted test path, one invocation, a diff. Scoped to what this milestone changed — whole-repo gates (full test suite, repo-wide lint/typecheck, an aggregate `ci` target) run once in `index.md`'s Final Verification, never per milestone.

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

Verify before leaving `in-spec`. Every item must be satisfiable by reading the plan directory alone.

## Frontmatter

- [ ] `title` matches the plan's H1 and `type` is the task type chosen at intake.
- [ ] `sp` equals the sum of the milestone files' `sp`.
- [ ] `summary` is set (non-empty, single line, ≤ ~120 chars) for `feature` and `refactoring` plans.

## Content

- [ ] Context explains "why now", not just "what".
- [ ] For features and refactorings: `summary` is phrased as the user/internal-visible outcome, not engineering output.
- [ ] Definition of Done bullets are testable (verifiable by command or inspectable output).
- [ ] Decisions table lists real alternatives — no empty "Alternative considered" rows.
- [ ] Every milestone is a file in `milestones/` carrying its own goal, tasks, DoD and Verify — no milestone body in `index.md`.
- [ ] `index.md`'s milestone table has one row per milestone file and matches their frontmatter.
- [ ] Every milestone file's `## Verify` is a command or verifiable outcome scoped to what that milestone changed — no whole-repo gate (full suite, repo-wide lint/typecheck, aggregate `ci` target); those belong to `index.md`'s Final Verification.
- [ ] Every milestone file's `## References` names 1–3 existing files to copy the shape of where such files exist, or states that none applies.
- [ ] No milestone's Scope or Tasks offers two ways to do the same thing ("by hand or via X").
- [ ] No milestone asks for a deliverable in the worker's report — each is named as a path plus "Create" or "Append to", relative to the repo root or the plan directory.
- [ ] Every task lists exact file paths, not "related files" or "somewhere in X".
- [ ] Every task DoD uses checkboxes, not prose.
- [ ] Code sketches use `...` in method bodies — agents implement from interfaces, not by copying literal code.

## Anti-patterns (must be absent)

- [ ] No "TBD", "TODO", "implement later", "details to follow".
- [ ] No "Similar to Task N" without specifying what's similar.
- [ ] No "handle edge cases", "add error handling", "clean up" as standalone tasks.
- [ ] No "either X or Y" unresolved — pick one, justify in Decisions.
- [ ] No task spanning unrelated concerns (model + API + frontend in one row).
- [ ] No milestone that requires reading more than its own file and `index.md` to execute.

## External references validated

- [ ] Package / image / crate versions confirmed against official registries.
- [ ] Third-party API endpoints and flags validated against current docs.
- [ ] No assumed external reference without a verification note.

## Out of scope + coverage

- [ ] Out-of-scope section present; at least one excluded concern named.
- [ ] Every requirement in the user's request maps to at least one task, or is explicitly deferred in Out of scope with justification.

## Consistency

- [ ] Function / class names used in one task match their definition in another.
- [ ] File paths are consistent across tasks.
- [ ] Data structures (schemas, models) match between producer and consumer tasks.

## Backend-specific

- [ ] New data persistence (migration, schema change, new index) is called out explicitly and paired with a rollback note.
- [ ] Authorization / data-access checks section filled in if endpoints are touched, or marked N/A with justification.
- [ ] Deployment / config impact section filled in if env vars / infra change, or marked N/A.
- [ ] Testing Strategy answered if the work is quality-dependent, or marked N/A for pure deterministic work.

## CLAUDE.md impact

- [ ] Either names the specific sections/bullets to update (with an owning task) or explicitly states "No CLAUDE.md changes required" with justification.
- [ ] If the sprint introduces a registry / builder / harness, changes a public data shape, or relocates a "how to add X" procedure, there is a concrete task for the CLAUDE.md update — not deferred to retro.
