# Transition and commit

Everything accepted is on disk; nothing here re-drafts or re-opens the table.

## 1. Transition

Fired from the workdir, once every accepted item is written:

```bash
booping playbook-transition learn done
```

The command writes the primary plan's `status:`, then runs `close-working-set`, which moves every sibling in the retrospective's `plans:` list to `done`, re-renders the vault's `sprints.md`, and commits the plans together with the `lessons/` and `_booping/` files this run wrote. Nothing here hand-edits plan frontmatter or runs `booping vault-commit`.

```
awaiting-learning → done
script close-working-set: ok
```

That report is authoritative — do not re-read the plans to verify the moves.

## 2. Repo `CLAUDE.md` commit

If `write` also wrote to the attached repo's `CLAUDE.md`, commit that separately in the repo working tree (the transition only touches the vault, never the attached repo):

```bash
cd {repo-path}
git add CLAUDE.md
git commit -m "docs(claude-md): {short summary}"
```

## 3. Closing report

Post in chat: the plans closed with their new statuses, then a table of the items written — each with its target path and whether it was a new write or an in-place update — and the rejected-row count. No `/learn` re-offer; the working set is done.

## Replay

A replay that finds the accepted items already written re-fires nothing it does not need: a plan still at `awaiting-learning` takes the transition alone; a plan already at `done` is only re-reported, with the transition line reading `already at done — no transition taken`.
