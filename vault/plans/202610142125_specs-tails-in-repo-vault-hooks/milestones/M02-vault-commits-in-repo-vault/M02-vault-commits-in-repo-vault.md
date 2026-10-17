---
id: "02"
title: "Vault-commit hooks commit an in-repo vault, vault paths only"
sp: 8
status: done
plan: "vault/plans/202610142125_specs-tails-in-repo-vault-hooks/index.md"
---

# M02: Vault-commit hooks commit an in-repo vault, vault paths only

Every plugin-shipped vault-commit hook commits through one shared stdlib helper that detects the repo with `git rev-parse --is-inside-work-tree` and commits only the paths the hook names, so an in-repo vault gets its commits and unrelated staged repo changes stay out of them.

**Scope:**

- New `playbooks/_scripts/_vault_git.py` — stdlib-only module, not a hook (hooks resolve by exact name, nothing calls `_vault_git.py`). Two functions:

  ```python
  def inside_git_worktree(vault: Path) -> bool:
      """The vault may be a subdirectory of a larger repository — ask git."""
      ...

  def commit_paths(vault: Path, paths: list[str], message: str) -> str | None:
      """None when the vault is in no git work tree; otherwise "ok" or "nothing to commit".
      Stages `paths` (vault-relative), then commits only them."""
      ...
  ```

  `commit_paths` runs `git -C {vault} add -- {paths}` (`check=True`), then `git -C {vault} commit -q -m {message} --only -- {paths}` with `capture_output=True`; return code 0 → `"ok"`, else `"nothing to commit"`. A failing `git add` raises `CalledProcessError` uncaught — the hook exits non-zero and the transition aborts, exactly as the hooks' `check=True` add does today; only the commit's return code is absorbed. `--only` with pathspecs commits those paths' working-tree content and leaves every other staged entry staged and uncommitted (checked on git 2.56).
- The four hooks import it and drop their own repo test and git calls. Each prepends the shared `_scripts` dir to `sys.path` from its own location, then `from _vault_git import commit_paths`:
  - `playbooks/_scripts/close-working-set` — `Path(__file__).resolve().parent`; delete its private `_inside_git_worktree`.
  - `playbooks/groom/_scripts/commit-plan`, `playbooks/code-review/_scripts/close-code-review`, `playbooks/retro/_scripts/drop-plan` — `Path(__file__).resolve().parents[2] / "_scripts"`.
- Each hook keeps its own printed summary wording: `None` maps to today's no-repo output (`commit-plan` keeps `; no vault git repo`, the others print no `vault-commit:` suffix), a string maps to `; vault-commit: {outcome}`. Commit messages are unchanged.
- Update each touched script's module docstring where it says "self-contained" / "nothing outside the standard library is imported" so it names the shared `_vault_git` helper (still stdlib-only).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Shared helper `inside_git_worktree` + `commit_paths` | `playbooks/_scripts/_vault_git.py` | 2 | done |
| 2.2 | Route the four hooks through `commit_paths`; drop the `.git`-exists tests and `_inside_git_worktree` copy | `playbooks/_scripts/close-working-set`, `playbooks/groom/_scripts/commit-plan`, `playbooks/code-review/_scripts/close-code-review`, `playbooks/retro/_scripts/drop-plan` | 3 | done |
| 2.3 | Regression tests: each hook against a vault nested in a git repo and against a vault that is its own repo | `booping-python/tests/scripts/vault_commit_test.py` | 3 | done |

## Definition of Done

### Task 2.1

- [x] `playbooks/_scripts/_vault_git.py` exists, imports only the standard library, and defines `inside_git_worktree` and `commit_paths` with the signatures above.
- [x] `commit_paths` passes `--only --` and the paths to `git commit`; the commit's stdout/stderr never reaches the hook's stdout.

### Task 2.2

- [x] `rg -n '"\.git"' playbooks` prints nothing; `rg -n "_inside_git_worktree" playbooks` prints nothing.
- [x] `rg -ln "commit_paths" playbooks` lists exactly the four hooks plus `_vault_git.py`.
- [x] No hook runs `git add` or `git commit` itself (`rg -n '"commit", "-q"|"add",' playbooks` matches only `_vault_git.py`).
- [x] `booping-python/tests/scripts/close_code_review_test.py` passes unchanged.
- [x] `booping-python/e2e/cases/playbook-transition/a-parked-groom-run-cancels-through-the-in-spec-superstate.txtar` passes unmodified (its fixture is in no git repo, so `commit-plan` still exits 0 on the no-repo branch).

### Task 2.3

- [x] New `booping-python/tests/scripts/vault_commit_test.py` runs each hook as a subprocess the way `booping playbook-transition` does (cwd and `BOOPING_WORKDIR` per the hook's docstring, `BOOPING_ARTIFACT` where the hook reads it), with real `git` in `tmp_path` (`git init`, local `user.name`/`user.email`).
- [x] Parametrized over the four hooks × two layouts: **nested** — `tmp_path/repo` is the git repo, the vault is `repo/vault`, plus a staged unrelated change `repo/src/x.txt`; **own repo** — the vault itself is the git repo.
- [x] Nested layout asserts: a new commit exists whose `git show --name-only HEAD` lists only paths under `vault/` that the hook names; `src/x.txt` is still staged and absent from HEAD. Own-repo layout asserts: a new commit exists with the hook's paths.
- [x] One case per layout asserts a second run with no changes leaves HEAD where it was and prints `vault-commit: nothing to commit` (use `close-code-review` with `plan: null`).
- [x] Mental mutation check: restoring a `(vault / ".git").exists()` gate in any hook fails its nested case; dropping `--only` fails the staged-`src/x.txt` assertion.
- [x] Tests are named after the outcome (`test_nested_vault_commit_carries_only_vault_paths`, …), not the mechanism.
- [x] Worker's final reply: only the list of changed files.

## References

- `booping-python/tests/scripts/close_code_review_test.py` — how a hook is run as a subprocess with `BOOPING_WORKDIR` / `BOOPING_ARTIFACT`, and its vault fixture shape.
- `playbooks/_scripts/close-working-set` lines 103–110 — the rev-parse test `inside_git_worktree` moves out of.
- `booping-python/src/booping/commands/playbook_transition.py` lines 244–260 — how hook scripts are resolved and with which env/cwd.

## Verify

```
cd booping-python && uv run pytest tests/scripts -q
```
