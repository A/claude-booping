# Write accepted rows

The review table in the input is accepted — write every accepted row in a single pass per target type. Table acceptance is the consent; ask nothing further.

Write paths use these templates (resolve each placeholder before writing):

- `_lessons/{N}_{kebab}.md` — one rule per file, in this project's vault. `{N}` is the next integer, computed from `ls _lessons/` highest existing prefix + 1 (`1` when the directory is empty or absent — create it); body follows the lesson body shape below. The `targets:` list is the row's Targets cell verbatim, one entry per line. The `retro:` frontmatter points at the run's retrospective, `plans/{primary-slug}/retro.md`.
- `_booping/skill_{name}.md` — per-skill extension in this project's vault.
- `_booping/agent_{name}.md` — per-agent extension in this project's vault.
- Repo `CLAUDE.md` — the attached repo's `CLAUDE.md`, one-line bullet additions; no paragraph rewrites. **Never** write to the global `~/.claude/CLAUDE.md` or any user-level scope — learn only touches this project's vault and the attached repo.

An `update existing at target X` row edits the file already holding the rule in place — no fresh file at another target. Extend, don't rewrite: add the row's content in the shape the file already uses, touch only prose the addition makes stale (a count in the title, a sibling reference), and leave everything else — including the existing **Example** — byte-identical.

## Lesson body shape

```
---
id: {N}                                # monotonically-increasing integer; matches the filename prefix
title: {one-sentence rule as a prescriptive statement}
targets:                               # what this lesson is injected into; exact names only, no globs
  - {playbook}                         # or {playbook}/{step}, or agent:{agent-id}
retro: plans/{primary-slug}/retro.md   # the retro that surfaced this lesson
created: YYYY-MM-DD                    # date this lesson was extracted
---

{The principle, imperative form. One compact paragraph; a short bullet list is fine when the rule has named sub-checks.}

**Example**: {One concrete case that illustrates the rule — what went wrong or right, in one or two lines. No motivation paragraphs, no multi-section "how to apply", no forbidden/edge-case lists. The retro carries the backstory; link it via the retro frontmatter.}
```

The retrospective is the backstory, not the lesson: however long the retro finding runs, the persisted lesson body stays a couple of sentences plus its one example. Never copy the retro's narrative, motivation, or timeline into a lesson.

Return: a `## Changed` section listing each write as `- [CREATED|UPDATED] path — one-line note`, and nothing else.
