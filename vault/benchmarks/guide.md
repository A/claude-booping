# claude-booping model benchmark — run guide

A fixed develop-sprint benchmark: every model runs the same groomed plan from the same repo state, in its own throwaway clone, on its own branch, without asking the user anything.

## Invocation

The user hands you this file's path plus a model name, e.g.

```
Run the benchmark in ~/Claude/notes/claude_booping_benchmark.md with qwen/qwen3-next-80b-a3b-instruct
```

`{model}` is that model name, verbatim, as OpenRouter spells it. No model name given → ask for one and stop; never pick one yourself. `{model_slug}` is `{model}` with `/` and any other non-alphanumeric character replaced by `-`.

## Fixed parameters

| Parameter | Value |
| --- | --- |
| Source repo | `/home/anton/Dev/@A/claude-booping` — cloned per run, never developed in |
| Workspace | `{source repo}/.benchmarks/{workspace_id}-{model_slug}/` — the clone the run happens in; `{workspace_id}` is the `YYYYMMDD-HHMMSS` stamp taken when it is created |
| Baseline commit | `a025189` — head of `bench/reference`: the plan as groomed and `just ci` green, before any of it was developed |
| Plan | `./vault/plans/202608121417_frontmatter-update-e2e-migration/index.md`, inside the workspace (3 milestones, `type: refactoring`, status `awaiting-approval`) |
| Branch | `bench/{model_slug}`, cut inside the workspace |
| Push remote | `gh` → `git@github.com:A/claude-booping.git`, added to the clone |
| Worker agent | `openrouter-developer`, driven with `{model}` |

These are the `frontmatter-update-e2e` entry in [index.md](index.md)'s registry frontmatter, which is also where the scoring weights and the etalon corpus live. The registry is authoritative; this table is its readable form.

`.benchmarks/` is gitignored in the source repo, so a workspace is invisible to it. Two vaults are in play and must not be confused: the workspace's own `vault/` is the sprint's scratch copy — the plan under test, its milestone statuses, the checkboxes the sprint flips — and dies with the clone, while the scorecard, the run details and the registry live in the source repo's vault and are the only thing committed. Workspaces are disposable: prune them with `rm -rf .benchmarks/{dir}` once a run's branch is pushed.

## Steps

1. Confirm the source repo has the baseline commit (`git -C /home/anton/Dev/@A/claude-booping cat-file -t a025189`). A dirty source tree is irrelevant — a clone carries committed state only, so nothing here touches your work.

2. Clone into the workspace and cut the branch off the baseline. `{workspace_id}` is stamped now, `date +%Y%m%d-%H%M%S`:

   ```
   git clone /home/anton/Dev/@A/claude-booping .benchmarks/{workspace_id}-{model_slug}
   cd .benchmarks/{workspace_id}-{model_slug}
   git remote add gh git@github.com:A/claude-booping.git
   git checkout -b bench/{model_slug} a025189
   ```

   The clone is local, so its objects are hardlinked and it costs no network. `origin` points back at the source repo and is never pushed to; `gh` is what carries the branch to GitHub in publish.

3. Restore the gitignored files the clone could not carry, then build the virtualenvs — all before any development starts:

   ```
   cp /home/anton/Dev/@A/claude-booping/.booping .booping
   uv sync --project booping-python && uv sync --project booping-tracker
   just ci
   ```

   `.booping` is the vault marker and is gitignored, so a fresh clone has none and every `booping` call in the workspace would resolve no vault. `just ci` green here is the precondition for the run: the model under test never fixes tooling itself, and a run where it spends attempts on a broken workspace measures the workspace, not the model. Red → stop and report; do not start the sprint.

4. Run the develop playbook against the plan, from inside the workspace:

   ```
   /playbook develop ./vault/plans/202608121417_frontmatter-update-e2e-migration/index.md
   ```

5. Drive the whole sprint to its end without asking the user anything — see **Autonomy** below.
6. Report the result — see **Report**.

## Autonomy

The user is not available during a benchmark run. Every decision the playbook would put to them is pre-answered here:

- **Branch**: `bench/{model_slug}`, already created in step 2. Do not call `AskUserQuestion` for it; do not create another branch; do not switch branches mid-run.
- **Plan validity / drift**: the baseline commit is the plan's own groom commit, so there is no drift. Any drift check answers "proceed".
- **Review gates**: answer them yourself with the option that continues the run, and record in the report that the gate was auto-answered.
- **Abort approval**: after two recorded attempts on the same milestone the playbook needs approval to abort. Approve it yourself — a failed sprint is a valid measurement, not a reason to intervene. See **Failed sprints** below.
- Never call `AskUserQuestion` at any point in the run. Never wait for a chat reply.

Everything else about the playbook is unchanged: the runner never writes application code, every milestone goes to a worker agent, milestones run one at a time on the branch, and the plan's own bookkeeping (DoD checkboxes, milestone statuses, transitions) is done exactly as the playbook prescribes.

## Failed sprints

A model that exhausts its attempts on a milestone produces a result, not an aborted run. When the playbook asks for abort approval, approve it, take the `fail` edge, and record the outcome as `fail@Mnn` — `Mnn` being the milestone it died on. That string is what lands in the scorecard's `outcome` column.

Then continue exactly as for a passing run: leave the workspace and its branch in place with whatever work they carry, and run measure and publish over them. A failed run is not scored on its partial work — `code`, `agentic` and `review` stay `-` in the scorecard row; what the row does carry is the run's footprint (`diff`, `tokens`, `cost`, `time`) plus a footnote when the failure needs explaining, and that footprint is the comparison being made. Never delete the branch, re-run the sprint from scratch, or finish the milestone by hand.

## Worker delegation

Every milestone briefing goes to the `openrouter-developer` agent, and the briefing's first line pins the model:

```
Use OpenRouter model `{model}` for this milestone.
```

No other agent writes code — not `booping:booping-developer`, not the runner. That holds for fix attempts too: a retry after a failed milestone goes back to `openrouter-developer` with the same `{model}`, so the benchmark measures one model end to end.

The scorecard's `provider` column is keyed by the worker agent that ran the milestones: `openrouter-developer` → `openrouter`, `llama-developer` → `local`, `booping:booping-developer` → `anthropic`. Pass it to `bench-score report` as `--provider` (default `openrouter`).

## Report

Post the sprint report the playbook asks for, then add the benchmark scorecard:

- model, branch, workspace path, wall-clock duration
- per milestone: attempts spent (1, 2, or failed), the commit sha, whether the DoD held on the first attempt
- guardrails: the `just ci` verdict at the end of the run
- failures worth naming: context-limit deaths, degenerate tool-call loops, malformed tool inputs, milestones abandoned
- the worker's run logs — `~/.tmp/openrouter-developer/*.ndjson`, one per attempt

Leave the branch in place when the run ends; it is the artifact being compared. Do not merge it, do not delete it, do not rebase it. Publish is what pushes it to `gh`; nothing before publish pushes anything. The workspace stays until you prune it — measure and the diff reviewers read it, and a pruned workspace is only recoverable by cloning again from the pushed branch.
