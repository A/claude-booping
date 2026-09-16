# Model benchmarks: score models on a real develop sprint

Which model should run your develop sprints? A public leaderboard scores puzzle-solving in a vacuum, not whether a model can carry a three-milestone refactoring through a real playbook — reading a groomed plan, staying inside a scope allowlist, keeping CI green, writing tests that actually catch bugs. booping's answer is to make the sprint itself the benchmark: every model runs the same plan from the same commit under the same rules, and everything it does gets scored into one comparable scorecard row.

The result worth spoiling up front: the biggest lever turned out to be the harness, not the model. Handing a milestone to the model directly beat one of the two orchestration templates tried against it outright and matched the other in less than half the wall clock — and the one it beat was retired as pure overhead.

## What a run is

The benchmark is a fixed develop sprint — one groomed plan, frozen at a baseline commit where the plan exists and CI is green, before any of it was developed. Every run:

- **clones the source repo into a throwaway workspace** — a per-run clone under a gitignored `.benchmarks/` directory, so nothing touches a checkout anyone works in
- **cuts its own branch off the baseline** — `bench/{model_slug}`, the run's artifact: never merged, never rebased, never fixed up by hand
- **drives the [develop playbook](../develop.md) autonomously** — review gates auto-answered, plan drift impossible because the baseline is the plan's own groom commit
- **pins every line of code to the model under test** — the runner never writes code; each milestone briefing goes to a single worker agent, a thin proxy handing the work to a headless pi session (the same [agent-proxy pattern](external-agents.md) used for any external worker), so the model id in the briefing (`llama-local/{model}`, `openrouter/{model}`, …) selects both the model and the provider

Two failed attempts on the same milestone end the run as `fail@Mnn`. A failed run is still a result: it is not scored on its partial work, but its row carries the run's footprint — diff size, tokens, cost, wall-clock — because a model that dies expensively and one that dies cheaply are different answers.

Every worker invocation appends to one ndjson log for the whole run, with a segment label per milestone — the process half of the score is read from it later.

## What a row means

Every number comes from one script, `bench-score`, in the vault at `benchmarks/_scripts/bench-score`. It hardcodes nothing: every path, command, weight and threshold is read from a machine-readable registry (frontmatter on `benchmarks/index.md`). One subcommand per scoring layer:

- **`gates`** — pass/fail checks on the finished branch: CI green, the diff inside the scope allowlist, deterministic re-runs, the superseded tests actually deleted
- **`corpus`** — quality of the test corpus the sprint produced, graded against a frozen reference corpus (the *etalon*, frozen from one chosen reference run and never regenerated in place)
- **`mutations`** — kill-rate over a frozen set of bug patches: each mutation is applied and the model's corpus must fail
- **`process`** — read from the worker's tool logs: attempts spent, test-baseline rewrites, tool discipline (malformed tool inputs, degenerate call loops, context deaths), and churn. The reader normalises both the Claude Code log schema and pi's, so process figures mean the same thing whichever harness produced them
- **`cost`** — USD from the provider's generation accounting, or the worker's own usage figures for local models
- **`report`** — folds all of the above, plus review grades, into the final row and writes the run detail

Review is the one layer no script computes: independent diff reviewers — isolated sub-agents on different frontier models — grade the branch against a shared rubric on a 1–5 scale. `bench-score report` emits the review cell pending and the playbook's measure step folds the reviewers' rows and their mean grade into the detail report and the history row.

The output is three artifacts per run: one row appended to `benchmarks/history.md` (the append-only scorecard), a machine-shaped detail report under `benchmarks/runs/`, and a human-readable report under `benchmarks/reports/` that the row links. A cell reading `-` is a layer that was not measured, never a zero — the detail report names the reason.

## Setting one up in your own vault

The benchmark machinery is vault content, not a plugin feature — it exercises booping from userland, so you can build the same thing in any project's [vault](../vault.md). The pieces:

