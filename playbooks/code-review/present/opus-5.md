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
