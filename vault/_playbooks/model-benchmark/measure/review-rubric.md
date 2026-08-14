# Diff review rubric

Review one diff against the plan it was written for. You judge the work, not the author: no praise, no encouragement, no restating what the diff does. A finding the diff does not support is worse than a missing finding.

## Criteria

Grade each criterion out of 5 — 5 nothing to fix, 3 works with real defects, 1 fails its own goal — with exactly one line of justification naming the evidence.

| Criterion | What earns the grade |
| --- | --- |
| Correctness | The change does what the plan asked, on the edges as well as the happy path. Wrong results, unhandled inputs the plan named, and behaviour that contradicts the plan cost the most. |
| Test quality | Tests fail when the behaviour breaks and pass when it is merely refactored: real assertions on observable outcomes, the input cases that matter covered, no assertion that only restates the implementation, no test disabled or weakened to go green. |
| Code quality | Readable at the level the surrounding code sets: names that say what they hold, no duplicated logic, no dead or unreachable branches, errors handled where they occur, no commentary that repeats the code. |
| Scope discipline | Only what the plan asked for. Unrequested refactors, drive-by renames, files outside the allowed scope, and abandoned half-changes all cost, as does a task the plan asked for and the diff never does. |

## Findings

After the grades, list the findings — each one file and line, what is wrong, and why it matters, in one or two sentences. Order them worst first. No finding for a matter of taste the criteria above do not cover, and no finding you cannot point at a line for. Nothing to report is an empty list, not a paragraph.

## Return

Return the grade table and the findings list, nothing else — no summary, no recommendation, no description of the diff.

| criterion | grade /5 | justification |
| --- | --- | --- |
| correctness | | |
| test quality | | |
| code quality | | |
| scope discipline | | |
