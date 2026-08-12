# Contract corpus

One txtar case per file under `cases/<command>/`, run by the
[pytest-txtar](https://github.com/A/pytest-txtar) plugin — that README is the case-format specification
(sections, sandbox, normalization, `[..]` wildcard, authoring flow).

`conftest.py` supplies booping's configuration:

| Spec field | Value |
| --- | --- |
| `commands` | `booping` → the repository's `bin/booping` |
| `roots` | `home`, `xdg`, `cwd` |
| `cwd_root` | `cwd` |
| `env` | `HOME` → `home`, `XDG_CONFIG_HOME` → `xdg` |
| tokens | `{HOME}`, `{XDG}`, `{CWD}` (the defaults) |

The `xdg` root is the config merge's global tier, `home` its `~`, and `cwd` the directory commands
run in.

## Running

```
just e2e                 # the whole corpus
just e2e '<-k expr>'     # a subset, e.g. just e2e smoke
```

Rebaseline from `booping-python/`:

```
uv run pytest e2e --txtar-update [-k expr]
```
