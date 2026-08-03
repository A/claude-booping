Extract candidates for self-learning from the retrospective read at `intake`. **Decompose** each insight into atomic candidates — one rule per candidate — BEFORE target assignment.

Each candidate must satisfy:

- **Imperative form** — `do X` or `don't Y`. Not "X happened" or "X is good".
- **Single concern** — if you can't state the rule without "and", "plus", or `;`, split it.
- **No bare internal IDs** — when referring to an existing lesson, pair the ID with its title slug (e.g. `lesson 0004 (information-architecture-pattern)`, not just `lesson 0004`). Same for retro-internal codes; restate the underlying mechanic.
- **One sentence each in the report** — the review-table `Rule` and `Example` cells are one sentence each. The persisted lesson file may elaborate the rule into a compact paragraph after approval.

For each candidate, pick a target from the routing matrix in the preamble. When the target is a lesson, pick its `targets:` entries from the target space below — the routing matrix decides *which kind of file* the candidate lands in, the target space decides *what the lesson is wired to*.

Work the target space in two passes: read the table of contents, shortlist the playbooks the candidates actually touch, then run the fetch command for exactly those (one call, names joined by commas) and pick entries from what comes back. Never guess a step name that the fetched targets did not show.

Nothing is presented to the user yet — the dedup sweep runs first, and the review table is the single surface where candidates appear.

{% include "_partials/lesson_target_toc.md" %}
