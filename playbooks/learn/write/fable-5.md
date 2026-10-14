# Write accepted rows

The review table in the input is accepted — write every accepted row in a single pass per destination. Table acceptance is the consent; ask nothing further.

There are exactly two destinations (resolve each placeholder before writing):

- A rule record in this project's specs tier. Run `booping specs init --tier project` first — it creates the tier when absent, and its last stdout line is the tier root. Each new record is `{root}/rule/{NNNN}-{slug}.md`, `{NNNN}` from `booping specs next rule --tier project`, run per record; the record follows the rule record shape below. The `targets:` list is the row's Targets cell split on commas — one YAML list item per entry. Quote `title:`, `summary:` and `brief:`. A re-run after a partial failure reuses the record already written for a row — same `title` in the tier — instead of taking a new number.
- Repo `CLAUDE.md` — the attached repo's `CLAUDE.md`, one-line bullet additions; no paragraph rewrites. **Never** write to the global `~/.claude/CLAUDE.md` or any user-level scope — learn only touches this project's vault, its specs tier and the attached repo.

Rows by sweep verdict:

- `update existing at rule/NNNN` — edit that record in place, no fresh record, and bump `updated_at`. Extend, don't rewrite: add the row's content in the shape the record already uses, touch only prose the addition makes stale, and leave everything else — including the existing **Example** — byte-identical.
- `covered` — not written.
- `conflict with {ref}`, accepted — written as a new project rule whose `## Rule` opens with a `[clarify]` sentence naming `{ref}` as the departed rule and asking the owner for an ADR recording the departure.

After the last file is written, run `booping specs check --tier project`: an error on a written record is fixed in the record and the check re-run until it reports none — never by weakening the record's content.

The retrospective is the backstory, not the rule: however long the retro finding runs, the `## Rule` body stays a couple of sentences plus its one example. Never copy the retro's narrative, motivation, or timeline into a record.

## Rule record shape

```
---
type: rule
title: "{one-sentence rule as a prescriptive statement}"
summary: "{what the rule says and where it applies, one line, at most 200 characters}"
created_by: claude
created_at: {YYYY-MM-DD}                     # the run date
updated_at: {YYYY-MM-DD}                     # the run date; bumped on every in-place edit
status: accepted
targets:                                     # the row's Targets cell, one entry per item
  - {playbook}                               # or {playbook}/{step}, agent:{agent-id}, skill:{name}
brief: "{the row's Brief cell}"
sources: [{retrospective path relative to the repo root}]   # omit when the vault is outside the repo
---

## Rule

{The principle, imperative form. One compact paragraph; a short bullet list is fine when the rule has named sub-checks.}

**Example**: {One concrete case — what went wrong or right, in one or two lines.}

## Follows from

- [{value title}]({relative path to the value record}) — {vault inside the repo: the value a project or booping value names; vault outside: a fitting project-tier value}
- [Retro: {slug}]({relative path to retrospectives/{slug}.md}) — {vault inside the repo, no value names it: the retrospective}
- [clarify] Learnt from `retrospectives/{slug}.md` in the project vault, which a record outside the vault cannot link — see the [tier README](../README.md); link a value or settle the source.
  {vault outside the repo, no project-tier value fits: this exact item, the only one}
```

Return: a `## Changed` section listing each write as `- [CREATED|UPDATED|DELETED] path — one-line note`, and nothing else.
