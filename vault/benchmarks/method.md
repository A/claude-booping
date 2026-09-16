# Benchmark method

How a row in [history.md](history.md) is produced, and what each of its columns means. The registry frontmatter in [index.md](index.md) is the authority for every path, weight and threshold named here; [guide.md](guide.md) is the runbook a human follows.

## The task

A fixed three-milestone refactoring sprint — migrate the `frontmatter-update` command's unit tests to a txtar e2e corpus (plan `202608121417_frontmatter-update-e2e-migration`).

## The method

Every model runs the same groomed plan from the same baseline commit (`a025189`), in its own throwaway clone on its own `bench/{model_slug}` branch. The develop playbook drives the sprint; every line of code is written by the worker agent pinned to the model under test, with review gates auto-answered and no human in the loop. Two failed attempts on a milestone end the run as `fail@Mnn`; a failed run is not scored on its partial work — `code`, `agentic` and `review` stay `-`, the row carries only the run's footprint: `diff`, `tokens`, `cost`, `time`. One row per run, appended by the `model-benchmark` playbook's publish step; every number is computed by `bench-score` and audited in the linked run detail.

## The worker

The worker agent is the registry entry's `worker`, and it is `pi-developer`: it hands each milestone to a headless **pi** session and lets pi do its own planning, delegation and validation — one harness reaching every provider pi has (`llama-local/…`, `ollama-cloud/…`, `openrouter/…`), so the model id in the briefing selects both model and provider. It is the only worker. `openrouter-developer` and `llama-developer` were retired on 2026-08-16, pi covering both their providers through one code path; rows they produced record the harness that actually ran them in their run details.

How the milestone is driven inside that session is the run's `orch` setting — `/loop`, `/orchestrate`, or `direct` with no template at all. It is a harness variable, not a model one, so two rows differing only in `orch` measure the orchestration and not the model.

`bench-score` reads either log schema — Claude Code's `assistant`/`user`/`result` stream, or pi's `tool_execution_*` / `message_end` events — and normalises them, so a row's process figures mean the same thing whichever harness produced them. pi tags every event a sub-agent raises with `agent`/`agentRun`, and the run detail's process profile breaks the tool calls down by agent; a pi log written before that tagging existed carries orchestrator traffic only, and a run scored from such logs says so in its detail rather than reporting the gap as clean process.

## Columns

- `date` — run start, `YYYY-MM-DD hh:mm`, taken from the first attempt log's stamp (the same stamp as the `report` link's id)
- `model` — model id as the worker's provider spells it
- `provider` — where the worker ran: the provider half of pi's model id (`llama-local/…` → `local`, `ollama-cloud/…` → `local`, `openrouter/…` → `openrouter`). Rows predating pi are keyed by their own retired worker instead — `openrouter-developer` → `openrouter`, `llama-developer` → `local`, `booping:booping-developer` → `anthropic`
- `orch` — how the milestone was driven inside the pi session, which is a property of the harness rather than of the model:
  - `orchestrate` — pi's `/orchestrate`: the session cuts the milestone into chunks and briefs a fresh worker per chunk, validating each with a separate validator agent
  - `loop` — pi's `/loop`: the session writes one task list and workers take tasks from it in a single warm context until a context budget stops them, each reporting what the next one needs to know
  - `direct` — no runner at all: the milestone briefing goes straight to pi as a plain prompt, with pi's own tools and no orchestration template. The baseline the other two are measured against
  - `-` — rows predating pi, driven by a retired worker that had no such choice
- `effort` — the reasoning-effort preset the run pinned the model to (`medium`, `high`, …). Stated by the invoker at scoring time (`bench-score report --effort`): the logs never record it, so the branch slug and the run setup are its only witnesses. `-` when the run used the model's default or the setting predates the column
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
- `freeze` — `{lost time} ({wedge count})`: time lost to provider wedges — a stream dying mid-request and being auto-retried, which locally means the model reloading or llama-swap restarting. Counted from pi's `auto_retry` events; each wedge is measured from the last logged progress before the doomed request to the first progress after its retry, so the doomed generation itself counts as lost. A lower bound: a stall the provider recovers from without a retry leaves no event and is not counted. `-` on rows whose logs carry no retry events (Claude Code schema, or scored before the metric existed), never a zero
- `report` — link to the human-readable run report under `reports/`; rows published before the reports existed carry `-` and are read through their detail under `runs/`
- `comment` — free-form human note on the row, written by hand after the run; `bench-score` and the playbook always leave it empty

Rows published before 2026-08-16 carry a single figure in `tokens` and `-` in `cache`: the split did not exist when they were scored, and a published row is never re-scored. That figure is in+out with cache excluded for every row but `claude-opus-5`, whose prompt figure includes cache reads — so it is not comparable to the `in` of a row scored since.

A cell reading `-` is a layer that was not measured, never a zero. The run detail names the reason.
