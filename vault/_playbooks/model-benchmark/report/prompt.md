---
summary: Write the human-readable run report — a narrative telling of the whole run sourced entirely from the run detail — into the registry's `reports_dir`, as the file the history row will link.
review_gate: null
---

# Write the run report

The detail under `runs/` is machine-shaped evidence; this step writes the human telling of the same run. The reader is someone scanning the benchmarks repo's README history table who clicked a row: they get the story, the judgement, and the standing — every number still traceable.

- Path: `{bench}/{reports_dir}/{run_id}-{model_slug}.md` — same basename as the detail, sibling directory from the registry entry's `reports_dir`.
- Sources, and nothing else: the run detail, `run`'s and `measure`'s returns held in this conversation, and existing history rows for the standing section. No `bench-score` re-run, no metric computed here, no new measurement. A claim that cannot be pointed at a detail cell or an earlier row does not go in.
- The detail itself is never edited here, and its frontmatter `status:` stays the machine's.

## Shape

Frontmatter: `benchmark`, `model`, `run_id`, `date`, `outcome`, `detail` (relative link to the run detail). No `status:` — the report carries no run state.

Sections, in order — each one says what its numbers *mean*, not only what they are:

1. **Header** — title naming the model; a compact table of harness, outcome with attempts, the three scores, diff size, time, tokens, cost; a link to the run detail as the evidence behind every figure.
2. **The task** — what the benchmark asks of every model, one short paragraph, so the report stands alone.
3. **Sprint narrative** — one paragraph per milestone: attempts spent, wall clock, commit, what the worker actually did, and any judgement call, recovery, or blemish worth a sentence. This is the section the detail cannot carry; write it from what the run actually showed.
4. **Gates** — the verdict table with evidence, one line on anything that was close or noteworthy.
5. **Corpus quality** — exact-name against mapped recall, the unported behaviours named individually, four-channel rigour, wildcard discipline, any orphan case.
6. **Mutation kills** — the kill rate, what was killed cleanly in one breath, and a table of the survivors with why each lived. Tie survivors to unported behaviours when the mapping shows it.
7. **Process profile** — the per-milestone table, tool mix, and a plain statement of where every agentic deduction came from.
8. **Review** — both grades with sub-grades, the convergent findings worst first, and the pattern in one sentence.
9. **Standing** — a comparison table of the relevant sibling rows read from the README history table (same weights at other quantisations, the same model's earlier rows, nearest cloud scores), and what the comparison actually says. Rows are read, never recomputed.
10. **Footnotes** — conventions in play (a `-` cost cell, worker-usage accounting), process notes (renamed logs, harness quirks), and where the branch and workspace live.

Tone: narrated plain English over metric dumps; weaknesses named as plainly as strengths; no praise filler, no hedging. Tables carry the numbers, prose carries the meaning.

A failed run gets the same file: the narrative centers on where and how the sprint died, the footprint (diff, tokens, cost, time) is the comparison being made, and each unmeasured layer's section collapses to one line naming why it is absent — never a guessed number.

## Closing the step

No transition is taken here — the run stays at `publishing`; `publish` appends the row that links this report and takes the closing edge.

## Return format

```markdown
## Changed:

- [CREATED] benchmarks/{reports_dir}/{run_id}-{model_slug}.md — human-readable run report

## Notes:

- sections: {which sections were written, and any layer collapsed with its reason}
- standing: {which sibling rows the comparison reads against}
- sources: every figure traced to the run detail or an existing history row; nothing recomputed
```
