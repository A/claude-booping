# Settle the review scope

Nothing is reviewed until the target is named, resolved into something concrete, and opened as the run's artifact. You receive: whether this session's `develop` run just delivered a plan — its path, title and `commit:` baseline; the repo's recent commit history, its current branch, and whether the working tree carries uncommitted work; and the plans listed below.

{%- from "_partials/timestamps.md" import slug_ts, human_ts %}
{%- set review_candidates = 'core.code_review_playbook.queries.scope_candidates' | query %}
{%- if review_candidates %}

## Plans eligible for review

Each is a candidate; its `commit:` is the diff base. **Reviews** counts the code reviews already linked on the plan — a plan that has been reviewed before is still a candidate, since a second look after fixes is a new run over the same plan.

| SP | Title | Baseline | Reviews |
| --- | --- | --- | --- |
{% for plan in review_candidates -%}
| {{ plan.sp or "?" }} | [{{ plan.title | replace("|", "\\|") | replace("\n", " ") }}]({{ plan.path }}) | {{ plan.commit or "— none" }} | {{ plan.code_reviews | length if plan.code_reviews else "—" }} |
{% endfor %}
{%- else %}

## Plans eligible for review

_No plans in the candidate query — that route offers nothing this run._
{%- endif %}

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

- **A plan is in scope** → `codereviews/{plan-dirname}/{{ slug_ts }}.md`, where `{plan-dirname}` is the plan's own directory name (the parent of its `index.md`).
- **No plan** — latest commits, a range, a file list, the working tree → `codereviews/{target-slug}/{{ slug_ts }}.md`, where `{target-slug}` is a kebab-cased name for what was resolved: `latest-commits`, `working-tree`, or the range or path kebabbed.

Create the directory lazily (`mkdir -p`) and write the file with exactly these frontmatter keys:

- `plan:` — the plan's vault-relative path, or `null` on every route that resolved no plan. The exit hook script reads this key.
- `scope:` — one line describing the resolved diff range or target.
- `created:` — `{{ human_ts }}`.

```yaml
---
plan: plans/202608081156_token-refresh/index.md
scope: diff a1f3c02..HEAD on feat/token-refresh — 6 commits, 12 files
created: {{ human_ts }}
---
```

The body opens with an H1 naming the review and a `## Scope` section holding the report below verbatim. `## Findings`, `## Verdict` and `## Resolution` are appended by `present` and `resolve` — never stubbed here.

No `status:` is hand-written. Bootstrap the run from the vault root once the file is on disk, which stamps it:

```
booping playbook-transition code-review in-agent-review --target codereviews/{dir}/{{ slug_ts }}.md --workdir {vault}
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
