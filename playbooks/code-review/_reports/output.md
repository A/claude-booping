A run reviews one confirmed scope end to end: `scope` settles what to look at and opens the run's artifact, `review` returns severity-classified findings from a detached pass, `present` records them and collects the user's verdict, and `resolve` acts on it and closes.

## Guidance

- Date & time: 1970-01-01 00:00
- The run's artifact is one code review per run — `codereviews/{plan-dirname}/197001010000.md` when a plan is in scope, `codereviews/{target-slug}/197001010000.md` otherwise.
- The run workdir is the **vault root**; every `booping playbook-state` / `booping playbook-transition` call passes `--target codereviews/{dir}/{ts}.md`, since the machine declares no `artifact:`.
- The artifact carries `plan:` — the reviewed plan's vault-relative path, or `null` for an ad-hoc scope. The exit hook reads it and appends the artifact to that plan's `code_reviews:` list. Plan `status:` is never touched here.

**Resuming a run** — read the frontier with `booping playbook-state code-review --workdir {vault} --target codereviews/{dir}/{ts}.md`, then re-enter at the reported status:
- `in-agent-review` — the artifact exists and the verdict is still pending: re-run `review` over the scope the artifact's `## Scope` records, and continue from `present`.
- `human-review` — the findings are on record: re-post them from the artifact's `## Findings` and collect the verdict, or continue from `resolve` when `## Verdict` is already written.

**Hard rules — hold for the whole run:**
- No hand commits, no pushes. The repo's changes stay for the user; the vault commit is the exit hook's.
- Style the project's linter or formatter already enforces is filtered out — it is noise, not review signal.
- A lesson violation is always a `BLOCKER`. Never softened to `SUGGESTION`.
- No edit beyond a user-approved trivial nit. Every non-trivial fix routes through the worker agent named below.

Eval runs are proposed, never launched — the user triggers them.


## Available Agents

Delegate heavy reads to the agents below, under the return contract the step states — the step
itself stays yours. Never delegate to an agent that is not on this list.

| agent | good for | bad for |
| --- | --- | --- |
| `booping:booping-researcher` | Blast-radius reads on large diffs (≥ ~5 files) aggregated into a compressed summary of touched modules and integration points | Single-file reads — call Read directly; Small greps or existence checks that fit in a few lines of output |
| `booping:booping-developer` | Applying user-approved non-trivial fixes surfaced by the review (BLOCKER or SUGGESTION) | Trivial inline nits — orchestrator handles those directly |



## Shared instructions

- Never write angle-bracket placeholders (`<name>`, `<path>`) into a file or a chat reply. Obsidian
  reads them as HTML tags and stops rendering the block that holds them. Write `{name}`, `{path}`.
- Never manually break markdown lines. Write each paragraph, bullet, or table row as one line and
  let the renderer wrap it — hard line breaks turn into mid-sentence breaks after any later edit.

## Playbook Steps

Execute the steps in the most effective order considering their dependencies.

| Step | Dependencies | Summary | Review gate |
| --- | --- | --- | --- |
| `scope` | — | Put every scope candidate on one `AskUserQuestion` call — the plan this session delivered, the latest coherent work on this branch, the eligible plans, and a free-text route — then resolve the answer into a diff range or file list, open the run's artifact on it, and report it back before any review work is spent. | — |
| `review` | `scope` | Perform the whole review craft over the confirmed scope in one detached pass — stack discovery, checklist selection, blast radius, every loaded checklist, and the lesson-, DoD- and intent-aware dynamic checks — returning each finding classified `BLOCKER` / `SUGGESTION` / `NIT` with its anchor, snippet, proposed fix and rationale. Nothing is written anywhere. | — |
| `present` | `review` | Write the findings `review` returned into the artifact's `## Findings`, advance the run to the human-review status, post them grouped by severity, and record the user's verdict under `## Verdict` — nothing is re-derived or re-classified here. | — |
| `resolve` | `present` | Act on the verdict already recorded — approved trivial nits applied inline, approved non-trivial fixes delegated to the worker agent with the finding and its fix, rejected findings dropped without argument — then write `## Resolution` to the artifact, close the run, and report what was applied, delegated and left. | — |

