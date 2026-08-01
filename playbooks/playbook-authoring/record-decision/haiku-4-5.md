# Record a decision

The input is one or more user decisions, as short summaries, passed by the runner. Append
them to the decisions log so the run's settled choices live in one place.

## The edit to make

`<slug>/_specs/DECISIONS.md` — create the file when missing (heading `# Decisions`, nothing
else); then append one line per decision:

- `` `[YYYY-MM-DD HH:MM]` <summary> `` — the timestamp is REQUIRED: take it from
  `date -u +"%Y-%m-%d %H:%M"`, never omit or invent it.
- Summaries verbatim as given — no rewording, no merging, no filtering. Narrowing the log is
  a later, human decision.
- Append only — never edit or delete existing lines.

Invoked with no decision (bootstrap): create the file when missing, change nothing else.

## Return format

```
## Changed:
- [UPDATED] <slug>/_specs/DECISIONS.md

## Notes:
- <n> decision(s) recorded
```

On bootstrap with nothing to record:

```
## Changed:
- [CREATED] <slug>/_specs/DECISIONS.md

## Notes:
- bootstrap, nothing recorded
```
