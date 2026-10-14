# Extract candidates

Extract candidates for self-learning from the retrospective in the input. **Decompose** each insight into atomic candidates — one rule per candidate — BEFORE target assignment.

Each candidate must satisfy:

- **Imperative form** — `do X` or `don't Y`. Not "X happened" or "X is good".
- **Single concern** — if you can't state the rule without "and", "plus", or `;`, split it.
- **No bare internal IDs** — when referring to an existing rule or lesson, pair the ID with its title slug (e.g. `rule/0004 (questions-settled-in-grooming)`, not just `rule/0004`). Same for retro-internal codes; restate the underlying mechanic.
- **One sentence each in the report** — the `Rule` and `Example` cells are one sentence each. The persisted rule record may elaborate the rule into a compact paragraph after approval.
- **Brief** — every rule candidate carries a `Brief`: one or two self-sufficient lines that reach the target, without restating what the agent checks or knows anyway (`src/specs/README.md`, rule frontmatter).

For each candidate, pick one of the two destinations below. When the destination is a rule, pick its `targets:` entries from the target space in the input.

The input carries the target space already fetched: every playbook, its summary, its steps, the rules already targeting it, and the addressable agents. Never guess a step name that the target space does not show.

## Destinations

Every accepted learning lands in exactly one destination — no duplicates across destinations, no multi-destination rows. If a candidate would otherwise span both, decompose into two distinct rows.

- **Rule** — a behavior change reaching playbooks, playbook steps, agents, or a skill. Concrete, short, with one example. Lands at `rule/{NNNN}-{kebab}.md` under the project specs tier root (`booping specs init --tier project` prints it), and carries a `targets:` list — its wiring — and a `brief:`, what reaches the target; a rule with no valid target reaches nothing.
- **Repository CLAUDE.md** — a project fact aiding fresh-agent project understanding: layout path, CLI command, code-side convention. One-bullet additions; no paragraph rewrites. Lands at the attached repo's `CLAUDE.md`.

A rule's `targets:` entries use exact names only, no globs: `{playbook}`, `{playbook}/{step}`, `agent:{id}`, `skill:{name}` (`playbook` is the only skill). Several entries in one list are one rule, not a multi-destination row.

Never write `~/.claude/CLAUDE.md` or any user-level scope.

Route by **who must change behavior**, not by which playbook the finding was observed in — a finding surfaced while developing may still belong to the playbook that authors plans.

Return the candidate set as one markdown table and nothing else — columns `#`, `Rule`, `Example`, `Target` (one of: Rule, Repository CLAUDE.md), `Lands at` (the resolved file path), `Targets` (the rule's `targets:` wiring, `—` for a `CLAUDE.md` row), `Brief` (the rule's `brief:`, `—` for a `CLAUDE.md` row) — one row per candidate, no commentary before or after the table.