## State

Run state is persisted in artifacts under the run workdir. Only `booping playbook-transition` writes it — never hand-edit an artifact's `status`.

Read the whole run's frontier before starting or resuming:

```
booping playbook-state code-review --workdir <run workdir> --target {path}
```

### State: run

- Referenced by: outer graph
- Artifact: named per run — pass `--target {path}` (relative to the run workdir) on every call
- Initial status: `in-agent-review`
- Advance: `booping playbook-transition code-review <to> --target {path} --workdir <run workdir>`

| Status | To | When | Gates |
| --- | --- | --- | --- |
| `in-agent-review` | `human-review` | the detached review pass wrote its findings to `codereviews/{dir}/{ts}.md`, the run's `--target`, and the user's verdict is still pending | every finding carries its severity, anchor and proposed fix in the artifact |
| `human-review` | `done` | the user's verdict on every finding is resolved — applied, delegated or dropped — and recorded in the artifact | explicit user verdict captured at present — silence never counts; the artifact's `plan:` key holds the vault-relative plan path or `null`, since the hook script reads it |
| `done` | *(terminal)* | — | — |

## Step: Scope
# Settle the review scope

Nothing is reviewed until the target is named, resolved into something concrete, and opened as the run's artifact. You receive: whether this session's `develop` run just delivered a plan — its path, title and `commit:` baseline; the repo's recent commit history, its current branch, and whether the working tree carries uncommitted work; and the plans listed below.

## Plans eligible for review

Each is a candidate; its `commit:` is the diff base. **Reviews** counts the code reviews already linked on the plan — a plan that has been reviewed before is still a candidate, since a second look after fixes is a new run over the same plan.

| SP | Title | Baseline | Reviews |
| --- | --- | --- | --- |
| 5 | [Widget search](plans/19700101-widget-search/index.md) | — none | — |
| 2 | [Login timeout fix](plans/19700102-login-timeout/index.md) | — none | — |
| 3 | [Session cleanup sweep](plans/19700103-session-cleanup/index.md) | — none | 1 |


## The question

One `AskUserQuestion` call — single-select, free-text route on — carrying every candidate at once, so the user names the right scope outright instead of rejecting a wrong default first:

- **This sprint's plan** — the plan `develop` delivered earlier in this session, when there is one. Its slug and its baseline in the description.
- **Latest work on this branch** — the latest coherent piece of work, judged off `git log --oneline`: the latest plan delivery on this branch, a feature's worth of commits, whatever the commits actually suggest. Never a hardcoded commit count. Say in the description what you judged it to be and how many commits it spans.
- **One option per plan in the table above** — its slug, its baseline, and how many reviews it already carries.
- **Other** — free text: a diff range, a file list, or the working tree.

Drop a candidate that does not exist — no plan delivered this session, no plans in the table. Never invent one to fill the call.

## Resolve the answer

- **A plan** → `{its commit}..HEAD`. `git diff` and `git log --oneline` over the range to enumerate the commits and the changed files.
- **A diff range** (`HEAD~3..HEAD`, `main..feat/x`) → the range as given, same two commands.
- **A file or directory list** → those paths, no range.
- **The working tree** → `git status` plus `git diff`, staged and unstaged.

Run `git status` on every route: uncommitted work sitting outside the resolved range belongs in the report.

## Open the artifact

The run's workdir is the **vault root**, and every `booping playbook-state` / `booping playbook-transition` call passes `--target` — the machine declares no `artifact:`. Paths below are vault-relative.

