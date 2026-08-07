A run reviews one confirmed scope end to end: `scope` settles what to look at, `review` returns
severity-classified findings from a detached pass, `present` puts them in front of the user and
collects their verdict, and `resolve` acts on it. The run is ephemeral — no workdir, no persisted
state, no review artefact — so a second look after fixes is a new run.

**Hard rules — hold for the whole run:**
- No commits, no pushes. The user owns those.
- Style the project's linter or formatter already enforces is filtered out — it is noise, not
  review signal.
- A lesson violation is always a `BLOCKER`. Never softened to `SUGGESTION`.
- No persistent report. Findings and feedback live in this conversation.
- No edit beyond a user-approved trivial nit. Every non-trivial fix routes through the worker
  agent named below.

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
| `scope` | — | Put every scope candidate on one `AskUserQuestion` call — the plan this session delivered, the latest coherent work on this branch, the plans at the review status, and a free-text route — then resolve the answer into a diff range or file list and report it back before any review work is spent. | — |
| `review` | `scope` | Perform the whole review craft over the confirmed scope in one detached pass — stack discovery, checklist selection, blast radius, every loaded checklist, and the lesson-, DoD- and intent-aware dynamic checks — returning each finding classified `BLOCKER` / `SUGGESTION` / `NIT` with its anchor, snippet, proposed fix and rationale. Nothing is written anywhere. | — |
| `present` | `review` | Post the findings `review` returned, grouped by severity, and collect the user's verdict on them — nothing is re-derived, re-classified or written here. | — |
| `resolve` | `present` | Act on the verdict already in hand — approved trivial nits applied inline, approved non-trivial fixes delegated to the worker agent with the finding and its fix, rejected findings dropped without argument — then stamp `code_review:` on the reviewed plan and close on a report of what was applied, delegated and left. | — |

## Step: Scope
# Settle the review scope

Nothing is reviewed until the target is named and resolved into something concrete. You receive:
whether this session's `develop` run just delivered a plan — its path, title and `commit:` baseline;
the repo's recent commit history, its current branch, and whether the working tree carries
uncommitted work; and the plans listed below.

## Plans at the review status

Each is a candidate; its `commit:` is the diff base.

| SP | Title | Baseline |
| --- | --- | --- |
| 5 | [Widget search](plans/19700101-widget-search/index.md) | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa |
| 2 | [Login timeout fix](plans/19700102-login-timeout/index.md) | bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb |


## The question

One `AskUserQuestion` call — single-select, free-text route on — carrying every candidate at once,
so the user names the right scope outright instead of rejecting a wrong default first:

- **This sprint's plan** — the plan `develop` delivered earlier in this session, when there is one.
  Its slug and its baseline in the description.
- **Latest work on this branch** — the latest coherent piece of work, judged off `git log --oneline`:
  the latest plan delivery on this branch, a feature's worth of commits, whatever the commits
  actually suggest. Never a hardcoded commit count. Say in the description what you judged it to be
  and how many commits it spans.
- **One option per plan in the table above** — its slug, its baseline.
- **Other** — free text: a diff range, a file list, or the working tree.

Drop a candidate that does not exist — no plan delivered this session, no plans at the review
status. Never invent one to fill the call.

## Resolve the answer

- **A plan** → `<its commit>..HEAD`. `git diff` and `git log --oneline` over the range to enumerate
  the commits and the changed files.
- **A diff range** (`HEAD~3..HEAD`, `main..feat/x`) → the range as given, same two commands.
- **A file or directory list** → those paths, no range.
- **The working tree** → `git status` plus `git diff`, staged and unstaged.

Run `git status` on every route: uncommitted work sitting outside the resolved range belongs in the
report.

## Report it back — same turn, before any review work is spent

Post the resolved target in chat as `## Review scope`, so a wrong base is caught here and not after
the review has burned on it:

```markdown
## Review scope

`{plan path}` — {the plan this session's develop run delivered / a plan queued at the review
status}. Baseline `{sha}`.
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
```

Nothing is written to the vault or the repo, and no plan-lifecycle status moves in either
direction. The confirmed scope lives in this conversation.

## A plan with no `commit:` baseline

Such a plan yields no diff range. Say so and re-ask inside this same step — another plan, or an
explicit range or file list through the free-text route. Post this in place of the report:

```markdown
`{plan path}` has no `commit:` baseline, so there is no diff range to review it from. Pick another
plan, or give me an explicit range or file list.
```

No scope is fixed until the re-ask lands, and nothing downstream runs before it.

## Return

None. This step is runner-performed: it runs in the driving conversation and returns no block to
the harness. What it leaves behind is the `## Review scope` report above and the facts `review`
reads out of it — the diff range or file list, the branch, and the plan in scope with its path when
there is one.

## Step: Review

Perform the whole review craft over the confirmed scope in one detached pass — stack discovery, checklist selection, blast radius, every loaded checklist, and the lesson-, DoD- and intent-aware dynamic checks — returning each finding classified `BLOCKER` / `SUGGESTION` / `NIT` with its anchor, snippet, proposed fix and rationale. Nothing is written anywhere.

Tell a sub-agent — model opus, effort high — to get its instructions by calling this command: `booping render-playbook code-review --step review`.

## Step: Present
Put the findings `review` returned in front of the user and collect their verdict on them.

## What you receive

- the severity-classified findings — each with its file and line anchor, its severity, the
  offending snippet, the proposed fix, and the checklist item or lesson id it cites
- the confirmed review scope, which names the post

Take the findings as they stand. Do not re-read the code, re-derive a finding, re-word a fix, or
move a finding between severities — a lesson violation stays a `BLOCKER`. Nothing is judged here.

## What you produce

