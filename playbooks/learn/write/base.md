After the table is accepted, write every accepted row in a single pass per destination. No per-edit `AskUserQuestion` calls; table acceptance is the consent.

There are exactly two destinations (resolve each placeholder before writing):

- `_lessons/{N}_{kebab}.md` — one rule per file, in this project's vault. `{N}` is the next integer, computed from `ls _lessons/` highest existing prefix + 1 (`1` when the directory is empty or absent — create it); body follows the lesson body shape inlined below. The `targets:` list is the row's Targets cell split on commas — one YAML list item per entry, never several names in one item (`- a, b` and `- a b` are both one invalid target and the lesson injects nowhere). Quote `title:` — a colon in the sentence breaks the frontmatter otherwise. The `retro:` frontmatter points at the run's retrospective, `retrospectives/{slug}.md`.
- Repo `CLAUDE.md` — the attached repo's `CLAUDE.md`, one-line bullet additions; no paragraph rewrites. **Never** write to the global `~/.claude/CLAUDE.md` or any user-level scope — learn only touches this project's vault and the attached repo.

An `update existing at target X` row edits the file already holding the rule in place — no fresh file at another target. Extend, don't rewrite: add the row's content in the shape the file already uses, touch only prose the addition makes stale (a count in the title, a sibling reference), and leave everything else — including the existing **Example** — byte-identical.

After the last file is written, render every playbook a new or updated lesson targets (`booping render-playbook {playbook}`) and read its notices: a `**Note — tell the user:** lesson … has no valid targets` line means a malformed `targets:` list — fix the file and re-render before moving on.

The retrospective is the backstory, not the lesson: however long the retro finding runs, the persisted lesson body stays a couple of sentences plus its one example. Never copy the retro's narrative, motivation, or timeline into a lesson.

{% include "_partials/_lesson_template.j2" %}
