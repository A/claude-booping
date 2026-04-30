# CLI

`bin/booping` is the single entry point to the plugin's Python tooling. It is a thin shell wrapper around `uv run --project booping-python booping ...`, so every subcommand resolves the plugin root from the wrapper's own location and runs in the bundled uv environment.

You normally do not call `bin/booping` directly — skill bodies invoke `booping render ...` at load time, and `just docs` / `just build` wrap the build subcommands. The cases where you reach for the CLI yourself are debugging, manual rebuilds, and force-refreshing `sprints.md`.

## Subcommands

### `render`

Render a Jinja2 template with the full project context to stdout (or to a file).

```text
bin/booping render <template-path> [--output <path>]
```

- **`<template-path>`** — path to a `.j2` template. Resolved relative to the plugin root if not absolute.
- **`--output <path>`** — write to file; parent directories are created. Without `--output`, output goes to stdout.

When to use: rendering a runtime skill template by hand to inspect the output (`bin/booping render src/templates/skills/groom.md.j2`), or rendering the runtime-only `plan_lifecycle_overview` doc.

### `render-sprints`

Regenerate `~/Claude/{project}/sprints.md` from the project's plan files using `src/templates/sprints.md.j2`.

```text
bin/booping render-sprints [--output <path>]
```

- **`--output <path>`** — write to a different path; `--output -` writes to stdout. Default is the resolved vault's `sprints.md`.

Requires a project context (a directory with a `.booping` marker somewhere up the tree). Exits with code `2` if no project resolves.

When to use: force-refresh `sprints.md` after a manual frontmatter edit or status flip. `/chat` calls this on every orient, so most of the time you do not need to.

### `build`

Render every `src/files/**/*.j2` template to its plugin-root destination using `src/config_files.yaml`. This is the build step that materialises the on-disk skill and agent shells.

```text
bin/booping build
```

No arguments. Walks `src/files/` recursively, renders each `*.j2` to the matching path with the suffix stripped (e.g. `src/files/skills/groom/SKILL.md.j2` → `skills/groom/SKILL.md`), and prints the count of files written.

When to use: after editing any template under `src/files/` or any value under `src/config_files.yaml`. `just build` wraps it; `just dev` watches and re-runs on change.

### `debug-context`

Dump the assembled `Context` as YAML — the same context every skill renders against.

```text
bin/booping debug-context
```

No arguments. Output is YAML on stdout. Plan / lesson / retro / template bodies are summarised as `<N lines>` to keep the dump readable; everything else (config, project metadata, plan frontmatter, lesson and template paths) is rendered in full.

When to use: verifying that a project-local override in `~/Claude/{project}/config.yaml` deep-merged the way you expected, or troubleshooting why a skill is rendering an unexpected value. See [Project config](project_config.md#verifying-the-merged-config).

### `debug-template`

Reserved for rendering a template alongside its assembled context for side-by-side troubleshooting.

```text
bin/booping debug-template
```

Registered as a subcommand but not yet wired up — invoking it currently exits with `not implemented: debug-template`. Use `bin/booping render <template>` plus a separate `bin/booping debug-context` in the meantime.
