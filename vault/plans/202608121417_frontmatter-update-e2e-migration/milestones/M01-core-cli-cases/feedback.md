**Blocked (1/2)**: `## Verify` red — 15/16 cases pass, `log-when-vault-attached.txtar` fails: the command exits 1 with "plan not found" in the sandbox, so no log line is written.

What was checked: worker's commit `fe9a788` adds 16 txtar cases under `booping-python/e2e/cases/frontmatter-update/`; `uv run pytest e2e -k frontmatter` reports 1 failure.

What was wrong: the failing case's fixture tree does not resolve a project/vault the way the passing scaffold case `logs-are-appended-when-a-project-is-attached` (or similarly named log case) under `booping-python/e2e/cases/scaffold/` does. The worker guessed at marker placement instead of replicating the working scaffold log case's exact fixture layout (`.booping` marker location, `vault/` tree, `project_name`, and the plan-path argument relative to the sandbox cwd).

What the next attempt must do:
- Open the scaffold corpus log case and copy its fixture structure byte-for-byte (marker, config, directory roots), changing only the invoked command to `booping frontmatter-update` against a plan file placed inside that same resolved tree.
- The plan path passed on the command line must resolve from the sandbox cwd — inspect a passing scaffold case to see which root the cwd maps to.
- Rebaseline expected output with `uv run pytest e2e --txtar-update -k frontmatter` from `booping-python/`, then run `uv run pytest e2e -k frontmatter` and get 16/16 green.
- Land the fix as a new commit; never amend.
