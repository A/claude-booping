# llama.cpp freeze test — fast agentic-load run

A stripped benchmark run for one question only: does llama.cpp freeze under agentic load, and how much wall time do the freezes cost. No scoring, no case mapping, no reviews, no history row, no vault artifacts — the run's whole output is one `wall` + `freezes` readout from `bench-score process`. Everything happens in a persistent throwaway workspace that is reset before and after each run.

## Fixed parameters

| Parameter | Value |
| --- | --- |
| Source repo | `/home/anton/Dev/@A/claude-booping` |
| Workspace | `{source repo}/.benchmarks/freeze-test-{model_slug}/` — persistent, reused across freeze tests, reset each run |
| Baseline commit | `a025189` — same as the real benchmark |
| Plan | `./vault/plans/202608121417_frontmatter-update-e2e-migration/index.md`, inside the workspace |
| Branch | `bench/{model_slug}`, reset to the baseline each run |
| Worker | `pi-developer`, `direct` runner, one invocation for the whole plan |
| Model / thinking | whatever is under test, e.g. `llama-local/Qwen3.8-27B-Q8` with `--thinking medium` |

`{model_slug}` derives as in [guide.md](guide.md): model half of the pi id, non-alphanumerics → `-`, lowercased.

## One-time setup

Skip when the workspace already exists.

```bash
cd /home/anton/Dev/@A/claude-booping
git clone . .benchmarks/freeze-test-{model_slug}
cd .benchmarks/freeze-test-{model_slug}
git checkout -b bench/{model_slug} a025189
cp /home/anton/Dev/@A/claude-booping/.booping .booping
uv sync --project booping-python
```

`just ci` green here once is a sanity check worth the minute; the per-run resets never dirty tooling, so it is not repeated per run.

## Per run

1. **Reset** the workspace to the baseline (also the recovery step after any aborted run):

   ```bash
   cd /home/anton/Dev/@A/claude-booping/.benchmarks/freeze-test-{model_slug}
   git checkout bench/{model_slug}
   git reset --hard a025189
   git clean -fd
   ```

   `git clean` without `-x` keeps every gitignored file — `.booping` and the synced `.venv` survive; only the worker's leftover work is swept.

2. **Stamp** the run's log path: `~/.tmp/pi-developer/freeze-{ts}-{model_slug}.ndjson`, `{ts}` = `date +%Y%m%d-%H%M%S`. One fresh log per run — never append to an earlier test's log.

3. **Launch** one `pi-developer` invocation covering the whole plan, and let it run to the end unless stopped by hand:

   ```bash
   ~/.claude/bin/pi-developer -D -C {workspace} \
     --model {model} --thinking {level} \
     -L ~/.tmp/pi-developer/freeze-{ts}-{model_slug}.ndjson -S freeze-test \
     "Implement the plan vault/plans/202608121417_frontmatter-update-e2e-migration/index.md — all three milestones under its milestones/ directory, in id order (M01, M02, M03), each to its own Definition of Done, running each milestone's Verify command. Read the plan and each milestone file first. Work on the current branch; leave everything uncommitted."
   ```

   Poll `~/.claude/bin/pi-developer --status {status-path}` until `DONE` (via the `pi-developer` agent this is its normal collect loop). Milestone bookkeeping, transitions, DoD validation and commits are all skipped — nothing here is a sprint, so nothing sprint-shaped is recorded.

4. **Read the numbers.** `--ndjson` mode profiles every segment in the file regardless of label, so the single `freeze-test` segment needs no milestone-name mapping and no worktree:

   ```bash
   cd /home/anton/Dev/@A/claude-booping
   vault/benchmarks/_scripts/bench-score process --benchmark frontmatter-update-e2e \
     --ndjson ~/.tmp/pi-developer/freeze-{ts}-{model_slug}.ndjson \
     | jq '.run | {wall, freezes, freeze_ms}'
   ```

   `wall` is the segment's whole duration, `freezes`/`freeze_ms` the wedge count and total lost time — the same detector the real benchmark's `freeze` column uses. Everything else in the JSON is ignorable here.

5. **Reset back** — repeat step 1, so the workspace is clean for the next test.

## What this run is not

- Not a benchmark run: no registry artifact, no `runs/` detail, no history row — never publish these numbers.
- Nothing is committed anywhere and no branch state survives the reset; the log under `~/.tmp/pi-developer/` is the run's only residue, delete it when done.
- A freeze mid-run is the finding, not a failure: note the wall/freeze readout and reset. Stopping a wedged run by hand is fine — the log up to the stop still profiles.
