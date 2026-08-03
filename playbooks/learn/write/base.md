After the table is accepted, write every accepted row in a single pass per target type. No per-edit `AskUserQuestion` calls; table acceptance is the consent.

Write paths use these templates (resolve each placeholder before writing):

- `_lessons/{N}_{kebab}.md` — one rule per file, in this project's vault. `{N}` is the next integer, computed from `ls _lessons/` highest existing prefix + 1 (`1` when the directory is empty or absent — create it); body follows the lesson body shape inlined below. The `targets:` list is the row's Targets cell verbatim, one entry per line. The `retro:` frontmatter points at the run's retrospective, `plans/{primary-slug}/retro.md`.
- `_booping/skill_{name}.md` — per-skill extension in this project's vault.
- `_booping/agent_{name}.md` — per-agent extension in this project's vault.
- Repo `CLAUDE.md` — the attached repo's `CLAUDE.md`, one-line bullet additions; no paragraph rewrites. **Never** write to the global `~/.claude/CLAUDE.md` or any user-level scope — learn only touches this project's vault and the attached repo.

An `update existing at target X` row edits the file already holding the rule in place — no fresh file at another target.

{% include "_partials/_lesson_template.j2" %}
