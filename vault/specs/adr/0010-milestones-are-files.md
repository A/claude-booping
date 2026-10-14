---
type: adr
title: A milestone is a file handed to the worker by path
summary: Each milestone is its own file in its own directory with status and feedback beside it; develop hands a worker that file's path, never a slice of the plan body.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
values: [value/0002, value/0003, value/0007]
sources: [CHANGELOG.md, CLAUDE.md]
---

## Context

Milestones were sections of the plan body; develop briefed a worker from the plan.
A stopped sprint had no per-milestone progress to resume from, and a rejected
attempt left no durable record of what was wrong. The plan's milestone table and
story-point total were kept by hand.

## Decision

Each milestone is a directory `milestones/M{nn}-{kebab}/` holding the milestone
file named after it — frontmatter `id`, `title`, `sp`, `status`, `plan`, plus tasks,
DoD, Verify and References. The file is the contract handed to a worker by path;
`index.md` is context only. Milestone `status:` is develop's per-instance run state
(`pending` → `in-progress` → `done`, `blocked` off in-progress), so a stopped sprint
resumes at the first milestone that is not done. A rejected attempt writes
`feedback.md` beside the file — the only place attempts are counted. `index.md`'s
milestone table and `sp` are generated from the files.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [Milestone files](#milestone-files) | accepted | medium | low | Contract by path; per-milestone resume |
| [Milestones inside the plan body](#milestones-inside-the-plan-body) | rejected | low | medium | Worker gets a slice; no per-milestone state |

### Milestone files

One file per milestone, with sidecars in its directory.

- **Pros:** the worker reads only its contract; status and attempts survive the
  session; the table and SP total cannot drift from the files.
- **Cons:** plans groomed before the change have no milestone files and must be
  re-groomed or finished first.
- **Complexity:** medium.
- **Reversibility:** low.

### Milestones inside the plan body

Milestones are sections of `index.md`; the runner cuts the relevant slice into the
briefing.

- **Pros:** one file per plan.
- **Cons:** no per-milestone status to resume from; the hand-kept table and SP total
  can disagree with the sections.
- **Complexity:** low.
- **Reversibility:** medium.

## Consequences

- Every milestone edge runs the `refresh-milestone-table` hook.
- The `core.plans.milestones.glob` matches the milestone file inside each directory,
  never a sidecar beside it.
