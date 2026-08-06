# Adopt the plan

Load the plan the preamble resolved and the repo `CLAUDE.md`.

**Validate entry status**: the plan's `status:` must match an entry transition of the run machine
(the `## State` section's table). Otherwise stop and report clearly.

When the plan entered at `awaiting-plan-review`, capture the user's approval explicitly — "looks
good" counts, silence never does. That approval is what the `awaiting-plan-review` →
`ready-for-dev` edge gates on.

## Plan-validity check

Compare the plan's `commit:` field with the repo's current HEAD, `{{ macro('core.macros.git_commit') }}`.

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