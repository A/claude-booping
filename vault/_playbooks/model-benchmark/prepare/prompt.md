---
summary: Resolve the model and the benchmark entry against the registry, refuse the run on any failed preflight, then cut the benchmark branch off the entry's baseline and get its virtualenvs green before a single milestone is delegated.
review_gate: null
---

# Prepare the benchmark run

## Resolve

- **Model** — the name the user gave, verbatim, as OpenRouter spells it. None given → say so and stop. Never pick a model, never infer one from an earlier run.
- **Benchmark** — the id the user gave, matched against the registry entries in `{vault}/benchmarks/index.md`. None given and the registry holds one entry → that entry. Several → ask which. An id no entry carries → say so and stop.
- **`{model_slug}`** — derived from the model name per `guide.md`'s **Invocation** section. The branch is the entry's `branch_scheme` with that slug substituted.

Everything below reads the resolved entry: `repo`, `baseline`, `plan`, `worker`, `logs_dir`, `api_key_env`. Read them from the frontmatter; do not carry them from a previous run.

## Preflight

All four checks run before anything is created. A failed check stops the run with one line naming what failed and what it needs — no stashing, no discarding, no fixing it on the user's behalf:

| Check | Refusal |
| --- | --- |
| the entry's `repo` has a clean tree (`git status --short` empty) | uncommitted work in the bench repo — commit or clear it, nothing here touches it |
| the branch is unborn (`git rev-parse --verify` fails on it) | that benchmark branch already exists — an earlier run for this model is on it and is never overwritten |
| the environment variable the entry's `api_key_env` names is set and non-empty | the OpenRouter key is not in this environment — the cost layer cannot be measured without it |
| the entry's `logs_dir` exists and is writable | the worker's log directory is missing or read-only — without its ndjson there is no process profile and no cost |

## Cut the branch

Create the branch off the entry's `baseline` in the entry's `repo`, and stay on it for the whole run. Then run `guide.md`'s virtualenv precheck step in that repo and get it green here — a sprint that spends attempts on broken tooling measures the copy, not the model.

## Closing the step

Nothing is written to the vault and no transition is taken: the run artifact is born in `measure` (see the preamble). Carry the resolved facts forward in the return — `run` and `measure` both work from them.

## Return format

```markdown
## Notes:

- model: `{model}` → slug `{model_slug}`
- benchmark: `{id}` — repo `{repo}`, baseline `{baseline}`, plan `{plan}`, worker `{worker}`
- branch: `{branch}` created off `{baseline}`
- preflight: tree clean; branch unborn; `{api_key_env}` present; logs dir `{logs_dir}` writable
- venvs: {what the precheck reported, and whether anything had to be re-synced}
- started: {YYYY-MM-DD HH:MM}
```
