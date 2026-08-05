---
status: awaiting-prompt-confirm
reviewed_at: 20260804 17:46
fixtures_reviewed_at: 20260804 17:46
---

# resolve

[← index](../../index.md)

## Contract

- **Needs** —
  - the human's verdict on the findings — which they approved, which they rejected, and any
    correction of their own
  - the findings as classified: severity, file-and-line anchor, offending snippet, proposed
    fix, rationale
  - for each approved fix, whether it is a trivial inline edit or not
  - the project's conventions the fixing agent must follow
- **Value** — the run's only mutation, and the only place the human's own words become code.
  The verdict arrives already collected, identical whichever surface carried the review, and
  this step only acts on it: approved trivial nits go in by hand, approved non-trivial fixes go
  out to the worker agent with the finding, its files and the proposed fix, rejected findings
  are dropped without argument — the human's call is final and never re-litigated. Findings are
  never re-presented or re-classified here. The run closes on a report of what was applied,
  what was delegated and what was left, so the user sees the whole ledger without re-reading
  the diff.
- **Output files** —
  - none — the step creates and updates no document. Its effects are edits in the repo working
    tree at the paths the approved findings anchor (trivial nits by the runner, non-trivial
    fixes by the worker agent) and the closing report in chat.
  - nothing under the vault, no review file on any route, no commit, no push, no plan-status
    move.
- **Harness return** — `## Changed:` one `[UPDATED] <repo path>` line per file edited,
  annotated with the finding it closes and who applied it (runner or worker agent); `## Notes:`
  the closing ledger — counts applied, delegated and dropped — and the standing
  `nothing committed or pushed` line; `## Questions:` only when an approved fix cannot be
  applied.
- **Review gate** —
  - none — the human's own feedback is the approval
- **Delegation** — assisted: the runner performs the step and delegates every approved
  non-trivial fix to the worker agent the preamble's agent table names.

## Example artifact

The closing report, in chat:

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

Nothing committed or pushed — the changes sit in the working tree.
```

## Return Format

```markdown
## Changed:

- [UPDATED] src/auth/session.py — NIT `session.py:88` rename, `:141` comment (runner)
- [UPDATED] src/auth/refresh.py — BLOCKER `refresh.py:52` constant-time compare (booping-developer)
- [UPDATED] src/api/routes.py — SUGGESTION `routes.py:210` 401 branch extracted (booping-developer)

## Notes:

- 2 applied by the runner, 2 delegated to `booping-developer`, 1 dropped on the user's call
- nothing committed or pushed; no plan status moved

## Questions:
```
