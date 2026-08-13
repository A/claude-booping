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

## Shipped content

A case may depend on plugin-shipped content only through its **existence, never its extent**. The
migration gate is the worked example: its notice is one line carrying the latest shipped migration
id, so `[..]` covers the id at a stable line count and the dependency reduces to "at least one
migration ships". A case that would break when a core playbook, skill or migration is *added* fails
the rule and is written differently.

## Unasserted output

Omitting a `stdout` section means **unasserted**, not empty — an assertion on emptiness is a `stdout`
section with no body. `debug-context` is the one command relying on this: its dump enumerates every
core playbook, skill and agent, so no wildcard survives a shipped-content addition, and its cases pin
exit code and stderr only. A case that omits `stdout` carries a comment saying why.

## Executable fixtures

A fixture section carries content, never permissions — a mode is not expressible in a case file. A
fixture that must be executable, such as a `playbook-transition` `script` hook, is made so by a
leading `cmd` line, since `cmd` lines run raw argv from the `cwd` root:

```
-- cmd --
chmod +x ../home/Claude/_playbooks/fx-hooks/_scripts/note
booping playbook-transition fx-hooks noted --workdir run
```

## Running

```
just e2e                 # the whole corpus
just e2e '<-k expr>'     # a subset, e.g. just e2e smoke
```

Rebaseline from `booping-python/`:

```
uv run pytest e2e --txtar-update [-k expr]
```
