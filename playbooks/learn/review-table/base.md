Render the review table in the [review table format](${CLAUDE_PLUGIN_ROOT}/docs/learn_review_table.md); a row's Targets cell draws on the preamble's `## Targets`.

Use `AskUserQuestion` once to collect the user's accept / reject / add response. Do not prompt per row.

The confirmed response is what the exit edge's first gate names — record it. Nothing is written in this step.
