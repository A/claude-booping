# claude-booping model benchmark — run guide

A fixed develop-sprint benchmark: every model runs the same groomed plan from the same repo state, in its own throwaway clone, on its own branch, without asking the user anything.

## Invocation

The user hands you this file's path plus a model name, e.g.

```
Run the benchmark in ~/Claude/notes/claude_booping_benchmark.md with llama-local/Qwen3.8-27B
```

`{model}` is that model name, verbatim, as pi spells it — `provider/model`, listed by `pi-developer --list-models [search]`. No model name given → ask for one and stop; never pick one yourself. `{model_slug}` is the model half of that id with every non-alphanumeric character replaced by `-`, lowercased; the provider prefix stays out of the slug and out of the branch name.

## Fixed parameters

| Parameter | Value |
| --- | --- |
| Source repo | `/home/anton/Dev/@A/claude-booping` — cloned per run, never developed in |
| Workspace | `{source repo}/.benchmarks/{workspace_id}-{model_slug}/` — the clone the run happens in; `{workspace_id}` is the `YYYYMMDD-HHMMSS` stamp taken when it is created |
| Baseline commit | `a025189` — head of `bench/reference`: the plan as groomed and `just ci` green, before any of it was developed |
| Plan | `./vault/plans/202608121417_frontmatter-update-e2e-migration/index.md`, inside the workspace (3 milestones, `type: refactoring`, status `awaiting-approval`) |
| Branch | `bench/{model_slug}`, cut inside the workspace |
| Push remote | `gh` → `git@github.com:A/claude-booping.git`, added to the clone |
| Worker agent | `pi-developer`, driven with `{model}` |

These are the `frontmatter-update-e2e` entry in [index.md](index.md)'s registry frontmatter, which is also where the scoring weights and the etalon corpus live. The registry is authoritative; this table is its readable form.

`.benchmarks/` is gitignored in the source repo, so a workspace is invisible to it. Two vaults are in play and must not be confused: the workspace's own `vault/` is the sprint's scratch copy — the plan under test, its milestone statuses, the checkboxes the sprint flips — and dies with the clone, while the scorecard, the run details and the registry live in the source repo's vault and are the only thing committed. Prune a workspace with `rm -rf .benchmarks/{dir}` once you no longer want its branch — nothing pushes it for you.

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
   uv sync --project booping-python
   just ci
   ```

   Sync every uv project the **workspace** holds, not every project the source repo holds today: the baseline is an older commit, and at `a025189` that is `booping-python` alone — `booping-tracker` does not exist there, and `uv sync --project booping-tracker` fails with `Project directory 'booping-tracker' does not exist`. `ls */pyproject.toml` in the clone is the list to sync.

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

Every milestone briefing goes to the `pi-developer` agent, and the briefing's first line pins the model, the run's log path and this milestone's segment label:

```
Use model id `{model}` for this milestone (pass it as `--model`), log the run to
`~/.tmp/pi-developer/{ts}-{model_slug}.ndjson` (pass it as `-L`) and label this
invocation `{milestone}` (pass it as `-S`).
```

`{ts}` is stamped once for the whole run, `date +%Y%m%d-%H%M%S`, and every briefing — retries included — repeats that same path: one run is one log, appended to. `-S` is what splits it back apart, `pi-developer` bracketing each invocation with a `run_segment` marker carrying the label, and `bench-score` scoring one attempt per marker pair. An invocation left without `-S` is labelled with pi-developer's default, the pid, which matches no milestone name and scores as nothing.

No other agent writes code — not `booping:booping-developer`, not the runner. That holds for fix attempts too: a retry after a failed milestone goes back to `pi-developer` with the same `{model}`, so the benchmark measures one model end to end.

### Reasoning effort

`--thinking` takes seven names but `qwen3.8-27b-fp8` serves **three** efforts, so the seven collapse onto them — plus `off`, which suppresses thinking entirely:

| pi level | template effort |
| --- | --- |
| `minimal`, `low` | low |
| `medium` | medium |
| `high`, `xhigh`, `max` | xhigh |

A tier comparison must therefore pick levels from **different rows**. `low` against `medium` against `xhigh` measures three efforts; `high` against `xhigh` against `max` measures one effort three times, and `low` against `minimal` measures one effort twice. Levels within a row differ only by run-to-run variance, which on this benchmark is wide enough to look like a result.

Two things nothing downstream can catch, so the invoker is the only witness: pi clamps a level the model does not expose without printing anything, and the logs carry no reasoning-level field (`usage.reasoning` is 0 on every message). Before trusting a new tier axis, probe it — same prompt, each level three or more times, counting `assistantMessageEvent.thinking_delta` characters in the `-L` ndjson — and re-probe after any change to what the host serves. Reasoning length is prompt-sensitive: on a short factual prompt the three efforts span roughly 250 → 500 → 1,500 characters, on a multi-constraint puzzle roughly 2,300 → 1,600 → 3,700, and the fine ordering between adjacent levels flips between the two.

The scorecard's `provider` column is the provider half of pi's model id — `llama-local/…` → `local`, `openrouter/…` → `openrouter`, `ollama-cloud/…` → `local`. Pass it to `bench-score report` as `--provider` (default `openrouter`). The `effort` column is `--effort` on the same call: the reasoning preset the run pinned (`medium`, `high`, …), left at its `-` default when the model ran on its own default — the logs never record it, so the invoker is the only witness, and two rows naming different levels from the same row of the **Reasoning effort** table above ran at the same effort. `pi-developer` is the only worker there is: the `openrouter-developer` and `llama-developer` agents it replaced were retired on 2026-08-16, and rows they produced are keyed by their own agent; see [method.md](method.md).

## Report

Post the sprint report the playbook asks for, then add the benchmark scorecard:

- model, branch, workspace path, wall-clock duration
- per milestone: attempts spent (1, 2, or failed), the commit sha, whether the DoD held on the first attempt
- guardrails: the `just ci` verdict at the end of the run
- failures worth naming: context-limit deaths, degenerate tool-call loops, malformed tool inputs, milestones abandoned
- the run's log — `~/.tmp/pi-developer/{ts}-{model_slug}.ndjson`, one file holding every attempt as a segment

Leave the branch in place when the run ends; it is the artifact being compared. Do not merge it, do not delete it, do not rebase it. Nothing in the run pushes it anywhere and no pull request is opened — publish commits the scorecard and the run detail, and stops there. The workspace therefore holds the only copy of the branch: it stays until you prune it, and pruning it before pushing the branch by hand throws the artifact away.
