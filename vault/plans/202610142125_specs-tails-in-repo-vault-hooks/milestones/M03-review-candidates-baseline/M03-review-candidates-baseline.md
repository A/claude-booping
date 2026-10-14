---
id: "03"
title: "code-review candidates show the plan's baseline commit"
sp: 2
status: done
plan: "vault/plans/202610142125_specs-tails-in-repo-vault-hooks/index.md"
---

# M03: code-review candidates show the plan's baseline commit

The `scope_candidates` query selects `commit`, so the code-review scope step's **Baseline** column shows each plan's `commit:` and falls back to `— none` only when it is null.

**Scope:** the template `playbooks/code-review/scope/opus-5.md:16` already renders `{{ plan.commit or "— none" }}`; the query never fetched `commit`, so the fallback always fired. Fix is data only:

- `src/config.yaml` — `core.code_review_playbook.queries.scope_candidates.columns` becomes `[sp, title, code_reviews, commit]`.
- `documentation/project_config.md` — the restated `scope_candidates` block (around line 154) gets the same `columns:` line.

The committed report `playbooks/code-review/_reports/output.md` drifts by exactly the three candidate rows; the runner accepts it (not the worker).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Add `commit` to the `scope_candidates` columns | `src/config.yaml` | 1 | done |
| 3.2 | Mirror the columns line in the config reference | `documentation/project_config.md` | 1 | done |

## Definition of Done

### Task 3.1

- [x] `bin/booping config-get core.code_review_playbook.queries.scope_candidates.columns` prints a list containing `commit`.
- [x] `just snapshots` drifts only `playbooks/code-review/_reports/output.md`, and only its three **Plans eligible for review** rows: the Baseline cell of `19700101-widget-search` becomes `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`, `19700102-login-timeout` becomes `bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`, `19700103-session-cleanup` becomes `cccccccccccccccccccccccccccccccccccccccc`. Tests: the committed snapshot is the regression check (integration tier); no new unit test.
- [x] The worker does not run `just snapshots-accept` and writes nothing under `_reports/`.

### Task 3.2

- [x] `rg -n "columns: \[sp, title, code_reviews" documentation/project_config.md src/config.yaml` shows `commit` on both lines.
- [x] Worker's final reply: only the list of changed files.

## References

- `playbooks/code-review/scope/opus-5.md` — the consumer of `plan.commit` (do not modify).
- `playbooks/_fixtures/vault/plans/19700101-widget-search/index.md` — fixture plan carrying `commit:`.

## Verify

```
just snapshots
```