- **A plan is in scope** → `codereviews/{plan-dirname}/197001010000.md`, where `{plan-dirname}` is the plan's own directory name (the parent of its `index.md`).
- **No plan** — latest commits, a range, a file list, the working tree → `codereviews/{target-slug}/197001010000.md`, where `{target-slug}` is a kebab-cased name for what was resolved: `latest-commits`, `working-tree`, or the range or path kebabbed.

Create the directory lazily (`mkdir -p`) and write the file with exactly these frontmatter keys:

- `plan:` — the plan's vault-relative path, or `null` on every route that resolved no plan. The exit hook script reads this key.
- `scope:` — one line describing the resolved diff range or target.
- `created:` — `1970-01-01 00:00`.

```yaml
---
plan: plans/202608081156_token-refresh/index.md
scope: diff a1f3c02..HEAD on feat/token-refresh — 6 commits, 12 files
created: 1970-01-01 00:00
---
```

The body opens with an H1 naming the review and a `## Scope` section holding the report below verbatim. `## Findings`, `## Verdict` and `## Resolution` are appended by `present` and `resolve` — never stubbed here.

No `status:` is hand-written. Bootstrap the run from the vault root once the file is on disk, which stamps it:

```
booping playbook-transition code-review in-agent-review --target codereviews/{dir}/197001010000.md --workdir {vault}
```

## Report it back — same turn, before any review work is spent

The same block goes into the artifact's `## Scope` and into chat, so a wrong base is caught here and not after the review has burned on it:

```markdown
## Review scope

`{plan path}` — {the plan this session's develop run delivered / a plan picked off the candidate table}. Baseline `{sha}`.
    ← both lines omitted when no plan is in scope

Diff range `{base}..HEAD` on `{branch}` — {n} commits, {n} files changed, +{x}/−{y}.
    ← or: {n} files named directly, when the scope is a file list

| Changed file | +/− |
| --- | --- |
| `{path}` | +{x}/−{y} |
| … {n} more |
    ← about ten rows, then summarise the tail

Working tree is clean — nothing uncommitted sits outside the range.
    ← or what is uncommitted and whether it is in scope

Artifact `codereviews/{dir}/{ts}.md` — opened at `in-agent-review`.
```

No plan-lifecycle status moves in either direction, here or anywhere in the run.

## A plan with no `commit:` baseline

Such a plan yields no diff range. Say so and re-ask inside this same step — another plan, or an explicit range or file list through the free-text route. No artifact is created, and nothing downstream runs, until the re-ask lands. Post this in place of the report:

```markdown
`{plan path}` has no `commit:` baseline, so there is no diff range to review it from. Pick another plan, or give me an explicit range or file list.
```

## Return

None. This step is runner-performed: it runs in the driving conversation and returns no block to the harness. What it leaves behind is the artifact at `in-agent-review`, the `## Review scope` report, and the facts `review` reads out of it — the diff range or file list, the branch, the artifact path, and the plan in scope with its path when there is one.

## Step: Review

Perform the whole review craft over the confirmed scope in one detached pass — stack discovery, checklist selection, blast radius, every loaded checklist, and the lesson-, DoD- and intent-aware dynamic checks — returning each finding classified `BLOCKER` / `SUGGESTION` / `NIT` with its anchor, snippet, proposed fix and rationale. Nothing is written anywhere.

Tell a sub-agent — model opus, effort high — to get its instructions by calling this command: `booping render-playbook code-review --step review`.

## Step: Present
# Record the findings and collect the verdict

Put the findings `review` returned in front of the user and collect their verdict on them.

## What you receive

- the severity-classified findings — each with its file and line anchor, its severity, the offending snippet, the proposed fix, and the checklist item or lesson id it cites
- the confirmed review scope and the run's artifact path under `codereviews/`

Take the findings as they stand. Do not re-read the code, re-derive a finding, re-word a fix, or move a finding between severities — a lesson violation stays a `BLOCKER`. Nothing is judged here.

The order below is fixed: write the findings, advance the run, ask, record the verdict.

## 1. Write the findings