Nothing is written: no file in the vault, no file in the repo. The step's output is the post in
chat and the verdict that comes back, which `resolve` acts on.

Post the findings grouped by severity — `BLOCKER`, then `SUGGESTION`, then `NIT` — each group
headed with its count, an empty group dropped entirely. One entry per finding: file and line, the
offending snippet, the proposed fix, and the item or lesson it cites. Head the post with the scope.

```markdown
## Review findings — `a1f3c02..HEAD` (plan `20260803-14-02_token-refresh`)

**BLOCKER (1)**
- `src/auth/refresh.py:52` — token compared with `==`: `if token == stored:`
  → `if secrets.compare_digest(token, stored):` — lesson `0007_constant_time_compare`

**SUGGESTION (2)**
- `src/api/routes.py:210` — the 401 branch is duplicated in three handlers; extract
  `_unauthorized()` — checklist `python:dry`
- `src/api/routes.py:33` — error envelope drops the request id — checklist `api:errors`

**NIT (2)**
- `src/auth/session.py:88` — `tmp` → `refreshed_at` — checklist `python:naming`
- `src/auth/session.py:141` — comment above `_rotate()` no longer matches the code
```

Close on the ask — which of these should be applied — in prose, in the same message, never through
`AskUserQuestion`. Then stop and wait. When `review` returned no findings, say so and say there is
nothing to rule on; the run still passes through here.

## The verdict

Read the reply as chat text and carry it forward as the user gave it: which findings they approved,
which they rejected, and any correction or finding of their own. Do not argue a rejection, do not
re-open a finding they settled, and do not start fixing anything — `resolve` owns that. Ask a
follow-up only where the reply leaves a finding genuinely unanswered.

Where the project has registered an agent for presenting a review, hand the findings to that agent
instead of posting them yourself and take the verdict back from it — what it does with them is
carried by its own description, not by this step.

## Step: Resolve
# Act on the verdict and close the run

The user's verdict is already in hand — which findings they approved, which they rejected, and any correction they gave in their own words — together with the findings as they were classified (anchor, severity, offending snippet, proposed fix, rationale) and the scope the run opened on. Act on the verdict; the findings are never re-presented, re-grouped or re-classified here, and the verdict is never asked for again or re-litigated.

## Each finding's disposition

- **Approved, trivial** — a rename, a stale comment, a small local edit the proposed fix already spells out: apply it yourself with `Edit`.
- **Approved, non-trivial** — everything else, whatever its severity: delegate it. Never apply it yourself.
- **Rejected** — drop it. No argument, no counter-proposal, no reworked version of it.
- **Corrected** — where the user described a fix different from the proposed one, their words win: carry theirs into the edit or the briefing in place of the proposed fix.

Where the verdict genuinely leaves a finding's disposition open, ask in `## Questions:` rather than guess.

## Delegating a non-trivial fix

The step stays yours; only the code change goes out. Brief the worker agent the **Available Agents** table names for applying approved non-trivial fixes — one briefing per fix, or one per file when several land in the same file. Each briefing carries the finding with its anchor, severity and offending snippet, the fix to apply (the user's correction where they gave one), the files it touches, and the project's conventions the change must follow. Take back which files it changed and what it did, and fold that into the report — do not re-read the diff to verify it.

## Stamping the reviewed plan

When a plan was in scope, stamp it once the dispositions are applied — that is what takes it out of the review queue:

```bash
booping frontmatter-update {plan path} code_review="{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"
```

The value is rendered by the command, so it is passed through verbatim, quoted exactly as above. A run opened on a bare diff range or file list has no plan and stamps nothing.

## The closing report

Post it in chat, once, as the last thing the step does — the whole ledger, so the user sees what landed without re-reading the diff. Group by disposition, count each group, name the agent the delegated fixes went to, and close on the standing line that nothing was committed or pushed:

```markdown
## Review closed — `abc1234..HEAD` (plan `20260803-14-02_token-refresh`)

**Applied here (2 nits)**
- `src/auth/session.py:88` — NIT · `tmp` renamed to `refreshed_at` (checklist `python:naming`)
- `src/auth/session.py:141` — NIT · stale comment above `_rotate()` dropped

**Delegated to `booping-developer` (1 blocker, 1 suggestion)**
- `src/auth/refresh.py:52` — BLOCKER · token compared with `==`; now
  `secrets.compare_digest` (lesson `0007_constant_time_compare`)
- `src/api/routes.py:210` — SUGGESTION · duplicated 401 branch extracted into
  `_unauthorized()`

**Dropped on your call (1)**
- `src/api/routes.py:33` — SUGGESTION · wider error envelope — you kept the current shape
```

A group with no entries is left out. The run ends here: the `code_review:` stamp is the only vault write, no review file is produced, no plan status moves, and a second look after these fixes is a new run.

## Return format

One `[UPDATED]` line per repo file edited, annotated with the finding it closes and who applied it, plus the stamped plan when one was in scope; the ledger counts and the standing no-commit line in `## Notes:`; `## Questions:` only when an approved fix cannot be applied.

```markdown
## Changed:

- [UPDATED] src/auth/session.py — NIT `session.py:88` rename, `:141` comment (runner)
- [UPDATED] src/auth/refresh.py — BLOCKER `refresh.py:52` constant-time compare (booping-developer)
- [UPDATED] src/api/routes.py — SUGGESTION `routes.py:210` 401 branch extracted (booping-developer)
- [UPDATED] plans/20260803-14-02_token-refresh/index.md — `code_review:` stamped

## Notes:

- 2 applied by the runner, 2 delegated to `booping-developer`, 1 dropped on the user's call
- nothing committed or pushed; no plan status moved

## Questions:
```
