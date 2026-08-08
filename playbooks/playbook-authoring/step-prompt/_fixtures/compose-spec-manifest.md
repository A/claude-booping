Target model: `opus-5:medium`.

The confirmed spec of the target step:

```markdown
---
reviewed_at: 20260730 09:00
---

# compose

## Contract

- **Needs** —
  - the module files under review
  - the sweep findings, one line each
- **Value** — one review report the user signs off: every genuine finding, each with a fix
  sketch naming the concrete change.
- **Output files** —
  - `[CREATED] _review/review.md`
- **Harness return** — `## Changed:` list; `## Questions:` empty unless a finding cannot be
  judged from the module alone.
- **Review gate** —
  - the user confirms the findings before anything is filed
- **Delegation** — detached, `opus-5:medium`

## Example artifact

    # Review — small-module

    ## Findings

    - `auth.py:7` — `refresh` extends expiry with no cap; a token can be refreshed forever.
      Fix: reject refresh once `expires_at - issued_at` exceeds the session ceiling.

    ## Verdict

    REQUEST CHANGES — 1 finding, 1 blocking.
```

The confirmed manifest:

```markdown
---
name: mod-review
title: Module Review
summary: Review a module file by file and compose one signed-off report.
jinja: true
trigger: reviewing a module; auditing a directory of code into a report
graph:
  sweep: []
  compose: [sweep]
---

# Module Review

Your goal is one confirmed review report per module. `sweep` works per file — one sub-agent
per file, spawned in a single message, each given its subject as a **Target: <file>** line.

Eval runs are proposed, never launched — the user triggers them.
```
