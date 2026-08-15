---
summary: Score the branch — corpus first, mapped onto the etalon names by a case-mapping judge, then the full `bench-score report` that writes the run detail, then the two diff reviews folded into it, leaving a report with no unfilled cell and a history row in hand.
review_gate: null
---

# Measure the branch

Everything mechanical is `bench-score`'s; everything judged is a sub-agent's. Run the script from the source repo root so its default registry path resolves, or pass `--registry {vault}/benchmarks/index.md`. Each invocation takes `--benchmark {id}`, `--branch {branch}` and `--repo {workspace}` from `prepare`'s return — without `--repo` the script scores the source repo, which does not carry the branch.

## 1. Corpus, then the case mapping

Run `bench-score corpus` and keep its JSON. Its recall and gap counts are **exact case-name matches only**: a case the model wrote under a different name reads as a miss on both sides of the comparison, which is what the next sub-agent settles.

Spawn one detached case-mapping judge. Its inputs are programmatic — never a case name you typed yourself:

- the registry entry's `etalon_cases` and `gap_cases` lists;
- the corpus JSON's `unmatched_etalon` and `unmatched_branch` lists;
- the bodies of the branch cases named in `unmatched_branch`, read from the entry's `cases_dir` in the workspace, on the branch.

It returns one table and nothing else: a row per unmatched etalon name, `{etalon case} → {branch case, or none}`, with the branch case's behaviour in a clause; plus, for every `gap_cases` name, a verdict — covered by a named branch case, or not covered — since a gap case is scored on behaviour, not spelling. A branch case may map to at most one etalon name, and an etalon name to at most one branch case.

Fold the returned mapping into a copy of the corpus JSON: add the mapped hits to `aggregate.recall.matched` and `aggregate.gaps.matched`, recompute `aggregate.recall.pct` from them, and leave in `unmatched_etalon`, `unmatched_branch` and `gaps.unmatched` only what the judge mapped to nothing. Nothing else in the JSON changes, and the exact-name counts stay noted for the report.

## 2. The report

Run `bench-score report` with the mapped corpus JSON handed in through its `--corpus-json` flag, so recall and gaps score on mapped counts while every other layer is measured fresh. It writes the run detail under the registry's `runs_dir` and prints the history row on stdout — keep the row, it is `publish`'s input, and keep the detail path, it is the run artifact.

Read the detail it wrote before touching it: it names any layer that could not be measured and drops it from the composite denominator itself. Never fill such a layer in by hand.

Then append a `## Case mapping` section to the detail, below the corpus table: the judge's table verbatim, the gap verdicts, and one line giving exact-name recall against mapped recall so the difference is auditable.

## 3. The reviews

{% set review_agent = config.core.model_benchmark_playbook.review_agent -%}
Spawn {% if review_agent %}two diff reviewers in parallel, both detached — a generic `fable:medium` sub-agent and `{{ review_agent }}`{% else %}one detached diff reviewer, a generic `fable:medium` sub-agent — no review agent is configured, which is not an error{% endif %}. The briefing every reviewer gets is the same:

- `review-rubric.md` beside this step, in full — it is the contract, and both reviewers are graded against the identical text;
- the branch diff against the registry entry's `baseline`, taken in the workspace;
- the case-mapping table from step 1, so a behaviour the branch never ported surfaces as a finding rather than as a silent absence;
- the entry's `scope_allowlist`, which is what "in scope" means for this diff.

A reviewer that returns nothing usable is recorded as such in the review section with its reason; it is never re-run to get a better grade, and its grade never falls back to the other reviewer's.

Replace the detail's placeholder `## Review` table with one row per reviewer — reviewer, grade /5, findings — put the mean grade in the `review` cell of the detail's `## History row` table and of the history row you are carrying, and write the same mean to the artifact's frontmatter with `booping frontmatter-update {detail path} review={mean}`. The frontmatter `status:` is never touched by hand.

## Closing the step

With no placeholder cell left in the detail, advance the run per the `## State` section.

## Return format

```markdown
## Changed:

- [CREATED] benchmarks/runs/{run_id}-{model_slug}.md — full run detail

## Notes:

- scores: code {n}/100 · agentic {n}/100 · review {n}/5 — outcome `{outcome}`
- layers: {one clause per layer measured, and per layer bench-score dropped with its reason}
- case mapping: recall {exact}/{total} exact → {mapped}/{total} mapped; gaps {n}/{m} covered
- reviews: {one clause per reviewer — who, grade, how many findings}
- history row: {the row, verbatim}
- transition: {the transition report verbatim}
```
