Setup takes a repo from any starting state to a working booping project: a booping config with a resolved `home_dir` at the machine level, then a scaffolded vault, `.booping` marker and, for a repo-local vault, a home-dir symlink at the project level. Every phase already satisfied on entry is detected and skipped rather than redone, so a re-run on a fully set-up project reports the state instead of changing it. The run is ephemeral — it lives in this one conversation, has no persisted state and nothing to resume — and a cancelled run leaves the machine and the repo untouched.

## Shared instructions

- Never write angle-bracket placeholders (`<name>`, `<path>`) into a file or a chat reply. Obsidian
  reads them as HTML tags and stops rendering the block that holds them. Write `{name}`, `{path}`.
- Never manually break markdown lines. Write each paragraph, bullet, or table row as one line and
  let the renderer wrap it — hard line breaks turn into mid-sentence breaks after any later edit.

## Playbook Steps

Execute the steps in the most effective order considering their dependencies.

| Step | Dependencies | Summary | Review gate |
| --- | --- | --- | --- |
| `setup-booping` | — | Settle the machine level — when booping is not yet initialized, ask the preferred home dir (default `~/Claude/`) and create the machine config; either way make the home dir exist as a git repo. | — |
| `setup-project` | `setup-booping` | Settle the project level — ask location, name and marker visibility, then scaffold the vault tree, write the `.booping` marker, and symlink a repo-local vault into the home dir; when the project is already wired, report it and offer the change routes. | — |

## Step: Setup Booping
# Set booping up on this machine

The run's context report carries the booping-initialized flag and, when booping is initialized, the machine's configured home dir. The flag picks the branch below and is the only thing that answers *whether* booping is configured: `booping config-get home_dir` always prints a value — the core default `~/Claude/` when no config exists — so it answers only *what* the home dir is.

## Branch: already initialized

Read the resolved value back with `booping config-get home_dir` and report it. The config is never edited, re-pointed or reformatted. Still make the home dir exist and be a git repo, per **Home dir** below — an existing config says nothing about the directory.

## Branch: not initialized

Ask the user for the preferred home dir through `AskUserQuestion` — one question, `~/Claude/` as the default option, any other path accepted as free input. Nothing is written until the answer arrives.

Then create `${XDG_CONFIG_HOME:-~/.config}/booping/config.yaml`, parent directories included, holding the answer as its only key — verbatim and unexpanded, `~` left as the user typed it:

```yaml
home_dir: ~/Claude/
```

Read the value back with `booping config-get home_dir` and report it.

## Home dir

The home dir is one git repository covering every vault under it — `booping vault-commit` runs git from inside a vault and relies on that enclosing repo. Create and initialize it, expanding `~` yourself; both commands are no-ops when they already hold:

```bash
mkdir -p {home_dir}
git -C {home_dir} rev-parse --git-dir >/dev/null 2>&1 || git -C {home_dir} init
```

Report which of the two actually did something. A home dir that already sits inside another git repo is left alone — say so rather than nesting a second one.

## Return format

Close with this block and nothing after it. All three sections, in this order, each present even
when it has no entries — no `(none)` placeholder, no prose around them.

```
## Changed:

- [CREATED|UPDATED|DELETED] {vault-relative path} — {one line, what changed}

## Notes:

- {one line the user or a later step needs}

## Questions:

1. {question answerable in one line}
```

## Step: Setup Project
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

3. `booping scaffold core.setup_playbook.scaffold {vault_dir}` — the vault tree: `plans/`, `retrospectives/`, `_lessons/`, `_booping/`, `notes/`, a `sprints.md` Bases view and a `.gitignore`. It takes no `--set` variables. A non-empty destination exits 1; ask before re-running it with `--force` (0 success, 1 user error, 2 OSError). `booping-create-project` is a different path and is not what this step calls.
4. `{repo_root}/.booping` — `project_name: {name}` always, plus `vault_path: {dir}` resolved against the repo root when the vault lives in the repo. Then, from the repo root, `booping marker-set latest_migration=@latest` — a fresh vault is already current, and without the key every render reports it behind.
5. Repo-local vault only: `{home_dir}/{name}` as a symlink to the absolute vault dir. The scaffold tree cannot make it — it declares directories and text files only — so create it here.
6. The visibility answer: append `.booping` to `{repo_root}/.gitignore` or to `{repo_root}/.git/info/exclude`. Tracked, or the question skipped → neither file is touched.

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

## Return format

Close with this block and nothing after it. All three sections, in this order, each present even
when it has no entries — no `(none)` placeholder, no prose around them.

```
## Changed:

- [CREATED|UPDATED|DELETED] {vault-relative path} — {one line, what changed}

## Notes:

- {one line the user or a later step needs}

## Questions:

1. {question answerable in one line}
```
