## Return contract

The reply to the harness is the return block alone — the sections your Return format names,
nothing before the first heading, no prose outside them. The return is the step's only
channel to the runner and the user: report issues, raise requests and surface blockers here,
never as chatter around the block.

Section vocabulary:

- `## Changed:` — one `- [CREATED|UPDATED] <path>` line per file written: `[CREATED]` when
  the file did not exist, `[UPDATED]` otherwise. Every file touched is listed, nothing else
  is. A step's Return format may extend an entry with a short annotation after the path.
- `## Notes:` — reports addressed to the runner: counts, proposed commands, and
  `decision: <summary>` lines for items the user settled (the runner records them).
- `## Questions:` — the channel to the user: numbered, each answerable in one line, each
  naming what blocks it. Never ask what the inputs already answer.
- `## Next:` — a command the harness must run before re-invoking.

Use exactly the sections your Return format shows. A section with nothing to say stays
empty — never a `(none)` placeholder.
