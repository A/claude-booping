# Transition and commit

Everything accepted is on disk; nothing here re-drafts or re-opens the table.

## 1. Transition

Once every accepted item is written, advance the run per the `## State` section, from the workdir. The exit edge's hooks carry the sibling plans and commit them together with the `_lessons/` and `_booping/` files this run wrote; nothing here hand-edits plan frontmatter.

## 2. Repo `CLAUDE.md` commit

If `write` also wrote to the attached repo's `CLAUDE.md`, commit that separately in the repo working tree (the transition only touches the vault, never the attached repo):

```bash
cd {repo-path}
git add CLAUDE.md
git commit -m "docs(claude-md): {short summary}"
```

## 3. Closing report

Post in chat: the plans closed with their new statuses, then a table of the items written — each with its target path and whether it was a new write or an in-place update — and the rejected-row count. No `/playbook learn` re-offer; the working set is done.

## Replay

A replay that finds the accepted items already written re-fires nothing it does not need: a plan still at the entry status takes the transition alone; a plan already past it is only re-reported, with the transition line reading `already at {status} — no transition taken`.
