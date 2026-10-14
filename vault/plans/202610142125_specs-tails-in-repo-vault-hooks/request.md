# Request

> Request — specs tails and two vault-hook bugs (small, one plan):
> 1. `booping-python/src/booping/specs/records.py` keeps its own frontmatter splitter; the shared `booping.context._yaml.split_frontmatter` / `parse_frontmatter` is now fixed (closing delimiter only on a `---` line, `UnclosedFrontmatterError`). Make specs use the shared helper; keep the specs check messages and line numbers (frontmatter_error_line) as the e2e cases pin them.
> 2. Vault-commit hooks report `ok` but commit nothing when the vault lives inside the project repo (`.booping` `vault_path: vault`, like this repo): seen in groom's and code-review's exit hooks (`playbooks/_scripts/close-working-set` and whatever groom uses). Find the cause and make vault commits work for an in-repo vault (stage only vault paths, never unrelated repo changes).
> 3. code-review's list of plans eligible for review showed `— none` as the baseline of a plan whose `commit:` was set (plan 202610141731). Find the query and fix it.

## Task type

`bug` — two of three items are observed behaviour diverging from expected (in-repo vault commits silently skipped; a set `commit:` rendered as `— none`), and item 1 is a small dedup riding along. Not `feature`: no new user-facing capability is added. Not `refactoring`: the dominant work changes observable behaviour (commits land, baselines show); item 1 alone would be a refactoring, but it is too small to own the plan.

## Problem

1. `specs/records.py` duplicates the frontmatter splitter and its unclosed-block error that `booping.context._yaml` now owns; two copies of the delimiter rule can drift. After the change specs loads frontmatter through `split_frontmatter` / `UnclosedFrontmatterError`, and `booping specs check` prints the same messages and line numbers as today (the `e2e/cases/specs/check-frontmatter-*` cases are the contract).
2. With the vault inside the project repo, the vault-commit hooks on groom's and code-review's terminal edges exit `ok` but leave the vault changes uncommitted. They must commit the vault's changes into the project repo, staging only paths under the vault, never unrelated working-tree changes. Out-of-repo vaults (own git repo) keep today's behaviour.
3. code-review's eligible-plans list renders `— none` as the baseline of a plan whose `commit:` frontmatter is set. It must render the plan's baseline commit.

## Clarifications and Decisions

- Autonomous run: the owner is unavailable; every default this run takes is recorded in `clarifications.md` as an answered question.
- One plan, no split — the three items are small and independent.
