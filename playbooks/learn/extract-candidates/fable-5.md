# Extract candidates

Extract candidates for self-learning from the retrospective in the input. **Decompose** each insight into atomic candidates — one rule per candidate — BEFORE target assignment.

Each candidate must satisfy:

- **Imperative form** — `do X` or `don't Y`. Not "X happened" or "X is good".
- **Single concern** — if you can't state the rule without "and", "plus", or `;`, split it.
- **No bare internal IDs** — when referring to an existing lesson, pair the ID with its title slug (e.g. `lesson 0004 (information-architecture-pattern)`, not just `lesson 0004`). Same for retro-internal codes; restate the underlying mechanic.
- **One sentence each in the report** — the `Rule` and `Example` cells are one sentence each. The persisted lesson file may elaborate the rule into a compact paragraph after approval.

For each candidate, pick a target from the routing matrix below. When the target is a lesson, pick its `targets:` entries from the target space in the input — the routing matrix decides *which kind of file* the candidate lands in, the target space decides *what the lesson is wired to*.

The input carries the target space already fetched: every playbook, its summary, its steps, and the addressable agents. Never guess a step name that the target space does not show.

## Routing Matrix

This matrix is the routing contract for learn candidates. Every accepted learning lands in exactly one target — no duplicates across targets, no multi-target rows.

| Target | When to use | Lands at | Examples |
|--------|-------------|----------|----------|
| **Lesson** | Behavior change reaching one or more playbooks, playbook steps, or agents — design heuristic, test discipline, IA rule. Concrete, short, with one example. Carries a `targets:` list; a lesson with no valid target reaches nothing. | `_lessons/{N}_{kebab}.md` | "Challenge code design by SOLID principles", "Use AAA in test cases", "Design skill template partials by information hierarchy" |
| **Skill extra instructions** | Tweak or extend a single skill's method (code-review / playbook). | `_booping/skill_{skill}.md` | `skill_code-review.md`, `skill_playbook.md` |
| **Agent extra instructions** | Hook a single agent's behavior. Compact list. | `_booping/agent_{full-agent-name}.md` | `agent_booping-researcher.md`, `agent_booping-developer.md` |
| **Repository CLAUDE.md** | Project-fact aiding fresh-agent project understanding — layout path, CLI command, code-side convention. One-bullet additions; no paragraph rewrites. | `{repo}/CLAUDE.md` (the attached repo's file — **never** the global `~/.claude/CLAUDE.md` or any user-level scope) | (single canonical target — no filename variants) |

If a candidate would otherwise span two targets, decompose into two distinct rows; never duplicate the same rule across targets. A lesson is the one target that carries its own routing: it lands in this project's `_lessons/` and its `targets:` list wires it to the playbooks, steps and agents it applies to — several entries in one list are one row, not a multi-target row.

Route by **who must change behavior**, not by which playbook the finding was observed in — a finding surfaced while developing may still belong to the playbook that authors plans.

Return the candidate set as one markdown table and nothing else — columns `#`, `Rule`, `Example`, `Target` (one of: Lesson, Skill extra instructions, Agent extra instructions, Repository CLAUDE.md), `Lands at` (the resolved file path), `Targets` (the lesson's `targets:` wiring, `—` for non-lesson rows) — one row per candidate, no commentary before or after the table.
