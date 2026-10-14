---
type: adr
title: The runner owns the milestone commit; workers never commit
summary: A worker implements its milestone, runs its Verify and leaves the work uncommitted; the runner validates the tree against the DoD and makes one scoped commit per milestone.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
values: [values/0001#proven-to-work, values/0001#stack-agnostic-core]
sources: [CHANGELOG.md, CLAUDE.md]
---

## Context

In v1.0.1 the worker implemented its milestone, ran its verification until green
and made the repo commit; develop then checked that diff against the definition of
done before moving the milestone on. A commit that failed the check could already be on
the branch, and a worker driven through a foreign harness had to handle git.

## Decision

The worker runs its milestone's `## Verify` and leaves the work uncommitted. The
runner validates the working tree against the DoD, makes the repo commit — one per
milestone, staged from the contract's own paths, never `git add -A` — flips the
checkboxes and takes the transitions. No worker of any harness touches git history.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [Runner commits](#runner-commits) | accepted | low | high | Only DoD-green state reaches the branch |
| [Worker commits](#worker-commits) | rejected | low | high | The v1.0.1 shape |

### Runner commits

Validation precedes the commit, and both belong to the runner.

- **Pros:** only DoD-green state ever reaches the branch; a worker on a foreign
  harness needs no git at all.
- **Cons:** the runner must stage exactly the contract's paths.
- **Complexity:** low.
- **Reversibility:** high.

### Worker commits

The worker commits once its Verify is green; the runner checks the diff afterwards.

- **Pros:** not named in the source.
- **Cons:** a commit can land before the DoD check rejects it; every harness needs
  git.
- **Complexity:** low.
- **Reversibility:** high.

## Consequences

- A milestone's commit names the worker that built it in the configured message
  format.
- The runner's milestone commit never pushes, switches or creates a branch, or
  amends; it never stages a vault path.
