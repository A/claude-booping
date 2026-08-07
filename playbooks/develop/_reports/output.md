Your goal is one finished sprint per run: every milestone `done`, every DoD checkbox `[x]`,
work committed on the sprint branch in the attached repo, the project's guardrails green, and
the plan handed off to `/playbook retro`.

**Plan resolution.** Take the plan from the invocation argument; with none given, build a
candidate table of plans in the vault currently at `ready-for-dev` or `awaiting-plan-review` and
let the user pick. The plan's own directory, `plans/{slug}/`, is the run workdir — `index.md` is
both the plan document and the machine's artifact. The machine attaches to whatever status is
already on the file; it never bootstraps or creates it.

**Hard rules — hold for the whole run:**
- The runner never writes application code. Every task is delegated to a worker agent, even a
  one-line change.
- No scope additions: the sprint delivers exactly the plan's milestones and tasks, nothing more.
- `develop-loop` works one milestone group at a time — brief a worker, close the group, then
  move to the next. Never two workers on one sprint branch at once.

Eval runs are proposed, never launched — the user triggers them.


## Available Agents

Delegate heavy reads to the agents below, under the return contract the step states — the step
itself stays yours. Never delegate to an agent that is not on this list.

| agent | good for | bad for |
| --- | --- | --- |
| `booping:booping-developer` | All coding tasks — always delegate; never edit application code from the orchestrator | — |
| `booping:booping-researcher` | Phase 0 drift spot-check: given a large set of plan-named files, determine whether actual file shape matches the plan's assumptions | Milestone-diff review — that stays in the skill; Single-file reads — call Read directly |



## Shared instructions

- Never write angle-bracket placeholders (`<name>`, `<path>`) into a file or a chat reply. Obsidian
  reads them as HTML tags and stops rendering the block that holds them. Write `{name}`, `{path}`.
- Never manually break markdown lines. Write each paragraph, bullet, or table row as one line and
  let the renderer wrap it — hard line breaks turn into mid-sentence breaks after any later edit.

## Playbook Steps

Execute the steps in the most effective order considering their dependencies.

| Step | Dependencies | Summary | Review gate |
| --- | --- | --- | --- |
| `intake` | — | Adopt the plan the preamble resolved — validate its `status:` against an entry transition, capture the user's approval when it entered at `awaiting-plan-review`, then check plan validity against the repo's current commit: cheap summary first, the plan-named diff only on the user's word; trivial drift patched in place, non-trivial drift halted back to grooming. | — |
| `provision` | `intake` | Set the sprint up — pick the branch from the plan's task type per the branch conventions, propose a kebab-case name and create it off the repo's current branch only after the user confirms; then settle the milestone groups the briefings will cover, within the configured ceiling, and fire the `ready-for-dev` → `in-progress` transition. | The user confirms the branch name before the branch is created — asked through `AskUserQuestion`, never as chat prose; a name the user rewrites is used verbatim, and nothing touches git until the answer arrives. The milestone groups are internal — settled by the step, reported in its return, never put to the user |
| `develop-loop` | `provision` | Run the sprint group by group — one briefing per group to the worker agent, one worker at a time on the sprint branch; on each report verify against the milestone's DoD and its plan-authored Verify, flip the checkboxes, task rows and milestone status, commit per milestone, refresh and commit the vault snapshot, and report what shipped before the next group. | — |
| `verify` | `develop-loop` | Run the project's guardrails over the finished sprint once — tests, lint, typecheck, formatter, whatever else must hold for a PR to open without CI failing — plus the plan's own bookkeeping, every DoD checkbox `[x]` and every milestone `done`, read off disk, and return what passed and what failed; no code-quality judgement, no fixes applied here. | — |
| `wrap-up` | `verify` | Close the run — update the documentation the sprint invalidated, make one closing commit, fire the `in-progress` → `done` transition, refresh and commit the vault snapshot, then report the sprint and offer a retro. Guardrail results and completeness arrive as verify's evidence and are never re-established here. | — |

## State

