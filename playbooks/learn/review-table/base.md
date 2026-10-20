Render the review table in the [review table format](${CLAUDE_PLUGIN_ROOT}/docs/learn_review_table.md); a row's Targets cell draws on the preamble's `## Targets`.

Close the message by asking, in prose, for the user's accept / reject / add response over the whole table — never per row — then stop and wait; the user may ask back about a row before answering.

The confirmed response is what the exit edge's first gate names — record it. Nothing is written in this step.
