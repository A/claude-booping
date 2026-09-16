# Tracker contract corpus

One txtar case per file under `cases/<verb>/`, run by the
[pytest-txtar](https://github.com/A/pytest-txtar) plugin — that README is the case-format
specification (sections, sandbox, normalization, `[..]` wildcard, authoring flow). `cases/cli/`
holds the cases that belong to no single verb: the global flags and the parser's own failures.

`conftest.py` supplies the tracker's configuration:

| Spec field | Value |
| --- | --- |
| `commands` | `booping-tracker` → the repository's `bin/booping-tracker` |
| `roots` | `home`, `xdg`, `cwd` |
| `cwd_root` | `cwd` |
| `env` | `HOME` → `home`, `XDG_CONFIG_HOME` → `xdg` |
| tokens | `{HOME}`, `{XDG}`, `{CWD}` (the defaults) |

A case that names no `--config-file` resolves `core.tracker` by shelling to `bin/booping`, which
reads the same sandboxed `cwd`, `home` and `xdg` roots.

## Running

```
just e2e                 # the whole corpus, both projects
just e2e '<-k expr>'     # a subset
```

Rebaseline from `booping-tracker/`:

```
uv run pytest e2e --txtar-update [-k expr]
```
