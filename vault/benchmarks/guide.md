# claude-booping model benchmark — run guide

A fixed develop-sprint benchmark: every model runs the same groomed plan from the same repo state, on its own branch, without asking the user anything.

## Invocation

The user hands you this file's path plus a model name, e.g.

```
Run the benchmark in ~/Claude/notes/claude_booping_benchmark.md with qwen/qwen3-next-80b-a3b-instruct
```

`{model}` is that model name, verbatim, as OpenRouter spells it. No model name given → ask for one and stop; never pick one yourself. `{model_slug}` is `{model}` with `/` and any other non-alphanumeric character replaced by `-`.

## Fixed parameters

| Parameter | Value |
| --- | --- |
| Repo | `/home/anton/Dev/@A/claude-booping-local-bench` |
| Baseline commit | `6fd0f38` — `groom: milestone contracts for frontmatter-update e2e migration`, head of `bench/reference`: the plan as groomed, before any of it was developed |
| Plan | `./vault/plans/202608121417_frontmatter-update-e2e-migration/index.md` (3 milestones, `type: refactoring`, status `awaiting-approval`) |
| Branch | `bench/{model_slug}` |
| Worker agent | `openrouter-developer`, driven with `{model}` |

These are the `frontmatter-update-e2e` entry in [index.md](index.md)'s registry frontmatter, which is also where the scoring weights and the etalon corpus live. The registry is authoritative; this table is its readable form.

## Steps

1. `cd /home/anton/Dev/@A/claude-booping-local-bench`.
2. Confirm the tree is clean (`git status --short`). Dirty → stop and report; never stash or discard the user's work.
3. Cut the benchmark branch off the baseline: `git checkout -b bench/{model_slug} 6fd0f38`. The branch already exists → stop and report, so an earlier run is never overwritten.
4. Prepare the virtualenvs, before any development starts:

   ```
   uv sync --project booping-python && uv sync --project booping-tracker
   head -1 booping-python/.venv/bin/pytest booping-tracker/.venv/bin/pytest
   ```

   The bench repo is a copy directory, so it ships `.venv/` trees whose console-script shebangs still point at the source checkout. Both shebangs must name a path under the bench repo; if either still points elsewhere, delete that `.venv/` and re-sync. Get this green now — the model under test never fixes venvs itself, and a run where it spends attempts on broken tooling measures the copy, not the model.

5. Run the develop playbook against the plan:

   ```
   /playbook develop ./vault/plans/202608121417_frontmatter-update-e2e-migration/index.md
   ```

6. Drive the whole sprint to its end without asking the user anything — see **Autonomy** below.
7. Report the result — see **Report**.

## Autonomy

The user is not available during a benchmark run. Every decision the playbook would put to them is pre-answered here:

- **Branch**: `bench/{model_slug}`, already created in step 3. Do not call `AskUserQuestion` for it; do not create another branch; do not switch branches mid-run.
- **Plan validity / drift**: the baseline commit is the plan's own groom commit, so there is no drift. Any drift check answers "proceed".
- **Review gates**: answer them yourself with the option that continues the run, and record in the report that the gate was auto-answered.
- **Abort approval**: after two recorded attempts on the same milestone the playbook needs approval to abort. Approve it yourself — a failed sprint is a valid measurement, not a reason to intervene. See **Failed sprints** below.
- Never call `AskUserQuestion` at any point in the run. Never wait for a chat reply.

Everything else about the playbook is unchanged: the runner never writes application code, every milestone goes to a worker agent, milestones run one at a time on the branch, and the plan's own bookkeeping (DoD checkboxes, milestone statuses, transitions) is done exactly as the playbook prescribes.

## Failed sprints

A model that exhausts its attempts on a milestone produces a result, not an aborted run. When the playbook asks for abort approval, approve it, take the `fail` edge, and record the outcome as `fail@Mnn` — `Mnn` being the milestone it died on. That string is what lands in the scorecard's `outcome` column.

Then continue exactly as for a passing run: leave the branch in place with whatever work it carries, and run measure and publish over it. Partial work still scores — gates, corpus quality and the process profile are all computed on what the branch actually holds, and a `fail@Mnn` row with real numbers is the comparison being made. Never delete the branch, re-run the sprint from scratch, or finish the milestone by hand.

## Worker delegation

Every milestone briefing goes to the `openrouter-developer` agent, and the briefing's first line pins the model:

```
Use OpenRouter model `{model}` for this milestone.
```

No other agent writes code — not `booping:booping-developer`, not the runner. That holds for fix attempts too: a retry after a failed milestone goes back to `openrouter-developer` with the same `{model}`, so the benchmark measures one model end to end.

## Report

Post the sprint report the playbook asks for, then add the benchmark scorecard:

- model, branch, wall-clock duration
- per milestone: attempts spent (1, 2, or failed), the commit sha, whether the DoD held on the first attempt
- guardrails: the `just ci` verdict at the end of the run
- failures worth naming: context-limit deaths, degenerate tool-call loops, malformed tool inputs, milestones abandoned
- the worker's run logs — `~/.tmp/openrouter-developer/*.ndjson`, one per attempt

Leave the branch in place when the run ends; it is the artifact being compared. Do not merge it, do not delete it, do not push it.