Run state is persisted in artifacts under the run workdir. Only `booping playbook-transition` writes it — never hand-edit an artifact's `status`.

Read the whole run's frontier before starting or resuming:

```
booping playbook-state develop --workdir <run workdir>
```

### State: run

- Referenced by: outer graph
- Artifact: `index.md` (relative to the run workdir)
- Initial status: `awaiting-plan-review`
- Advance: `booping playbook-transition develop <to> --workdir <run workdir>`

| Status | To | When | Gates |
| --- | --- | --- | --- |
| `awaiting-plan-review` | `ready-for-dev` | intake captured the user's explicit approval of the plan it entered on — "looks good" counts, silence never does | explicit user approval captured |
| `awaiting-plan-review` | `cancelled` | the user cancels the run | — |
| `ready-for-dev` | `in-progress` | provision created the confirmed sprint branch and settled the milestone groups; the first group is about to be delegated | the user confirmed the branch name; no unresolved non-trivial drift — that halts back to grooming instead |
| `ready-for-dev` | `cancelled` | the user cancels the run | — |
| `in-progress` | `done` | verify came back green on the project's guardrails and wrap-up made the closing commit and reported the sprint | every DoD checkbox [x] and every milestone status done; the project's guardrails and the plan's Final Verification green |
| `in-progress` | `fail` | an unrecoverable blocker at any point in the sprint, verification included, after two fix attempts on the same issue | two fix attempts documented in the plan; the user approved the abort |
| `in-progress` | `cancelled` | the user cancels the run | — |
| `done` | *(terminal)* | — | — |
| `fail` | *(terminal)* | — | — |
| `cancelled` | *(terminal)* | — | — |

## Step: Intake
# Adopt the plan

Load the plan the preamble resolved and the repo `CLAUDE.md`.

