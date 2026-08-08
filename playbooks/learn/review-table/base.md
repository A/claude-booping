Render the review table using the format defined in [review table format](${CLAUDE_PLUGIN_ROOT}/docs/learn_review_table.md), with one added column: **Targets**.

Every row carries a Targets cell — comma-separated entries from the preamble's target space, using the four entry forms and exact names only, no globs or wildcards:

- `{playbook}` — the lesson applies to the whole playbook
- `{playbook}/{step}` — it applies to one step of it
- `agent:{id}` — it applies to one agent
- `skill:{id}` — it applies to one skill

A `lesson` row's Targets cell is written verbatim into the file's `targets:` frontmatter list, so it must be non-empty. A repo `CLAUDE.md` row carries `—`: the file path is its routing.

Use `AskUserQuestion` once to collect the user's accept / reject / add response.

Do not prompt per row. Do not inline the column-by-column documentation here — the template owns the format, the accept/reject syntax, and the user-added-row split rule.

The confirmed response is what the exit edge's first gate names — record it. Nothing is written in this step.
