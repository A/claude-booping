---
status: awaiting-prompt-confirm
reviewed_at: 20260804 17:46
fixtures_reviewed_at: 20260804 17:46
---

# present

[← index](../../index.md)

## Contract

- **Needs** —
  - the severity-classified findings, each with its file and line anchor, severity, offending
    snippet, proposed fix and the checklist item or lesson it cites — taken as they stand, never
    re-read, re-derived or re-classified
  - the review scope, for the heading the findings are posted under
- **Value** — the findings reach the human in a form they can rule on, grouped by severity so the
  serious ones are not buried among nits, and their verdict comes back: which they approved, which
  they rejected, and any correction of their own. Nothing is judged here — the step presents what
  `review` returned and collects the human's answer on it.
- **Output files** —
  - none — nothing is written to the vault or the repo
- **Harness return** — none: the step is runner-performed, so it runs in the driving conversation
  and returns no block. What it leaves behind is the human's verdict on the findings, which is what
  `resolve` consumes.
- **Review gate** —
  - none — this step *is* the human review
- **Delegation** — inline: the runner presents the findings in chat and collects the verdict there.
  That is the default and needs nothing configured. The playbook's agent table is rendered from
  config, so where a project has registered an agent for presenting a review, the step can hand the
  findings to it instead; what that agent does with them and how is carried by its own description,
  not by this playbook.

## Example artifact

The findings as posted, grouped by severity, closing on the ask:

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

Which of these should I apply?
```

The verdict that comes back, taken as the human gave it:

```markdown
Blocker on the token expiry check is right, fix that one. The 401 extraction I don't want — we
fail fast there on purpose, leave it. Both nits are fine to apply.
```

## Return Format

None — the step is runner-performed, so nothing is returned to the harness. The findings are posted
in chat and the verdict carries forward in the same conversation for `resolve` to act on.
