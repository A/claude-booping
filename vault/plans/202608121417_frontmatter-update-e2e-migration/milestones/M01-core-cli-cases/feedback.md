**Blocked (1/2)**: The 17 authored txtar cases were left untracked in the working tree — no commit was made on `bench/qwen3-8-27b-reasoning-medium`, so the milestone delivered nothing to the branch.

What was checked: `git status` on the workspace shows `booping-python/e2e/cases/frontmatter-update/` as an untracked directory and `git log` carries no worker commit past the baseline `a025189`. The reported verify verdict (`uv run pytest e2e -k frontmatter -q` → 17 passed, no rewrites) is taken as given and was not re-run.

What the next attempt must do: keep the existing case files as they stand — they are the work, do not re-author them — and commit them on branch `bench/qwen3-8-27b-reasoning-medium` with a conventional-commit message scoped to the milestone. Stage only `booping-python/e2e/cases/frontmatter-update/`; the plan directory under `vault/` is the runner's bookkeeping and must stay out of the commit. Report the commit sha in the return.
