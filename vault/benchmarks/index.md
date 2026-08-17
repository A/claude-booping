---
benchmarks:
  - id: frontmatter-update-e2e
    source_repo: /home/anton/Dev/@A/claude-booping
    workspaces_dir: .benchmarks
    workspace_scheme: "{workspace_id}-{model_slug}"
    push_remote:
      name: gh
      url: git@github.com:A/claude-booping.git
    baseline: a025189
    plan: vault/plans/202608121417_frontmatter-update-e2e-migration/index.md
    branch_scheme: bench/{model_slug}
    worker: pi-developer
    logs_dir: ~/.tmp/pi-developer
    api_key_env: OPENROUTER_API_KEY
    scope_allowlist:
      - booping-python/e2e/cases/frontmatter-update/*.txtar
      - booping-python/tests/commands/frontmatter_update_test.py
      - vault/plans/202608121417_frontmatter-update-e2e-migration/**
    milestones_glob: milestones/*/M*.md
    cases_dir: booping-python/e2e/cases/frontmatter-update
    unit_file: booping-python/tests/commands/frontmatter_update_test.py
    unit_grep: frontmatter_update_test
    unit_grep_exclude:
      - vault
    commands:
      ci:
        argv: [just, ci]
      e2e:
        argv: [just, e2e]
      e2e_update:
        argv: [uv, run, pytest, e2e, --txtar-update]
        cwd: booping-python
      mutation_e2e:
        argv: [uv, run, pytest, e2e/cases/frontmatter-update, -q, --tb=no]
        cwd: booping-python
    etalon_cases:
      - append-creates-a-list-on-an-absent-key.txtar
      - append-creates-a-list-on-a-null-key.txtar
      - append-extends-an-existing-list.txtar
      - appending-the-same-value-twice-adds-it-once.txtar
      - append-onto-a-scalar-is-rejected.txtar
      - a-real-macro-runs-and-its-output-lands.txtar
      - boolean-value-lands-unquoted.txtar
      - diff-names-the-plan-on-both-sides.txtar
      - empty-key-in-a-pair-is-rejected.txtar
      - empty-value-lands-as-an-empty-string.txtar
      - float-value-lands-unquoted.txtar
      - integer-value-lands-unquoted.txtar
      - logs-one-line-when-a-vault-is-attached.txtar
      - macro-rendered-date-like-value-stays-a-string.txtar
      - malformed-append-pair-is-rejected.txtar
      - malformed-jinja-in-a-value-is-rejected.txtar
      - malformed-pair-is-rejected.txtar
      - missing-plan-file-is-rejected.txtar
      - newline-and-tab-bearing-values-round-trip.txtar
      - nothing-to-do-is-rejected.txtar
      - null-value-lands-unquoted.txtar
      - other-keys-comments-and-body-survive-the-set.txtar
      - pairs-removals-and-appends-combine-in-one-call.txtar
      - partly-numeric-value-stays-a-plain-string.txtar
      - remove-drops-a-key.txtar
      - re-setting-the-same-value-prints-no-diff.txtar
      - sets-a-key-to-a-literal-value.txtar
      - sets-multiple-keys-in-one-call.txtar
      - stubbed-macro-value-lands-typed.txtar
      - summary-goes-to-stderr-not-stdout.txtar
      - syntax-sensitive-string-keeps-its-quotes.txtar
      - unknown-macro-path-is-rejected.txtar
      - value-may-contain-equals-signs.txtar
      - yaml-1-1-boolean-word-stays-a-string.txtar
    gap_cases:
      - newline-and-tab-bearing-values-round-trip.txtar
      - malformed-append-pair-is-rejected.txtar
      - a-real-macro-runs-and-its-output-lands.txtar
    mutations_dir: vault/benchmarks/mutations/frontmatter-update-e2e
    mutations:
      command: mutation_e2e
      failure_pattern: "^FAILED\\s+(\\S+\\.txtar)"
    runs_dir: runs
    reports_dir: reports
    history_columns:
      [date, model, provider, outcome, att, code, agentic, review, diff, tokens, cache, cost, time, run]
    process:
      loop_threshold: 3
      edit_tools: [Write, Edit, NotebookEdit, write, edit]
      edit_input_keys: [content, new_string, new_source, edits]
      shell_tools: [Bash, bash]
      shell_input_key: command
      rebaseline_pattern: "--txtar-update"
      e2e_pattern: "just e2e|pytest[^\n]*\\be2e\\b"
      green_pattern: "\\b\\d+ passed\\b"
      red_pattern: "\\b\\d+ (failed|error)"
      malformed_patterns:
        - "InputValidationError"
        - "did not match the expected schema"
        - "Invalid tool parameter"
        - "missing required parameter"
        - "String to replace not found"
        - "has not been read yet"
      context_death_patterns:
        - "context (window |length )?(limit )?exceeded"
        - "prompt is too long"
        - "exceeds the maximum"
      context_death_stop_reasons: [max_tokens, context_overflow, length]
    cost:
      endpoint: https://openrouter.ai/api/v1/generation
      retries: 3
      backoff_seconds: 1.0
      concurrency: 8
      timeout_seconds: 30
    weights:
      code:
        gates:
          ci: 10
          determinism: 10
          scope: 10
          e2e: 5
          unit_deleted: 5
        corpus:
          mutation: 25
          recall: 15
          four_channel: 10
          gaps: 5
          wildcard: 5
      agentic:
        attempts: 30
        rebaseline: 20
        tool_discipline: 30
        churn: 20
      penalties:
        retry: 10
        rebaseline: 10
        malformed: 2
        loop: 5
        death: 10
      thresholds:
        wildcard_full_max: 0.05
        wildcard_zero_min: 0.3
        churn_full_max: 1.5
        churn_zero_min: 4.0
