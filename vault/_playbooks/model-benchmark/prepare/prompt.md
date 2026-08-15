---
summary: Resolve the model and the benchmark entry against the registry, refuse the run on any failed preflight, then clone the source repo into a fresh per-run workspace, cut the benchmark branch off the entry's baseline there, and get the workspace green before a single milestone is delegated.
review_gate: null
---

# Prepare the benchmark run

## Resolve

- **Model** — the name the user gave, verbatim, as OpenRouter spells it. None given → say so and stop. Never pick a model, never infer one from an earlier run.
- **Benchmark** — the id the user gave, matched against the registry entries in `{vault}/benchmarks/index.md`. None given and the registry holds one entry → that entry. Several → ask which. An id no entry carries → say so and stop.
- **`{model_slug}`** — derived from the model name per `guide.md`'s **Invocation** section. The branch is the entry's `branch_scheme` with that slug substituted.
- **`{workspace_id}`** — `date +%Y%m%d-%H%M%S`, stamped now. The workspace is the entry's `workspace_scheme` with it and the slug substituted, under `{source_repo}/{workspaces_dir}/`. It is this run's own directory: never reused, never shared with another run, and unrelated to the detail report's `{run_id}`, which `measure` derives from the worker logs.

Everything below reads the resolved entry: `source_repo`, `workspaces_dir`, `workspace_scheme`, `push_remote`, `baseline`, `plan`, `worker`, `logs_dir`, `api_key_env`. Read them from the frontmatter; do not carry them from a previous run.

## Preflight

All four checks run before anything is created. A failed check stops the run with one line naming what failed and what it needs — no fixing it on the user's behalf:

| Check | Refusal |
| --- | --- |
| the entry's `baseline` resolves in `source_repo` (`git cat-file -t`) | the baseline commit is not in the source repo — fetch it before benchmarking anything against it |
| the workspace path does not exist | that workspace is already there — pick a fresh `{workspace_id}` rather than developing on top of another run |
| the environment variable the entry's `api_key_env` names is set and non-empty | the OpenRouter key is not in this environment — the cost layer cannot be measured without it |
| the entry's `logs_dir` exists and is writable | the worker's log directory is missing or read-only — without its ndjson there is no process profile and no cost |

The source repo's own tree is never inspected and never touched: a clone carries committed state only, so the user can be mid-edit in it while a benchmark runs.

## Clone the workspace

Follow `guide.md`'s **Steps** 2 and 3 as written: clone `source_repo` into the workspace, add the entry's `push_remote`, cut the branch off `baseline` there, restore the gitignored `.booping` marker from the source repo, sync both virtualenvs, and get `just ci` green. Every command from here to the end of the run has the workspace as its cwd.

A red `just ci` stops the run — a sprint on a broken workspace measures the workspace, not the model. Report what failed and leave the clone in place for inspection.

## Closing the step

Nothing is written to the vault and no transition is taken: the run artifact is born in `measure` (see the preamble). Carry the resolved facts forward in the return — `run` and `measure` both work from them.

## Return format

```markdown
## Notes:

- model: `{model}` → slug `{model_slug}`
- benchmark: `{id}` — source repo `{source_repo}`, baseline `{baseline}`, plan `{plan}`, worker `{worker}`
- workspace: `{workspace path}` — clone of `{source_repo}`, remote `{push_remote.name}` added
- branch: `{branch}` created off `{baseline}` in the workspace
- preflight: baseline resolves; workspace path fresh; `{api_key_env}` present; logs dir `{logs_dir}` writable
- setup: `.booping` restored; venvs synced; `just ci` {verdict}
- started: {YYYY-MM-DD HH:MM}
```
