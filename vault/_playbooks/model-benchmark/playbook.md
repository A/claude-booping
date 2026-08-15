---
name: model-benchmark
title: Model benchmark
summary: Run one model through the fixed develop-sprint benchmark end to end — clone a throwaway workspace, drive the sprint autonomously on its own branch, score every layer with `bench-score`, and publish one comparable scorecard row backed by a full run detail report.
trigger: benchmark a model; score a bench branch; run the model benchmark and publish its scorecard
jinja: true
requires_project: true
---
A run ends with one row appended to the benchmark history and one detail report behind it: every mechanical number computed by `bench-score`, every review grade returned by a reviewer, and the benchmark branch left exactly as the sprint left it.

## Guidance

- The run workdir is `{vault}/benchmarks/`. Its `index.md` frontmatter is the registry — the benchmark ids, and every path, command, list, weight and threshold the run works from. Read values from there, never from memory, and never restate them in chat as fixed facts.
- Two trees, and they are never confused. The **source repo** holds the registry, the vault and the scorecard, and is the only thing committed to. The **workspace** is the per-run clone `prepare` creates under the entry's `workspaces_dir` — gitignored, disposable, and where the branch, the sprint, the scored worktree and the reviewed diff all live. Every `bench-score` call names it with `--repo`; nothing in the run develops in the source repo.
- With no benchmark id given, use the registry's only entry; with several, ask which. The model name is never chosen for the user — `prepare` stops without one.
- `guide.md` is the default benchmark's runbook: the fixed parameters, the venv precheck, the autonomy rules the sprint runs under, worker delegation, and what a failed sprint is. Steps point at its sections instead of copying them.
- The run artifact is the detail report `runs/{run_id}-{model_slug}.md` under the workdir. It does not exist until `measure`: `bench-score report` creates it, already carrying `status: measuring`, and its `{run_id}` is derived from the worker logs, so it is unknowable before the sprint has run. `preparing` and `running` are therefore held in this conversation alone — the run's first `booping playbook-transition` call is the one leaving `measuring`, and every call passes `--workdir {vault}/benchmarks --target runs/{run_id}-{model_slug}.md`, since the machine declares no `artifact:`.
- Nothing computes a metric by hand. Every number in the row and the detail comes from `bench-score` or from a reviewer's return; a layer that cannot be measured is left to `bench-score` to drop and name, never estimated.
- The benchmark branch is the artifact being compared: never merged, never deleted, never rebased, never fixed up by hand — not while measuring, not after a failed sprint. `publish` is the only step that pushes it, and no step deletes a workspace.

{% include "_partials/playbook_shared_instructions.md" %}
