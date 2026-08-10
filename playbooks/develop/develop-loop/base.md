# Run the sprint, milestone by milestone

This step runs once per milestone file, in `id` order; the instance's milestone is the one its `--instance` names. Provision's groups decide only how briefings are batched: a group's **first** instance composes and delegates one briefing covering that whole group, and the group's later instances ride that briefing straight to their own close.

Milestones run **sequentially** — never two workers on one sprint branch, and never edit application code yourself. Don't use git worktrees.

Provision already fired the `ready-for-dev` → `in-progress` edge. On a resume that still finds the plan at `ready-for-dev`, take that edge before the first delegation; otherwise never touch it.

Milestone transitions are the `## State` section's `milestone` machine, invoked as:

```
booping playbook-transition develop {to} --state milestone --instance {nn}-{kebab} --workdir {plan-dir}
```

`{nn}-{kebab}` is the milestone file's name without `.md`. The edge's hook regenerates `index.md`'s `## Milestones` table and its `sp` — never edit either by hand.

## Delegating a group

1. Open one tracking task for the group.
2. Transition every milestone in the group onto the edge whose `when` is the group being handed to a worker.
3. Compose **one** briefing, exactly this block:

   ```markdown
   ## Task

   Implement the milestones below, in the order given, on branch `{branch}`.

   ## Inputs

   - Contract — `{plan-dir}/milestones/{nn}-{kebab}.md`: one line per milestone in the group, in order.
   - Context — `{plan-dir}/index.md`: scope boundary, architecture and decisions.
   - Conventions — {the repo's `CLAUDE.md`, plus any convention file a milestone names}.
   - Drift — {intake's outstanding findings, or `none`}.

   ## Return

   One block per milestone, in the same order: what was done in one paragraph, then the files touched. No diffs, no pasted code, no command logs.
   ```

   Paths only: never paste a milestone's goal, tasks, DoD or Verify text into the briefing — the worker reads its contract itself. Briefings carry no lesson paths either; the worker gets its lesson context from its own extension file.
4. Delegate the briefing to the worker agent named in [Available Agents](#available-agents) — always delegate, even for a one-line change.
5. Never resurrect a worker by ID for the next group. Each group gets a fresh agent with empty context.

## Closing a milestone

Once the briefing that covers this instance's milestone has come back:

1. Verify the diff against the milestone file's `## Definition of Done`.
2. Run the milestone file's `## Verify` command — the project's own guardrails all wait for `verify` at sprint end.
3. In the milestone file: flip each satisfied DoD checkbox `- [ ]` → `- [x]`, and each finished task row's status. Bookkeeping only — no new tasks, no rewritten ones, and never `status:`, which the machine owns.
4. Take the milestone's closing edge.
5. Commit in the attached repo, one commit per milestone, message format `{{ config.core.develop_playbook.git.commit_message }}`.
6. Commit the plan in the vault git repo: `git -C {vault} add plans/{slug}`, then `git -C {vault} commit -q -m "develop: {slug} → in-progress"`.
7. Report to the user in one paragraph — what shipped, anything deferred — before the next milestone starts.

## When a milestone does not close

A failing `Verify` or a wrong diff goes back to the worker as a fix briefing — the same block, the same contract path — and the attempt is recorded under the milestone file's `## Notes`:

**Blocked (1/2)**: `{verify command}` failed on {what failed}; re-briefed the worker to {fix}.

Take the milestone's blocked edge on the record, and the edge back when the next attempt starts. After two recorded attempts on the same issue the blocker is unrecoverable: ask the user to approve the abort, then take the run machine's `in-progress` → `fail` edge. No scope additions and no runner-authored fix at any point.

## Return format

```
## Changed:

- [UPDATED] plans/{slug}/milestones/{nn}-{kebab}.md — {status before} → {status after}, {n} DoD checkboxes flipped
- repo commit: {the milestone's commit message}

## Notes:

- briefing: {the group this milestone's briefing covered, or that it rode an earlier group's briefing}
- verify: {the milestone's Verify verdict, and any fix attempts spent}
```
