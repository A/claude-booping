# Benchmark history

One row per benchmark run, appended by the `model-benchmark` playbook's publish step. Every number here is computed by `bench-score` and audited in the linked run detail.

Columns: `date` run date · `model` OpenRouter model id · `outcome` `pass` or `fail@Mnn` · `att` attempts per milestone · `code` code-quality composite /100 · `agentic` process composite /100 · `review` mean diff-review grade /5 · `diff` lines changed · `tokens` total in+out · `cost` USD from OpenRouter · `wall` sprint duration · `run` link to the detail report.

| date | model | outcome | att | code | agentic | review | diff | tokens | cost | wall | run |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-08-14 | `google/gemma-4-31b-it` | pass | 1/1/1 | 86.0 | 80.0 | 2.6 | 1498 | 3.6M | $0.37 | 21m38s | [20260814-173237](runs/20260814-173237-google-gemma-4-31b-it.md) |
| 2026-08-14 | `meta/muse-glimmer-30b` | fail@M01 | 2 | 65.0 | 70.0 | 1.75 | 33 | 391.6k | $4.05 | 5m51s | [20260814-183901](runs/20260814-183901-meta-muse-glimmer-30b.md) |
