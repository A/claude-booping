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

{% include "_partials/step_return.md" %}