Append `## Findings` to the artifact, grouped by severity — `BLOCKER`, then `SUGGESTION`, then `NIT` — each group headed with its count, an empty group dropped entirely. One entry per finding: file and line, the offending snippet, the proposed fix, and the item or lesson it cites. This block is written once and posted verbatim in step 3 — the artifact and the chat post never diverge.

```markdown
## Findings

**BLOCKER (1)**
- `src/auth/refresh.py:52` — token compared with `==`: `if token == stored:` → `if secrets.compare_digest(token, stored):` — lesson `0007_constant_time_compare`

**SUGGESTION (2)**
- `src/api/routes.py:210` — the 401 branch is duplicated in three handlers; extract `_unauthorized()` — checklist `python:dry`
- `src/api/routes.py:33` — error envelope drops the request id — checklist `api:errors`

**NIT (2)**
- `src/auth/session.py:88` — `tmp` → `refreshed_at` — checklist `python:naming`
- `src/auth/session.py:141` — comment above `_rotate()` no longer matches the code
```

When `review` returned no findings, the section is written as `_No findings._`.

## 2. Advance the run — before the user is asked

Once `## Findings` is on disk, transition per the `## State` section, from the vault root, passing the run's `--target`. The verdict is asked for at `human-review`, never at `in-agent-review`.

## 3. Post and ask

Post the block from step 1 in chat, headed with the scope:

```markdown
## Review findings — `a1f3c02..HEAD` (plan `202608031402_token-refresh`)
```

Close on the ask — which of these should be applied — in prose, in the same message, never through `AskUserQuestion`. Then stop and wait. With no findings, say so and say there is nothing to rule on; the run still passes through here.

Where the project has registered an agent for presenting a review, hand the findings to that agent instead of posting them yourself and take the verdict back from it — what it does with them is carried by its own description, not by this step.

## 4. Record the verdict

Read the reply as chat text and carry it forward as the user gave it. Do not argue a rejection, do not re-open a finding they settled, and do not start fixing anything — `resolve` owns that. Ask a follow-up only where the reply leaves a finding genuinely unanswered.

Append `## Verdict` to the artifact — one line per finding, its disposition in the user's own terms, their correction quoted where they gave one:

```markdown
## Verdict

- `src/auth/refresh.py:52` — BLOCKER · approved
- `src/api/routes.py:210` — SUGGESTION · approved, "extract it but keep the log line"
- `src/api/routes.py:33` — SUGGESTION · dropped — the current envelope shape stays
- `src/auth/session.py:88` — NIT · approved
- `src/auth/session.py:141` — NIT · dropped
```

`resolve` acts on this section; nothing else in the artifact is touched here, and no plan frontmatter moves.

## Step: Resolve
# Act on the verdict and close the run

The user's verdict is already recorded in the run's artifact under `## Verdict`, together with the findings as they were classified and the scope the run opened on. Act on it; the findings are never re-presented, re-grouped or re-classified here, and the verdict is never asked for again or re-litigated.

The order below is fixed: apply the dispositions, write `## Resolution`, close the run, report.

## Each finding's disposition

- **Approved, trivial** — a rename, a stale comment, a small local edit the proposed fix already spells out: apply it yourself with `Edit`.
- **Approved, non-trivial** — everything else, whatever its severity: delegate it. Never apply it yourself.
- **Rejected** — drop it. No argument, no counter-proposal, no reworked version of it.
- **Corrected** — where the user described a fix different from the proposed one, their words win: carry theirs into the edit or the briefing in place of the proposed fix.

Where the verdict genuinely leaves a finding's disposition open, ask in `## Questions:` rather than guess.

## Delegating a non-trivial fix

