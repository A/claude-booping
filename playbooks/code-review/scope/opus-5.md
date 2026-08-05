# Settle the review scope

Nothing is reviewed until the target is named and resolved into something concrete. You receive:
whether this session's `develop` run just delivered a plan — its path, title and `commit:` baseline;
the repo's recent commit history, its current branch, and whether the working tree carries
uncommitted work; and the plans listed below.

{%- set cr_status = config.core.code_review_playbook.status %}
{%- set review_candidates = 'core.code_review_playbook.queries.scope_candidates' | query %}
{%- if review_candidates %}

## Plans at the review status

Each is a candidate; its `commit:` is the diff base.

| SP | Title | Baseline |
| --- | --- | --- |
{% for plan in review_candidates -%}
| {{ plan.sp or "?" }} | [{{ plan.title | replace("|", "\\|") | replace("\n", " ") }}]({{ plan.path }}) | {{ plan.commit or "— none" }} |
{% endfor %}
{%- else %}

## Plans at the review status

_No plans sitting at `{{ cr_status }}` — that route offers nothing this run._
{%- endif %}

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