---

# Benchmark registry

This frontmatter is the machine-readable registry `bench-score` reads. Every benchmark run scores against one entry below; the runbook linked from each row is what a human follows.

A run is driven by `/playbook model-benchmark` ([`_playbooks/model-benchmark`](../_playbooks/model-benchmark/playbook.md)) — prepare, run, measure, publish — which resolves the model and the entry here and calls `bench-score` for every number it publishes. Driving a run by hand instead means following [guide.md](guide.md) step by step.

Every run develops in its own clone under the entry's `workspaces_dir`, never in a checkout anyone works in. Runs before 2026-08-14 predate that and were developed in a long-lived copy of the repo instead; their detail reports are unaffected, since a report records the branch and never the path it was built at.

| id | plan under test | branch scheme | runbook |
| --- | --- | --- | --- |
| `frontmatter-update-e2e` | `202608121417_frontmatter-update-e2e-migration` | `bench/{model_slug}` | [guide.md](guide.md) |

Scoring assets sit beside this file: [history.md](history.md) is the append-only scorecard table and [method.md](method.md) states what its columns mean and how a run is driven, `runs/` holds one machine-shaped detail report per run, `reports/` one human-readable run report written from it (rows from 2026-08-17 on link the report, which links its detail; earlier rows link their detail directly), `mutations/{id}/` holds the fixed patch set a corpus must kill, and `_fixtures/ndjson/` holds one hand-written synthetic log per process detector — a clean benchmark run never trips them, so they are how the detectors stay demonstrable. Run one with `bench-score process --benchmark {id} --ndjson _fixtures/ndjson/degenerate-loop.ndjson`: `degenerate-loop.ndjson` yields 1 loop and 0 malformed, `malformed-tool-inputs.ndjson` yields 2 malformed and 0 loops, the third tool error in it being an ordinary non-zero shell exit that must not count.

## Entry keys