The step stays yours; only the code change goes out. Brief the worker agent the **Available Agents** table names for applying approved non-trivial fixes — one briefing per fix, or one per file when several land in the same file. Each briefing carries the finding with its anchor, severity and offending snippet, the fix to apply (the user's correction where they gave one), the files it touches, and the project's conventions the change must follow. Take back which files it changed and what it did, and fold that into the report — do not re-read the diff to verify it.

## Write the resolution

Once every disposition is applied, append `## Resolution` to the artifact — the ledger of what this step did, grouped the same way the closing report groups it, one line per finding with the files it touched and who applied it:

```markdown
## Resolution

**Applied here (2)**
- `src/auth/session.py:88` — NIT · `tmp` renamed to `refreshed_at`
- `src/auth/session.py:141` — NIT · stale comment above `_rotate()` dropped

**Delegated to `booping-developer` (2)**
- `src/auth/refresh.py:52` — BLOCKER · now `secrets.compare_digest` (lesson `0007_constant_time_compare`)
- `src/api/routes.py:210` — SUGGESTION · duplicated 401 branch extracted into `_unauthorized()`

**Dropped on the user's call (1)**
- `src/api/routes.py:33` — SUGGESTION · wider error envelope — the current shape stays
```

A group with no entries is left out.

## Close the run

From the vault root, passing the run's `--target`:

```
booping playbook-transition code-review done --target codereviews/{dir}/{ts}.md --workdir {vault}
```

The exit edge's hooks stamp `reviewed_at:`, append the artifact's path to the linked plan's `code_reviews:` list, and commit the vault. Nothing here hand-edits plan frontmatter, and nothing here commits — the repo's own changes stay uncommitted for the user.

## The closing report

Post it in chat, once, as the last thing the step does — the whole ledger, so the user sees what landed without re-reading the diff. Name the artifact, group by disposition, count each group, name the agent the delegated fixes went to, and close on the standing line that nothing in the repo was committed or pushed:

```markdown
## Review closed — `abc1234..HEAD` (plan `202608031402_token-refresh`)

Recorded in `codereviews/202608031402_token-refresh/202608041530.md`; the plan's `code_reviews:` list now points at it.
    ← second clause omitted when the run had no plan in scope

**Applied here (2 nits)**
- `src/auth/session.py:88` — NIT · `tmp` renamed to `refreshed_at` (checklist `python:naming`)
- `src/auth/session.py:141` — NIT · stale comment above `_rotate()` dropped

**Delegated to `booping-developer` (1 blocker, 1 suggestion)**
- `src/auth/refresh.py:52` — BLOCKER · token compared with `==`; now `secrets.compare_digest` (lesson `0007_constant_time_compare`)
- `src/api/routes.py:210` — SUGGESTION · duplicated 401 branch extracted into `_unauthorized()`

**Dropped on your call (1)**
- `src/api/routes.py:33` — SUGGESTION · wider error envelope — you kept the current shape
```

A group with no entries is left out. The run ends here: no plan status moves, and a second look after these fixes is a new run against the same plan, with its own artifact.

## Return format

One `[UPDATED]` line per repo file edited, annotated with the finding it closes and who applied it, plus the artifact; the ledger counts and the standing no-commit line in `## Notes:`; `## Questions:` only when an approved fix cannot be applied.

```markdown
## Changed:

- [UPDATED] src/auth/session.py — NIT `session.py:88` rename, `:141` comment (runner)
- [UPDATED] src/auth/refresh.py — BLOCKER `refresh.py:52` constant-time compare (booping-developer)
- [UPDATED] src/api/routes.py — SUGGESTION `routes.py:210` 401 branch extracted (booping-developer)
- [UPDATED] codereviews/202608031402_token-refresh/202608041530.md — `## Resolution`, closed at `done`

## Notes:

- 2 applied by the runner, 2 delegated to `booping-developer`, 1 dropped on the user's call
- the vault commit is the exit hook's; nothing in the repo was committed or pushed

## Questions:
```

## Replay

A replay that finds `## Resolution` already written re-fires nothing it does not need: a run still at `human-review` takes the transition alone, a run already at `done` is only re-reported, with the transition line reading `already at done — no transition taken`.