**Validate entry status**: the plan's `status:` must match an entry transition of the run machine
(the `## State` section's table). Otherwise stop and report clearly.

When the plan entered at `awaiting-plan-review`, capture the user's approval explicitly — "looks
good" counts, silence never does. That approval is what the `awaiting-plan-review` →
`ready-for-dev` edge gates on.

## Plan-validity check

Compare the plan's `commit:` field with the repo's current HEAD, `0000000000000000000000000000000000000000`.

- **Equal**: proceed.
- **Different**: run the cheap-summary commands first — do **not** load the full `git diff` into
  context until the user has opted to revalidate.

  ```bash
  git diff --name-only {plan.commit}..HEAD
  git diff --shortstat {plan.commit}..HEAD
  git log --oneline {plan.commit}..HEAD
  ```

  - If none of the changed files appear in the plan's task `Files` columns and the shortstat is
    small: surface the summary and proceed.
  - If plan-touched files changed, or the shortstat is large: ask the user verbatim — *"Want me to
    revalidate the plan against the changes?"*
    - On revalidate: load only the plan-named slice of the diff
      (`git diff {plan.commit}..HEAD -- {plan files}`).
      - **Trivial drift** (small text shifts, no semantic conflict with milestones): apply the
        in-place plan edits — a task's file list, a DoD line, a Verify command — surface the diff,
        ask explicit user approval, then proceed. Frontmatter stays untouched: `status:` is the
        machine's and the baseline re-snapshot is the `ready-for-dev` → `in-progress` edge's hook,
        fired at provision.
      - **Non-trivial drift**: halt verbatim — ask user to confirm re-validation through groom playbook process.

## The report — posted in chat

```
Plan: {path}
Status: {plan status}
Commit drift: {plan hash}..{current commit hash}
```

## Step: Provision
# Provision the sprint

Set the sprint up in one step: a confirmed branch to commit on, and the milestone groups every
briefing in `develop-loop` will cover.

You get the plan — its type, title, slug, and its milestones with story points and execution
order — the repo's current branch, and the drift findings intake raised.

## Branch

If branch wasn't explicitly defined by user, decide which branch the sprint goes on per the table above — the plan's `type` picks the prefix — and propose a kebab-case name. Ask through `AskUserQuestion`. A name the user rewrites is used verbatim, and nothing touches git until the answer arrives. Switch from the current branch to the target one after user confirmation.

In multi-repo projects, reuse the same branch name across repos unless the user asks otherwise. When a branch for this sprint already exists, switch onto it and reuse it instead of creating one.

## Git

Branches always live in the attached repo. Always ask the user before switching or creating a branch. Branch names use kebab-case (lowercase, hyphenated).

### Branches

| Branch | When |
|--------|------|
| `feat/` | feature |
| `fix/` | bug |
| `refactor/` | refactoring |
| `chore/` | anything not matching a task type; tooling, dependency bumps, formatting |


### Commit messages

Format: `<agent>: <plan title> <message>`


## Milestone groups

Group consecutive milestones into agent briefings: each briefing covers **up to 2 milestone(s)**.
Group only when the milestones share enough context that one agent handling them in sequence is
cheaper than spinning a fresh agent per milestone. Otherwise keep them one-per-briefing.

The groups are yours to settle — reported in the return, never put to the user for confirmation.
Settle them as a table you keep for the return:

| Group | Milestones | SP | Grouped because |
| --- | --- | --- | --- |

Carry intake's outstanding drift alongside them, so `develop-loop` briefs against it.

## Closing the step

With the branch created and the groups settled, advance the run per the `## State` section. Unresolved non-trivial drift halts back to grooming instead of advancing.

## Return format

```markdown
## Changed:

- [UPDATED] plans/{slug}/index.md — {status before} → {status after}

## Notes:

- branch: `{name}` created off the current branch `{base}`, name confirmed by the user
- transition: {the transition report verbatim}
- groups: {n} briefings over {m} milestones (ceiling {c}) — G1 M1+M2, G2 M3, G3 M4+M5
- drift: {what intake raised and whether anything is outstanding}

```

When a branch for this sprint already existed, the branch note says so instead:

```markdown
- branch: `{name}` already existed and was reused — switched onto it, 2 commits ahead of `{base}`
```

## Step: Develop Loop
# Run the sprint, group by group

Milestone groups run **sequentially** — never two workers on one sprint branch, and never edit
application code yourself. Don't use git worktrees.

Provision already fired the `ready-for-dev` → `in-progress` edge. On a resume that still finds the
plan at `ready-for-dev`, take that edge before the first delegation; otherwise never touch it.

For each confirmed milestone group, in order:

1. Open one tracking task for the group.
2. Compose **one** briefing covering every milestone in the group: per-milestone request, related
   files, DoD and Verify, plus the project conventions and the plan's scope boundary. Briefings
   carry no lesson paths — the worker gets its lesson context from its own extension file.
3. Delegate the briefing to the worker agent named in [Available Agents](#available-agents) —
   always delegate, even for a one-line change. 
4. Do not continue next milestone in the same agent by resurrecting it with ID. Always start a fresh agent with empty context.
5. When the worker reports done, for **each milestone** in the group:
   - Verify the output against the milestone's DoD and the resulting diff.
   - Run the milestone's plan-authored `Verify` command — the project's own guardrails all wait for
     `verify` at sprint end.
   - Flip each completed task's DoD checkboxes in the plan: `- [ ]` → `- [x]`.
   - Flip each task row in the milestone's status table: `pending` → `done`.
   - Flip the milestone status to `done`.
   - Commit in the attached repo, one commit per milestone, message format
     `<agent>: <plan title> <message>`.
5. Commit the plan in the vault git repo: `git -C {vault} add plans/{slug}`, then
   `git -C {vault} commit -q -m "develop: {slug} → in-progress"`.
6. Report group completion to the user with a one-paragraph summary (what shipped, anything
   deferred) before starting the next group.

Plan edits here are bookkeeping only: no new milestones, no rewritten tasks, and never `status:`,
which the run machine owns.

## When a milestone does not close

A failing `Verify` or a wrong diff goes back to the worker as a fix briefing, and the attempt is
recorded under the milestone in the plan:

**Blocked (1/2)**: `{verify command}` failed on {what failed}; re-briefed the worker to {fix}.

After two recorded attempts on the same issue the blocker is unrecoverable: ask the user to approve
the abort, then take the `in-progress` → `fail` edge. No scope additions and no runner-authored fix
at any point.

## Return format

```
## Changed:

- [UPDATED] plans/{slug}/index.md — {groups closed, milestones flipped}
- repo commits: {one line per milestone commit}

## Notes:

- {per group: what shipped, anything deferred}
- {the Verify verdict per milestone, and any fix attempts spent}
```

## Step: Verify

Run the project's guardrails over the finished sprint once — tests, lint, typecheck, formatter, whatever else must hold for a PR to open without CI failing — plus the plan's own bookkeeping, every DoD checkbox `[x]` and every milestone `done`, read off disk, and return what passed and what failed; no code-quality judgement, no fixes applied here.

Tell a sub-agent — model sonnet, effort medium — to get its instructions by calling this command: `booping render-playbook develop --step verify`.

## Step: Wrap Up
# Close the sprint

Verify's report arrives as evidence: which guardrails ran, each verdict, and the plan's own
bookkeeping — every DoD checkbox and every milestone status. Take it as given. Wrap-up starts
only on a green verdict — a red one goes back to the runner for fixes and a verify re-run, never
here. Nothing here re-runs a command, re-reads the plan for completeness, or asks the user
anything: once wrap-up starts it closes without stopping.

The order below is fixed.

## 1. Documentation

Documentation only becomes wrong once the whole sprint has landed, so it is written once, here,
against the finished diff. Scope is the sprint's own diff — what the work made untrue or newly
needed: README sections, `docs/` pages, a CHANGELOG when the project keeps one, the repo's own
`CLAUDE.md` when the sprint changed a convention it states. Never a documentation pass of its
own, never a scope addition. When the sprint invalidated nothing, write nothing and say so in the
report.

## 2. Closing commit

One commit in the attached repo covering the documentation edits, message format
`<agent>: <plan title> <message>`. Skip it when there is nothing to commit — the milestone
commits already landed while the loop ran.

## 3. Transition

Once the closing commit exists (or there was nothing to commit), advance the run per the `## State`
section. The plan body is not edited here — no checkbox flipping, no milestone status writing, no
new sections.

## 4. Vault commit

After the transition, so the commit carries the exit status:

```bash
git -C {vault} add plans/{slug}
git -C {vault} commit -q -m "develop: {slug} → {new status}"
```

## 5. Sprint report

Post in chat: the branch, the milestones shipped, the guardrail verdict as verify reported it, the
documentation touched, the closing commit, the plan's new status. The sprint ends here: the plan is
`done` and nothing downstream is pending. Close on the offer `/playbook retro {plan-path}` — a
retrospective is optional, runnable at any time against a `done` plan, and the user runs it, never
this step.

```markdown
**Sprint done — {plan title} ({total} SP), branch `{branch}`.**

| # | Milestone | SP | Status |
| - | --------- | -- | ------ |
| 1 | {milestone} | {sp} | done |

Guardrails: {verdict as reported} — {commands}; the plan's Final Verification passed alongside them.

Docs: {what was updated and where}; committed as `{message}`.

The plan is at `{new status}`. Optional: `/playbook retro {plan-path}`.
```

A sprint that invalidated no documentation closes on the same shape, with the docs line reading
`Docs: nothing invalidated — no documentation changes were needed.` and no closing commit.

## Return format

```markdown
## Changed:

- [UPDATED] {documentation file} — {what changed}
- [UPDATED] plans/{slug}/index.md — {status before} → {status after}
- repo commit: `{closing commit message}`

## Notes:

- docs: {what was updated and why, or that the sprint invalidated none}
- transition: {the transition report verbatim}
- vault commit: {sha}
- retro offered: `/playbook retro {plan-path}`

## Questions:
```

The documentation lines are omitted when the sprint invalidated none, and the `repo commit:` line
then reads `repo commit: none — no documentation changes to commit`. The plan line is always
present. `## Questions:` is always empty — the run is over and nothing is open.
