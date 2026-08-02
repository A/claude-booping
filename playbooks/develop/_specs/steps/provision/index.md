---
status: done
agents:
  step-prompt: a57b9ff6c24e92be3
  step-spec: aa90b73e68bbb112b
  llm-tests: a2a45ebbef9def4ce
reviewed_at: 20260802 09:48
fixtures_reviewed_at: 20260802 09:52
suite_reviewed_at: 20260802 09:58
---

[← index](../../index.md)

# provision

## Contract

- **Needs** —
  - the plan's task type, title and slug
  - the plan's milestones with their story points and execution order
  - how much context consecutive milestones share — what a worker briefed on one already
    knows for the next
  - the grouping ceiling: how many consecutive milestones one briefing may cover
  - the project's branch conventions — which prefix each task type takes
  - the repo's current branch, and whether a branch for this sprint already exists
  - the drift findings intake raised, trivial patches included
- **Value** — the sprint set up in one step: a confirmed branch to commit on and the milestone
  groups every briefing in `develop-loop` will cover. The branch is the run's one stop besides
  verify's gate — the name is proposed and only created on the user's word; the groups are the
  step's own call and never put to the user. Both surfaces the step renders from are the shared
  ones — branch prefixes and the commit-message format from the branch-conventions partial, the
  grouping ceiling from the sprint-planning partial — so a project that overrides either gets
  the override here. Cheap to replay: at most the branch exists and no sprint work is committed.
- **Output files** —
  - none — the step's outputs are a repo-side effect and conversation state:
    - the sprint branch, created in the attached repo (`git switch -c {name}`) after the user
      confirmed the name, or the existing sprint branch switched onto and reused. It branches
      off the repo's **current branch** — git's own default, never the project's default branch —
      so on a repo-local vault the plan commits groom already made travel with the sprint. One
      branch per sprint; in a multi-repo project the same name is reused across repos unless the
      user asks otherwise. Nothing is created before the answer comes back.
    - the milestone groups and their order, held in conversation and carried to `develop-loop`
      in the step's return: each group is a set of consecutive milestones, grouped only where the
      shared context makes one worker cheaper than one per milestone and never over the ceiling;
      milestones that share nothing stay one per group.
    - the drift findings intake raised, restated with the groups so `develop-loop` briefs
      against them
  - the plan body is not edited here; the only write to `index.md` is the machine's own —
    **this step fires the `ready-for-dev` → `in-progress` transition at its end**, once the branch
    exists and the groups are settled (and after intake's approval edge, when the plan entered at
    `awaiting-plan-review`). The edge's `started` and `commit` stamps come with it. `develop-loop`
    keeps only an idempotent guard for a resume that finds the plan still at `ready-for-dev`.
- **Harness return** — `## Changed:` carrying the plan's `index.md` as `[UPDATED]` for the
  transition it fired, nothing else; `## Notes:` carrying the branch — its name, whether it was
  created or reused, and what it was branched off — the transition report verbatim, the group
  plan (how many briefings over how many milestones, each group's milestones and why it was
  grouped), and the outstanding drift, if any; `## Questions:` empty once the branch exists,
  carrying the branch-name proposal only on a pass that was stopped before creating it.
- **Review gate** —
  - the user confirms the branch name before the branch is created — asked through
    `AskUserQuestion`, never as chat prose; a name the user rewrites is used verbatim, and
    nothing touches git until the answer arrives
  - the milestone groups are internal — settled by the step, reported in its return, never put to
    the user for confirmation
- **Delegation** — inline: the runner renders the step and performs it itself, in the main
  context.

## Example artifact

The branch question, asked before anything is created (`AskUserQuestion`, the proposal against a
free-text alternative):

```markdown
The plan's type is `feature`, so the sprint takes the `feat/` prefix.

Proposed branch: `feat/local-vault-directories` — created from `main` (current branch).

Confirm the name, or give a different one.
```

On confirmation, in the attached repo:

```bash
git switch -c feat/local-vault-directories
```

The group plan the step settles for itself and carries to `develop-loop` — not shown to the user:

```markdown
| Group | Milestones | SP | Grouped because |
| --- | --- | --- | --- |
| 1 | M1 Marker + resolution, M2 Resolution call sites | 8 | one resolution path, same module — the second milestone is the first one's callers |
| 2 | M3 Scaffolding flag | 5 | own surface (`booping-create-project`), shares nothing with M1–M2 |
| 3 | M4 Docs + skill wiring, M5 Local-vault branch offer | 7 | both edit the same templates and the same docs page |
```

## Return Format

```markdown
## Changed:

- [UPDATED] plans/20260801-14-30_local-vault-directories/index.md — ready-for-dev → in-progress

## Notes:

- branch: `feat/local-vault-directories` created off the current branch `main`, name confirmed
  by the user
- transition: `ready-for-dev → in-progress`; frontmatter: started=20260802 10:12, commit=a1b2c3d
- groups: 3 briefings over 5 milestones (ceiling 2) — G1 M1+M2, G2 M3, G3 M4+M5
- drift: intake's two trivial patches are already in the plan; nothing outstanding

## Questions:
```

When a branch for this sprint already exists, the branch note says so instead:

```markdown
- branch: `feat/local-vault-directories` already existed and was reused — switched onto it,
  2 commits ahead of `main`
```
