# Extract candidates

Extract candidates for self-learning from the retrospective in the input. **Decompose** each insight into atomic candidates — one rule per candidate — BEFORE target assignment.

Each candidate must satisfy:

- **Imperative form** — `do X` or `don't Y`. Not "X happened" or "X is good".
- **Single concern** — if you can't state the rule without "and", "plus", or `;`, split it.
- **No bare internal IDs** — when referring to an existing lesson, pair the ID with its title slug (e.g. `lesson 0004 (information-architecture-pattern)`, not just `lesson 0004`). Same for retro-internal codes; restate the underlying mechanic.
- **One sentence each in the report** — the `Rule` and `Example` cells are one sentence each. The persisted lesson file may elaborate the rule into a compact paragraph after approval.

For each candidate, pick one of the two destinations below. When the destination is a lesson, pick its `targets:` entries from the target space in the input.

The input carries the target space already fetched: every playbook, its summary, its steps, and the addressable agents. Never guess a step name that the target space does not show.

## Destinations

Every accepted learning lands in exactly one destination — no duplicates across destinations, no multi-destination rows. If a candidate would otherwise span both, decompose into two distinct rows.

- **Lesson** — a behavior change reaching playbooks, playbook steps, agents, or a skill. Concrete, short, with one example. Lands at `_lessons/{N}_{kebab}.md` in this project's vault, and carries a `targets:` list; a lesson with no valid target reaches nothing.
- **Repository CLAUDE.md** — a project fact aiding fresh-agent project understanding: layout path, CLI command, code-side convention. One-bullet additions; no paragraph rewrites. Lands at the attached repo's `CLAUDE.md`.

A lesson's `targets:` entries use exact names only, no globs: `{playbook}`, `{playbook}/{step}`, `agent:{id}`, `skill:{name}` (`playbook` is the only skill). Several entries in one list are one lesson, not a multi-destination row.

Never write `~/.claude/CLAUDE.md` or any user-level scope.

Route by **who must change behavior**, not by which playbook the finding was observed in — a finding surfaced while developing may still belong to the playbook that authors plans.

Return the candidate set as one markdown table and nothing else — columns `#`, `Rule`, `Example`, `Target` (one of: Lesson, Repository CLAUDE.md), `Lands at` (the resolved file path), `Targets` (the lesson's `targets:` wiring, `—` for a `CLAUDE.md` row) — one row per candidate, no commentary before or after the table.
