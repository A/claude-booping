---
benchmarks:
  - id: frontmatter-update-e2e
    repo: /home/anton/Dev/@A/claude-booping-local-bench
    baseline: e0d1796
    plan: vault/plans/202608121417_frontmatter-update-e2e-migration/index.md
    branch_scheme: bench/{model_slug}
    worker: openrouter-developer
    logs_dir: ~/.tmp/openrouter-developer
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
---

# Benchmark registry

This frontmatter is the machine-readable registry `bench-score` reads. Every benchmark run scores against one entry below; the runbook linked from each row is what a human follows.

| id | plan under test | branch scheme | runbook |
| --- | --- | --- | --- |
| `frontmatter-update-e2e` | `202608121417_frontmatter-update-e2e-migration` | `bench/{model_slug}` | [guide.md](guide.md) |

Scoring assets sit beside this file: [history.md](history.md) is the append-only scorecard table, `runs/` holds one detail report per run, `mutations/{id}/` holds the fixed patch set a corpus must kill.

## Entry keys

- `baseline` — the commit every run branches from; `plan`, `scope_allowlist`, `cases_dir` and `unit_file` are paths relative to `repo`; `milestones_glob` is relative to the plan's directory.
- `commands` — every command `bench-score` runs inside the scored worktree, as `argv` plus an optional worktree-relative `cwd`. The script hardcodes none of them, so a benchmark on a differently-built repo only needs a different entry here.
- `unit_grep` — the token whose absence from the repo proves the superseded unit file left no stale reference. `unit_grep_exclude` lists directories the sweep skips: the plan documents under `vault/` name the deleted file on purpose, so a hit there is not a stale reference.
- `etalon_cases` — the reference corpus frozen from the opus run (`dc0be24` + `0648787`); `gap_cases` are the subset with no pre-existing unit-test counterpart, the cases a model only writes by reading the CLI rather than by translating tests.
- `weights` — composite scoring weights as data. Each composite sums to 100: `code` splits 40 gates / 60 corpus, `agentic` splits across the four process signals.
- `api_key_env` names the environment variable holding the OpenRouter token. The token itself is never config.
