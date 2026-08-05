# Set the project up

The run's context report carries the project-initialized flag and the previous step reports the resolved home dir — the flag picks the branch below. Nothing here is resolved at render time: read every fact at run time, from the report or from a shell call.

Gather in one batch before anything else:

- `git rev-parse --show-toplevel` — the repo root, and the source of the name candidates (its basename, kebab-cased). A non-zero exit means the repo is not under git; the cwd is the root then.
- `booping config-get home_dir` — the home dir, printed raw and unexpanded; expand `~` yourself.
- `ls {home_dir}` — the project names already taken.

## The project is not initialized

Ask first, write after.

1. **Location and name**, one `AskUserQuestion` call: where the vault lives — in the repo (default `./booping`) or under the home dir at `{home_dir}/{name}` — and what the project is called, with candidates from the repo directory name. Say so when a candidate is already taken under the home dir.
2. **Marker visibility**, a second `AskUserQuestion` call: tracked in git, hidden in `.gitignore` (visible to the team), or hidden in `.git/info/exclude` (invisible to the team). Skipped entirely when the vault lives in the repo, and when the repo is not under git.

Then, in order:

3. `booping scaffold vault.scaffold {vault_dir}` — the vault tree: `plans/`, `retrospectives/`, `_lessons/`, `_booping/`, `notes/` and a `.gitignore`. It takes no `--set` variables. A non-empty destination exits 1; ask before re-running it with `--force` (0 success, 1 user error, 2 OSError). `booping-create-project` is a different path and is not what this step calls.
4. `{repo_root}/.booping` — `project_name: {name}` always, plus `vault_path: {dir}` resolved against the repo root when the vault lives in the repo.
5. Repo-local vault only: `{home_dir}/{name}` as a symlink to the absolute vault dir. The scaffold tree cannot make it — it declares directories and text files only — so create it here.
6. The visibility answer: append `.booping` to `{repo_root}/.gitignore` or to `{repo_root}/.git/info/exclude`. Tracked, or the question skipped → neither file is touched.
7. `booping render-sprints`, run from the repo root so it resolves the marker just written and honours `vault_path:`. Idempotent.

## The project is already initialized

Report the wiring first — read it from the marker and the filesystem, never from memory:

```text
Project `claude-booping` is already set up.
  vault:  /home/anton/Dev/claude-booping/booping (in the repo)
  marker: .booping — project_name: claude-booping, vault_path: booping
  link:   ~/Claude/claude-booping -> booping/
```

Then offer the change routes via `AskUserQuestion`: move the vault, rename the project, merge it into another project, or change nothing. The routes are **offered, not scripted** — act on the user's call plus what this run already knows. A rename moves three things together: the vault directory, the marker's `project_name` and the home-dir symlink. Changing nothing writes nothing, and the report above is then the whole outcome.

## Hard rules

- Every decision is the user's, taken in-step via `AskUserQuestion`. Nothing is inferred silently, and nothing outside the vault, the marker and the symlink is written.
- There is no attach route — never wire the repo to a vault this run did not create.
- Stack detection and `_booping/` extension seeding are out of scope.

{% include "_partials/step_return.md" %}