- `source_repo`, `workspaces_dir`, `workspace_scheme` — a run is never developed in a checkout you work in. `prepare` clones `source_repo` into `{source_repo}/{workspaces_dir}/{workspace_scheme}` — one throwaway clone per run, `{workspace_id}` being prepare's own `YYYYMMDD-HHMMSS` stamp — and everything from the sprint to the diff review happens inside that clone. `workspaces_dir` is gitignored, so the clones never enter the source repo's index; they are disposable, and pruning one only costs the ability to re-read its worktree, the branch itself living on the remote.
- `push_remote` — the name and URL added to each clone, so the bench branch reaches GitHub for its pull request. A local clone inherits only `origin` pointing back at `source_repo`, which is not where pull requests live.
- `baseline` — the commit every run branches from; `plan`, `scope_allowlist`, `cases_dir` and `unit_file` are paths relative to the run's clone; `milestones_glob` is relative to the plan's directory.
- `commands` — every command `bench-score` runs inside the scored worktree, as `argv` plus an optional worktree-relative `cwd`. The script hardcodes none of them, so a benchmark on a differently-built repo only needs a different entry here.
- `bench-score --repo` — every subcommand takes the clone to score. Omitted, it falls back to `source_repo`, which only holds the branch after a `git fetch`; the playbook always passes the run's clone.
- `unit_grep` — the token whose absence from the repo proves the superseded unit file left no stale reference. `unit_grep_exclude` lists directories the sweep skips: the plan documents under `vault/` name the deleted file on purpose, so a hit there is not a stale reference.
- `etalon_cases` — the reference corpus frozen from the opus run (`dc0be24` + `0648787`); `gap_cases` are the subset with no pre-existing unit-test counterpart, the cases a model only writes by reading the CLI rather than by translating tests.
- `weights` — composite scoring weights as data. Each composite sums to 100: `code` splits 40 gates / 60 corpus, `agentic` splits across the four process signals. `penalties` are the per-incident deductions inside `attempts`, `rebaseline` and `tool_discipline`; `thresholds` are the ratio bands where `wildcard` and `churn` earn their full weight or nothing, interpolated linearly between. A layer that was not measured (no mutation run yet) drops out of the composite's denominator and is named in the run detail.
- `worker` and `logs_dir` — the agent every milestone briefing goes to, and where it writes one ndjson per attempt. `pi-developer` is the current worker: it drives a headless pi session, which reaches every provider pi has, so the model id in the briefing (`llama-local/…`, `openrouter/…`) selects both model and provider. A run names its logs `{ts}-{model_slug}-{milestone}.ndjson` through pi-developer's `-L` flag, which is what `select_logs` matches; `--since`/`--until` narrow the window further.
- `process` — how the worker's ndjson logs are read: which tools count as edits and where their payload sits, the regexes that recognise an e2e invocation and its green/red verdict, the `--txtar-update` marker, and the payload signatures that classify a tool error as a malformed input or a context death. `loop_threshold` is how many consecutive identical tool+input calls make a degenerate loop. Both harness schemas are read from one entry, which is why `edit_tools` and `shell_tools` list both vocabularies — Claude Code's `Write`/`Edit`/`Bash` and pi's `write`/`edit`/`bash`; `edit_input_keys` likewise covers pi's `edits` list of `{oldText, newText}` replacements alongside the string-valued keys. `bench-score` picks the schema per log file, so a run whose logs mix the two still profiles.
- `mutations_dir` and `mutations` — where the frozen patch set lives (relative to the repo holding this registry) and how a mutant is judged: `command` names the `commands` entry re-run once per patch, narrowed to the corpus under test, and `failure_pattern` is the regex whose first group pulls a failing case name out of that command's output, so a kill carries the names that caught it. The set is frozen per benchmark id — a new baseline is a new entry with its own directory, never a regeneration in place.
- `cost` — the OpenRouter generation endpoint plus the retry, concurrency and timeout budget for querying it. `--endpoint` overrides the URL per invocation. Logs carrying no OpenRouter generation id at all — a local model behind pi — are costed from the worker's own usage accounting instead, reported as source `worker-usage`.
- `runs_dir`, `reports_dir` and `history_columns` — where run detail reports and the human-readable run reports land (both relative to this file) and the exact column order of [history.md](history.md)'s table, so the emitted row cannot drift from its header. The history row links the report under `reports_dir`; the report links the detail under `runs_dir`, which `bench-score` still emits in its printed row before publish repoints it.
- `api_key_env` names the environment variable holding the OpenRouter token. The token itself is never config. It is read only when the logs actually carry generation ids to look up, so a local run needs no key.
