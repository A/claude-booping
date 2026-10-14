---
title: "Specs tails and in-repo vault hooks — shared frontmatter splitter, vault commits,
  review baseline"
type: "bug"
status: in-progress
sp: 12
related_to: null
created: 2026-10-14 21:26
planned: null
started: 2026-10-14 21:37
completed: null
code_reviews: []
sessions:
- a07e88d4-8835-40cb-89ab-80a93a6d3fdb
- a9ee126f-d8cb-4dd2-a9b1-14922499c384
retro: null
summary: Specs reuse the shared frontmatter splitter; vault-commit hooks work 
  for an in-repo vault; review baseline shows commit
commit: 1fc868204f7c2fa4ca6e53e766d66e9938388331
tracker_provider: null
tracker_request: null
tracker_issue: null
return_to: null
agents:
  research-codebase: adb2303da067e50bc
  cross-review: a836e3e0b34be7c5c
reviewed_at: 2026-10-14 21:36
---

# Specs tails and in-repo vault hooks — shared frontmatter splitter, vault commits, review baseline

## Context

- **Current state** — (1) `booping-python/src/booping/specs/records.py` keeps a private frontmatter regex, error class and splitter beside the shared, now-fixed `booping.context._yaml.split_frontmatter` / `UnclosedFrontmatterError`. (2) Three vault-commit hooks — `groom/_scripts/commit-plan:41`, `code-review/_scripts/close-code-review:123`, `retro/_scripts/drop-plan:49` — gate the commit on `(vault / ".git").exists()`, which is false for an in-repo vault (`.booping` `vault_path: vault`), so they skip the commit and exit 0, and `playbook-transition` reports `script …: ok`. Reproduced in this run: the `framing → researching` edge printed `script commit-plan: ok` and committed nothing. `_scripts/close-working-set` was fixed by 4b90729 with a `rev-parse` test, but only there. All four commit without a pathspec, so in a nested vault they would also sweep any unrelated staged repo change into the vault commit. (3) `src/config.yaml` `core.code_review_playbook.queries.scope_candidates` selects `[sp, title, code_reviews]`; `code-review/scope/opus-5.md:16` renders `plan.commit or "— none"`, so the Baseline cell is always `— none` (the committed report pins it for three fixture plans that all carry `commit:`).
- **Motivation** — in-repo vaults lose groom, code-review and retro history silently; review scope shows no diff base; the duplicated splitter can drift from the fixed one.
- **Scope** — the three fixes above with regression coverage. Not in scope: changing what `playbook-transition` prints for a hook (it reports the exit status), commit message wording, develop's runner-side commits.

## Decisions

- **Shared vault-commit helper**: one stdlib module `playbooks/_scripts/_vault_git.py` (`inside_git_worktree`, `commit_paths`) imported by all four hooks via `sys.path` from the script's own location — the earlier fix landed in one copy of four, which is the drift a single source prevents (value/0003). Alternative: a `booping vault-commit` CLI subcommand — rejected, the hooks are deliberately stdlib-only and do not shell back into `booping`.
- **Commit only named paths**: `git commit --only -- {paths}` after `git add -- {paths}` — keeps unrelated staged repo changes out of the vault commit in a nested vault, harmless for a vault that is its own repo. Alternative: refuse to commit when the index holds other staged paths — rejected, it would skip the commit whenever the user has staged work.
- **Repo detection**: `git -C {vault} rev-parse --is-inside-work-tree` — asks git instead of stat'ing `.git`, the test `close-working-set` already uses.
- **Specs splitter**: `records.py` reuses `split_frontmatter` and the message of `UnclosedFrontmatterError`; its YAML-error line arithmetic stays, because the shared regex hands YAML the same text after the opening line.
- **Review baseline**: add `commit` to the query's `columns` — data-only fix; the template is already right.

## Architecture

- Hooks run via `booping playbook-transition` (`booping-python/src/booping/commands/playbook_transition.py:244-260`, resolution by exact name: playbook `_scripts/` first, then the discovery roots' `_scripts/`), so a non-hook `_vault_git.py` in `playbooks/_scripts/` is never invoked as a hook.
- `commit-plan` derives the vault as `BOOPING_WORKDIR/../..`; the other three take `BOOPING_WORKDIR` as the vault root. Paths passed to `commit_paths` are vault-relative and used with `git -C {vault}`, so they resolve inside the nested repo correctly.
- The scope step's query feeds the `review_candidates` table through the `| query` filter; the committed report `playbooks/code-review/_reports/output.md` renders it over `playbooks/_fixtures/vault/`.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [Specs records load frontmatter through the shared splitter](milestones/M01-specs-shared-frontmatter-splitter/M01-specs-shared-frontmatter-splitter.md) | 2 | done |
| 02 | [Vault-commit hooks commit an in-repo vault, vault paths only](milestones/M02-vault-commits-in-repo-vault/M02-vault-commits-in-repo-vault.md) | 8 | pending |
| 03 | [code-review candidates show the plan's baseline commit](milestones/M03-review-candidates-baseline/M03-review-candidates-baseline.md) | 2 | pending |

## Implementation Order

M01, M02 and M03 are independent; run them in id order.

## Key Files Reference

| File | Role |
|------|------|
| `booping-python/src/booping/context/_yaml.py` | shared frontmatter splitter M01 adopts |
| `playbooks/_scripts/_vault_git.py` | new shared vault-commit helper (M02) |
| `booping-python/tests/scripts/close_code_review_test.py` | shape of hook subprocess tests |
| `src/config.yaml` | `scope_candidates` query (M03) |
| `playbooks/code-review/_reports/output.md` | committed report that drifts in M03 |

## Final Verification

- [ ] `just ci` is green.
- [ ] `just snapshots` drift is limited to the three Baseline cells M03 names; the runner accepts it with `just snapshots-accept code-review` under this run's snapshot policy and lists it in `develop-defaults.md`.
- [ ] `tests/scripts/vault_commit_test.py` is green inside `just ci` — it, not a live transition, proves nested-vault commits: the installed plugin runs hooks from its own checkout, not this worktree.

## Testing Strategy

N/A — deterministic. Regression checks: M01 the five `e2e/cases/specs/check-frontmatter-*` cases; M02 new `tests/scripts/vault_commit_test.py` (real git, nested and own-repo vaults); M03 the committed code-review report.

## Deployment / config impact

| Env var / config | docker-compose / deploy | terraform / infra | CI workflow |
|------------------|-------------------------|-------------------|-------------|
| `core.code_review_playbook.queries.scope_candidates.columns` gains `commit` | N/A | N/A | N/A |

## Authorization / data access

N/A — no endpoints or tenant data.

## Out of scope

- `playbook-transition` reporting a hook's own stdout instead of `ok` on exit 0.
- Conventional-commit prefixes for vault commits (`groom: …`, `codereview: …` stay as they are).
- Any user-tier playbook's own `_scripts/` (e.g. this vault's `_playbooks/`) — they may adopt `_vault_git` later.

## CLAUDE.md impact

No CLAUDE.md changes required — it already says vault commits are each playbook's own business via `script` hooks; the helper changes no documented contract.
