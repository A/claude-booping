# Run the sprint, milestone by milestone

This step runs once per milestone, in `id` order; the instance's milestone is the one its `--instance` names. Provision's groups decide only how briefings are batched: a group's **first** instance composes and delegates one briefing covering that whole group, and the group's later instances ride that briefing straight to their own close.

Each milestone owns a directory `{plan-dir}/milestones/{instance}/` holding its milestone file `{instance}.md` — the contract — and, once the runner has findings for it, `feedback.md`. `{instance}` is `M{nn}-{kebab}`.

Milestones run **sequentially** — never two workers on one sprint branch, and never edit application code yourself. Don't use git worktrees.

Provision already fired the `ready-for-dev` → `in-progress` edge. On a resume that still finds the plan at `ready-for-dev`, take that edge before the first delegation; otherwise never touch it.

Milestone transitions are the `## State` section's `milestone` machine, invoked as:

```
booping playbook-transition develop {to} --state milestone --instance {instance} --workdir {plan-dir}
```

The edge's hook regenerates `index.md`'s `## Milestones` table and its `sp` — never edit either by hand.

## Delegating a group

1. Open one tracking task for the group.
2. Transition every milestone in the group onto the edge whose `when` is the group being handed to a worker.
3. Compose **one** briefing, exactly this block:

   ```markdown
   ## Task

   Implement the milestones below, in the order given, on branch `{branch}`.

   ## Inputs

   - Contract — `{plan-dir}/milestones/{instance}/{instance}.md`: one line per milestone in the group, in order.
   - Feedback — `{plan-dir}/milestones/{instance}/feedback.md`: one line per milestone, same order; read it if it exists.
   - Context — `{plan-dir}/index.md`: scope boundary, architecture and decisions.
   - Conventions — {the repo's `CLAUDE.md`, plus any convention file a milestone names}.
   - Drift — {intake's outstanding findings, or `none`}.

   ## Return

   One block per milestone, in the same order: what was done in one paragraph, the files touched, and the `## Verify` command with its verdict. Leave the work uncommitted — committing is the runner's. No diffs, no pasted code, no command logs.
   ```

   Paths only: never paste a milestone's goal, tasks, DoD or Verify text into the briefing — the worker reads its contract itself. Briefings carry no lesson paths either; the worker gets its lesson context from its own extension file.
4. Delegate the briefing to the worker agent named in [Available Agents](#available-agents) — always delegate, even for a one-line change.
5. Never resurrect a worker by ID for the next group. Each group gets a fresh agent with empty context.

## Closing a milestone

Once the briefing that covers this instance's milestone has come back, the worker has already run the milestone's `## Verify` and left its work uncommitted in the working tree. Never re-run that command, and never edit application code yourself — but the commit is yours: nothing reaches the branch that has not passed the DoD.

1. Validate the working tree against the milestone file's `## Definition of Done` — `git status --short` and `git diff` (plus `git diff --cached`) over the paths the contract names.
2. Commit the milestone in the attached repo — one commit per milestone, message format `{{ config.core.develop_playbook.git.commit_message }}`, `<agent>` being the worker that built it. Stage the contract's own paths explicitly; never `git add -A`, never a vault path, never push, never switch or create a branch, never `--amend`.
3. In the milestone file: flip each satisfied DoD checkbox `- [ ]` → `- [x]`, and each finished task row's status. Bookkeeping only — no new tasks, no rewritten ones, and never `status:`, which the machine owns.
4. Take the milestone's closing edge.
5. Commit the plan in the vault git repo: `git -C {vault} add plans/{slug}`, then `git -C {vault} commit -q -m "develop: {slug} → in-progress"`.
6. Report to the user in one paragraph — what shipped, anything deferred — before the next milestone starts.

A worker that reports its milestone green over a working tree with nothing to stage has shipped nothing: that is a failed attempt, not a closed milestone.

## When a milestone does not close

A tree that misses the DoD, a `## Verify` the worker reports red, or a green report over an empty tree goes back as a fix briefing — uncommitted, since the commit only happens on a pass. First write your findings into `feedback.md` beside the milestone file — what you checked, what was wrong, what the next attempt must do — headed by the attempt record line:

**Blocked (n/2)**: {what failed}

`n` is one more than the number of `**Blocked (` lines already in that file; that file is the only place attempts are counted.

Take the milestone's blocked edge on the record, and the edge back when the next attempt starts. Brief a **fresh** agent for the fix — the same block, the same contract path, now with the feedback path — routed to `{{ config.core.develop_playbook.fallback_agent }}` when the milestone was built by some other agent. A rejected attempt left no commit behind, so the fix carries the milestone's whole work into one closing commit — never an amend of an earlier one. After two recorded attempts on the same issue the blocker is unrecoverable: ask the user to approve the abort, then take the run machine's `in-progress` → `fail` edge. No scope additions and no runner-authored fix at any point.

## Return format

```
## Changed:

- [UPDATED] plans/{slug}/milestones/{instance}/{instance}.md — {status before} → {status after}, {n} DoD checkboxes flipped

## Notes:

- briefing: {the group this milestone's briefing covered, or that it rode an earlier group's briefing}
- commit: {sha} — {the milestone's commit message}
- verify: {the verdict the worker reported, and any fix attempts spent}
```
