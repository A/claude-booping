After the table is accepted, write every accepted row in a single pass per destination. No per-edit `AskUserQuestion` calls; table acceptance is the consent.

There are exactly two destinations (resolve each placeholder before writing):

- A rule record in this project's specs tier. Run `booping specs init --tier project` first — it creates the tier when absent, and its last stdout line is the tier root. Each new record is `{root}/rule/{NNNN}-{slug}.md`, `{NNNN}` from `booping specs next rule --tier project`, run per record; the record follows the rule record shape below. The `targets:` list is the row's Targets cell split on commas — one YAML list item per entry. Quote `title:`, `summary:` and `brief:`. A re-run after a partial failure reuses the record already written for a row — same `title` in the tier — instead of taking a new number.
- Repo `CLAUDE.md` — the attached repo's `CLAUDE.md`, one-line bullet additions; no paragraph rewrites. **Never** write to the global `~/.claude/CLAUDE.md` or any user-level scope — learn only touches this project's vault, its specs tier and the attached repo.

Rows by sweep verdict:

- `update existing at rule/NNNN` — edit that record in place, no fresh record, and bump `updated_at`. Extend, don't rewrite: add the row's content in the shape the record already uses, touch only prose the addition makes stale, and leave everything else — including the existing **Example** — byte-identical.
- `update existing at _lessons/{file}` — write a new rule record carrying the lesson's content merged with the row's, then delete the lesson file. This deletion is the only write under `_lessons/`; learn never writes or edits a lesson.
- `covered` — not written.
- `conflict with {ref}`, accepted — written as a new project rule whose `## Rule` opens with a `[clarify]` sentence naming `{ref}` as the departed rule and asking the owner for an ADR recording the departure.

After the last file is written, run `booping specs check --tier project`: an error on a written record is fixed in the record and the check re-run until it reports none — never by weakening the record's content.

The retrospective is the backstory, not the rule: however long the retro finding runs, the `## Rule` body stays a couple of sentences plus its one example. Never copy the retro's narrative, motivation, or timeline into a record.

The rule record shape:
{% include "_partials/_rule_template.j2" %}
