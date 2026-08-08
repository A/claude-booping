Playbook `mod-review`, target step `compose`. The confirmed spec of the target step:

```markdown
---
reviewed_at: 20260730 09:00
---

# compose

[← index](../../index.md)

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

## Example artifact

    # Review — small-module

    ## Findings

    - `auth.py:7` — `refresh` extends expiry with no cap; a token can be refreshed forever.
      Fix: reject refresh once `expires_at - issued_at` exceeds the session ceiling.

    ## Verdict

    REQUEST CHANGES — 1 finding, 1 blocking.
```