1. **Freeze the task.** Pick a plan that makes a good yardstick — a refactoring with a checkable outcome works well, because the result can be graded against a reference rather than against taste. Groom it, get CI green, and record that commit as the baseline every run branches from.
2. **Write the registry.** Frontmatter on `benchmarks/index.md`: the baseline commit, the plan path, the workspace and branch naming schemes, the scope allowlist, every command as an argv list, and the scoring weights and thresholds as data. Benchmarking a differently-built repo is then a registry entry, not a script fork.
3. **Freeze the quality references.** An etalon corpus (the reference the `corpus` layer grades against) and a mutation patch set under `benchmarks/mutations/{id}/`. Both are frozen per benchmark id — a new baseline is a new entry, never a regeneration in place, or old rows stop being comparable.
4. **Write the runbook.** A `guide.md` a human (or the playbook) can follow: the fixed parameters, the workspace setup, and — the part that makes runs comparable — the autonomy rules that pre-answer every question the playbook would put to a user.
5. **Wrap it in a playbook.** A user playbook in the vault's `_playbooks/` — prepare, run, measure, report, publish — makes the whole run one invocation and keeps the bookkeeping (state transitions, the appended row, the committed reports) out of human hands. See [Playbooks](../playbook.md) for how user playbooks are discovered and driven.

## Driving a run

With the pieces in place, a run is one command:

```
/playbook model-benchmark with llama-local/Qwen3.8-27B-Q8
```

Under the hood, prepare clones and branches:

```
git clone {source_repo} .benchmarks/{workspace_id}-{model_slug}
cd .benchmarks/{workspace_id}-{model_slug}
git checkout -b bench/{model_slug} {baseline}
```

then restores anything gitignored the clone could not carry (the vault marker, virtualenvs) and verifies CI is green *before* the sprint starts — a model that spends attempts on a broken workspace measures the workspace, not the model. The sprint itself is the ordinary develop playbook run against the plan inside the clone, every milestone delegated to the pinned worker. Measure is a series of `bench-score` calls against the workspace:

```
bench-score gates     --benchmark {id} --branch bench/{model_slug} --repo {workspace}
bench-score corpus    --benchmark {id} --branch bench/{model_slug} --repo {workspace}
bench-score mutations --benchmark {id} --branch bench/{model_slug} --repo {workspace}
bench-score process   --benchmark {id} --ndjson {run_log}          --repo {workspace}
bench-score report    --benchmark {id} --branch bench/{model_slug} --repo {workspace} …
```

and publish commits the row and the reports to the source repo's vault. The workspace and its branch stay behind as the comparable artifact until you prune them.

## The insight: direct beats the orchestration templates

*How* a milestone is driven inside the worker's session is a harness variable, not a model one — so two rows differing only in that setting measure the orchestration. Three modes went head to head, recorded in the scorecard's `orch` column:

- **`orchestrate`** — the session cuts the milestone into chunks and briefs a fresh worker per chunk, with a separate validator agent checking each
- **`loop`** — the session writes one task list and workers take tasks from it in a single warm context until a context budget stops them, each reporting what the next one needs to know
- **`direct`** — no template at all: the milestone briefing goes straight to the session as a plain prompt, with the model's own tools and no orchestration scaffolding

Direct was meant to be the humble baseline the other two justified themselves against. It won. On the same 27B local model, the `loop` runs passed with code scores of 88.6 and 81.2 and review grades around 3 out of 5, each taking over an hour; the `direct` run scored 91.3 on code and 4.38 on review in under an hour, and a medium-reasoning variant driven direct reached 95.0. The templates spent their budget on their own machinery — fresh workers re-reading context, task-list bookkeeping, validator round-trips — without buying quality the plain briefing did not already get: the best `orchestrate` row on the board, 95.9 on code, needed more than twice the wall clock of the direct run that landed within a point of it.

`/loop` was retired on that evidence: it earned nothing for its overhead. Every run since uses direct orchestration, and it is now the baseline any future template has to beat — with a scorecard row, not an argument.

That is the real return on the benchmark: set up to compare models, its first durable finding was about the harness — a claim nobody would have settled from intuition, closed by two rows in a table.
