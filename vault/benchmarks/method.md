# Benchmark method

How a row in [history.md](history.md) is produced, and what each of its columns means. The registry frontmatter in [index.md](index.md) is the authority for every path, weight and threshold named here; [guide.md](guide.md) is the runbook a human follows.

## The task

A fixed three-milestone refactoring sprint — migrate the `frontmatter-update` command's unit tests to a txtar e2e corpus (plan `202608121417_frontmatter-update-e2e-migration`).

## The method

Every model runs the same groomed plan from the same baseline commit (`a025189`), in its own throwaway clone on its own `bench/{model_slug}` branch. The develop playbook drives the sprint; every line of code is written by the worker agent pinned to the model under test, with review gates auto-answered and no human in the loop. Two failed attempts on a milestone end the run as `fail@Mnn`; a failed run is not scored on its partial work — `code`, `agentic` and `review` stay `-`, the row carries only the run's footprint: `diff`, `tokens`, `cost`, `time`. One row per run, appended by the `model-benchmark` playbook's publish step; every number is computed by `bench-score` and audited in the linked run detail.

## The worker

The worker agent is the registry entry's `worker`. Runs from 2026-08-16 use `pi-developer`, which hands each milestone to a headless **pi** session as `/orchestrate` and lets pi do its own planning, delegation and validation — one harness reaching every provider pi has (`llama-local/…`, `ollama-cloud/…`, `openrouter/…`), so the model id in the briefing is what selects both model and provider. Earlier rows used `openrouter-developer`, `llama-developer` or the in-process `booping:booping-developer`, each driving a Claude Code session instead; their footnotes say so.

`bench-score` reads either log schema — Claude Code's `assistant`/`user`/`result` stream, or pi's `tool_execution_*` / `message_end` events — and normalises them, so a row's process figures mean the same thing whichever harness produced them. pi tags every event a sub-agent raises with `agent`/`agentRun`, and the run detail's process profile breaks the tool calls down by agent; a pi log written before that tagging existed carries orchestrator traffic only, and a run scored from such logs says so in its detail rather than reporting the gap as clean process.

## Columns

- `date` — run start, `YYYY-MM-DD hh:mm`, taken from the first attempt log's stamp (the same stamp as the `run` link's id)
- `model` — model id as the worker's provider spells it
- `provider` — where the worker ran, keyed by the worker agent: `openrouter-developer` → `openrouter`, `llama-developer` → `local`, `booping:booping-developer` → `anthropic`, `pi-developer` → whichever provider its model id names (`llama-local/…` → `local`, `openrouter/…` → `openrouter`)
- `outcome` — `pass`, or `fail@Mnn` naming the milestone the run died on
- `att` — attempts spent per milestone
- `code` — code-quality composite, %, grading the artifact: CI/scope/determinism gates plus corpus quality against the frozen etalon and mutation set
- `agentic` — process composite, %, read from the worker's tool logs: attempts, rebaselines, tool discipline, churn
- `review` — mean grade on a 1 to 5 scale from independent diff reviewers — isolated sub-agents running OpenAI Sol and Anthropic Fable — scoring the branch against a shared rubric
- `diff` — lines changed
- `tokens` — `in {total input} out {output}`. `in` is the whole input side, cache included; `out` is what the model generated
- `cache` — how much of that input never reached the model fresh: `in {cache reads} out {cache writes}` — read back from the cache, and written into it. Both sit inside `tokens in` and never in `tokens out`, so `in 2.9M` beside `cache in 2.6M` means only ~300k of the input was new. The two counters are disjoint in the raw logs of both harnesses, which is why `in` is their sum rather than either one
- `cost` — USD, from OpenRouter's generation API when the logs carry generation ids, otherwise the worker's own usage accounting
- `time` — sprint duration
- `run` — link to the detail report

Rows published before 2026-08-16 carry a single figure in `tokens` and `-` in `cache`: the split did not exist when they were scored, and a published row is never re-scored. That figure is in+out with cache excluded for every row but `claude-opus-5`, whose footnote records that its prompt figure includes cache reads — so it is not comparable to the `in` of a row scored since.

A cell reading `-` is a layer that was not measured, never a zero. The run detail names the reason.
