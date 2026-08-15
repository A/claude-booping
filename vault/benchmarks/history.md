# Benchmark history

**The task**: a fixed three-milestone refactoring sprint — migrate the `frontmatter-update` command's unit tests to a txtar e2e corpus (plan `202608121417_frontmatter-update-e2e-migration`).

**The method**: every model runs the same groomed plan from the same baseline commit (`a025189`), in its own throwaway clone on its own `bench/{model_slug}` branch. The develop playbook drives the sprint; every line of code is written by the worker agent pinned to the model under test, with review gates auto-answered and no human in the loop. Two failed attempts on a milestone end the run as `fail@Mnn`; a failed run is not scored on its partial work — `code`, `agentic` and `review` stay `-`, the row carries only the run's footprint: `diff`, `tokens`, `cost`, `time`. One row per run, appended by the `model-benchmark` playbook's publish step; every number is computed by `bench-score` and audited in the linked run detail.

| date       | model                             | outcome       | att   | code | agentic | review | diff | tokens | cost  | time     | run                                                                               |
| ---------- | --------------------------------- | ------------- | ----- | ---- | ------- | ------ | ---- | ------ | ----- | -------- | --------------------------------------------------------------------------------- |
| 2026-08-14 | `google/gemma-4-31b-it`           | pass          | 1/1/1 | 86.0 | 80.0    | 2.6    | 1498 | 3.6M   | $0.37 | 21m38s   | [20260814-173237](runs/20260814-173237-google-gemma-4-31b-it.md)                  |
| 2026-08-14 | `meta/muse-glimmer-30b`           | fail@M01 [^1] | 2     | -    | -       | -      | 33   | 391.6k | $0.30 | 5m51s    | [20260814-183901](runs/20260814-183901-meta-muse-glimmer-30b.md)                  |
| 2026-08-14 | `deepseek/deepseek-v4-flash-0731` | fail@M01      | 2     | -    | -       | -      | 38   | 1.4M   | $0.06 | 22m51s   | [20260814-190948](runs/20260814-190948-deepseek-deepseek-v4-flash-0731.md)        |
| 2026-08-14 | `x-ai/grok-4.6`                   | pass          | 1/1/1 | 91.3 | 80.0    | 3.1    | 1634 | 4.9M   | $3.68 | 46m23s   | [20260814-195257](runs/20260814-195257-x-ai-grok-4-6.md)                          |
| 2026-08-14 | `claude-opus-5` [^2]              | pass          | 1/1/1 | 91.2 | 90.0    | 4.63   | 1832 | 5.1M   | n/a   | 13m19s   | [20260814-210820](runs/20260814-210820-claude-opus-5-medium-booping-developer.md) |
| 2026-08-14 | `google/gemini-3.7-flash`         | pass          | 1/1/1 | 76.7 | 80.0    | 2.75   | 1564 | 9.4M   | $1.13 | 21m45s   | [20260814-211700](runs/20260814-211700-google-gemini-3-7-flash.md)                |
| 2026-08-14 | `qwen/qwen3.6-27b`                | pass          | 2/1/1 | 87.4 | 63.0    | 3.25   | 1514 | 5.4M   | $2.54 | 29m13s   | [20260814-211257](runs/20260814-211257-qwen-qwen3-6-27b.md)                       |
| 2026-08-14 | `z-ai/glm-4.5-air`                | pass          | 2/2/2 | 65.4 | 40.0    | 1.63   | 1680 | 12.5M  | $1.02 | 40m23s   | [20260814-211226](runs/20260814-211226-z-ai-glm-4-5-air.md)                       |
| 2026-08-14 | `Qwen3.6-27B-Q6` [^3]             | pass          | 2/1/1 | 76.6 | 65.0    | 3.0    | 1618 | 252.8k | -     | 32m30s   | [20260814-233230](runs/20260814-233230-qwen3-6-27b-q6.md)                         |
| 2026-08-14 | `poolside/laguna-s-2.1:free`      | pass          | 2/1/1 | 78.5 | 68.0    | 3.5    | 1524 | 12.5M  | $0.00 | 2h41m09s | [20260814-230156](runs/20260814-230156-poolside-laguna-s-2-1-free.md)             |
| 2026-08-15 | `Qwen3.8-27B` [^4]                | pass          | 1/1/2 | 90.1 | 80.0    | 3.0    | 1804 | 557.6k | -     | 4h56m20s | [20260815-012945](runs/20260815-012945-qwen3-8-27b.md)                            |

Columns:

- `date` — run date
- `model` — model id
- `outcome` — `pass`, or `fail@Mnn` naming the milestone the run died on
- `att` — attempts spent per milestone
- `code` — code-quality composite, %, grading the artifact: CI/scope/determinism gates plus corpus quality against the frozen etalon and mutation set
- `agentic` — process composite, %, read from the worker's tool logs: attempts, rebaselines, tool discipline, churn
- `review` — mean grade on a 1 to 5 scale from independent diff reviewers — isolated sub-agents running OpenAI Sol and Anthropic Fable — scoring the branch against a shared rubric
- `diff` — lines changed
- `tokens` — total in+out
- `cost` — USD from OpenRouter
- `time` — sprint duration
- `run` — link to the detail report

[^1]: Both M01 attempts were terminated by an OpenRouter `400 Provider returned error`, not by the model; the `deaths` detector does not recognise a provider abort, so `agentic` carries no death penalty. Not a clean read on the model — re-run to score it.

[^2]: Not an OpenRouter run. Every milestone went to the in-process `booping:booping-developer` sub-agent — Claude Code's own harness, `claude-opus-5` at effort `medium`, on subscription auth — so this row measures a harness-and-model pair, not a model behind `openrouter-developer`. `cost` is `n/a` because subscription auth emits no per-generation billing record; `tokens` are summed from the sub-agent transcripts rather than from OpenRouter, prompt including cache reads. Every other layer is the registry's standard run. See the detail's **Harness deviation** section.

[^3]: Not an OpenRouter run. Every milestone went to the `llama-developer` agent driving a headless Claude Code session against the local llama-swap box — `Qwen3.6-27B` at Q6_K_XL quantisation on llama.cpp — so this row measures a local deployment, not the hosted model behind `openrouter-developer`. `cost` is Claude Code's own pricing estimate (`ndjson-fallback`), not billing — the box costs electricity; `tokens` are native prompt+completion from the worker logs, cache reads excluded. The run was launched to benchmark `Qwen3.8-27B`, but the runner's model pin never reached the worker and the box served its default; the row is published under the model that actually ran. Every other layer is the registry's standard run.

[^4]: Not an OpenRouter run. Every milestone went to the `llama-developer` agent driving a headless Claude Code session against the local llama-swap box — `Qwen3.8-27B` on llama.cpp — so this row measures a local deployment, not a hosted model behind `openrouter-developer`. Unlike the earlier `Qwen3.6-27B-Q6` row, the model pin reached the worker: every attempt log's session header names `Qwen3.8-27B`. `cost` is `-` because the box bills nothing; the detail's cost table carries Claude Code's own pricing estimate (`ndjson-fallback`, $11.54), not billing. `tokens` are native prompt+completion from the worker logs, cache reads excluded. M03's first attempt died on an API request timeout after ~125 min of context reading with no work landed — an infra failure charged to the run as a retry, and most of the row's 4h56m wall clock. Every other layer is the registry's standard run.
