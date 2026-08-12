# pytest-txtar

Contract testing for command-line tools, driven by [txtar](https://pkg.go.dev/golang.org/x/tools/txtar)
archives: one file per case carrying the fixture tree, the invocation, and everything asserted about
the result — stdout, stderr, exit code, and files left behind.

Each case runs in a fresh sandbox; paths that vary per run are normalized to tokens before
comparison, and a golden-update flow rewrites assertions from the actual run.

The package is layered: `pytest_txtar.txtar` parses the archive format, the pytest-free core
(`case`, `sandbox`, `compare`, `update`) executes and compares cases parameterized by a
`TxtarSpec`, and a pytest plugin collects `*.txtar` files as test items.

Status: pre-release, under construction.

## Configuration

A consumer states what to run and where by implementing the `pytest_txtar_spec` hook in a
`conftest.py` beside its cases:

```python
from pathlib import Path

import pytest
from pytest_txtar.case import TxtarSpec

ROOT = Path(__file__).resolve().parents[1]


def pytest_txtar_spec(config: pytest.Config) -> TxtarSpec:
    return TxtarSpec(
        commands={"mytool": ROOT / "bin" / "mytool"},
        roots=("home", "xdg", "cwd"),
        cwd_root="cwd",
        env={"HOME": "home", "XDG_CONFIG_HOME": "xdg"},
    )
```

| Field | Meaning |
| --- | --- |
| `commands` | Command word → binary it resolves to, for the first word of a `cmd` line. |
| `roots` | Sandbox subdirectories a case may address under `fixtures/` and `expected/`. |
| `cwd_root` | The root the commands run in. |
| `env` | Environment variable → the root it is pointed at, on top of the ambient environment. |
| `tokens` | Root → normalization token; defaults to the upper-cased root in braces. |

The `home`/`xdg`/`cwd` roots above are one configuration, not a fixed set: a spec may name any roots
and bind any variables to them.

## Case format

This section defines the behavior; the package implements it. A runner in another language is
conformant when it agrees with everything below.

### Container — txtar

An archive is a leading comment followed by file sections. A section starts with a marker line
`-- name --`; everything up to the next marker line is its content.

- The marker line is exactly `--`, a space, the name, a space, `--`. Surrounding whitespace in the
  name is stripped; a name may contain `/`.
- A line whose name would be empty (`--  --`) is content, not a marker.
- Content that does not end in a newline is treated as if it did. A well-formed archive therefore
  round-trips byte-exactly through parse and serialize.
- A section name may appear only once per case; a repeat is a malformed case.
- There are no other syntax errors: any byte sequence parses.

### Sections

| Section | Required | Meaning |
| --- | --- | --- |
| `cmd` | yes | One command per line, run in order in the sandbox. |
| `exit` | no (default `0`) | Expected exit code of the last `cmd` line, as a decimal integer. |
| `stdout` | no | Expected stdout, normalized. |
| `stderr` | no | Expected stderr, normalized. |
| `fixtures/<root>/<path>` | no | File written under that sandbox root before the run. |
| `expected/<root>/<path>` | no | Expected content of that file after the run, normalized. |

`<root>` is one of the spec's `roots`, and `<path>` must stay inside it — an absent root, a bare
root with no path, or a path escaping through `..` is a malformed case.

Any other section name is a hard error — the case is malformed and collection fails. Unknown
sections are never ignored, so a typo (`stdOut`, `expect/cwd/x`) fails loudly instead of silently
asserting nothing.

Parent directories of a `fixtures/` path are created; an empty section creates an empty file.

### Sandbox

Each case runs in a fresh temporary directory holding one subdirectory per root in the spec. The
spec's `env` mapping points the named environment variables at those directories, and the commands
run in `cwd_root`.

Fixtures are materialized into the roots, then the `cmd` lines run. Nothing outside the sandbox is
read or written, and the sandbox is discarded after the case.

### Commands

Each `cmd` line is split with shell-like quoting and executed directly — there is no shell, so no
pipes, redirection, globbing or variable expansion. A first word listed in the spec's `commands`
mapping resolves to its configured binary path; any other first word is executed as given.

With more than one line:

- every line but the last must exit `0`; if one does not, the case fails;
- the last line's exit code is compared against `exit`;
- `stdout` and `stderr` are asserted against the concatenation of all lines' output, in order.

All lines share one sandbox, so a case can chain commands that build on each other's writes.

### Normalization

Before comparison, both sides are rewritten so that volatile values do not leak into the expected
text. Expected sections are written in normalized form.

Absolute sandbox paths in captured output are replaced by each root's token — `{HOME}` for the
`home` root by default, and whatever the spec's `tokens` mapping says otherwise.

Comparison is line by line. Within a line, the literal `[..]` matches any run of characters,
including none, and never crosses a line boundary — it covers commit hashes, timestamps and
durations. A line without `[..]` must match exactly, whitespace included.

Tokens and `[..]` apply to `stdout`, `stderr` and every `expected/` section. They are not expanded
in `cmd` or `fixtures/`, which are taken literally.

### Assertions

- An absent section asserts nothing. A case with no `stderr` section does not require stderr to be
  empty; a file with no `expected/` section is not checked.
- An absent `exit` asserts exit `0`.
- An `expected/` section for a file that does not exist fails the case.
- Files created beyond those named by `expected/` are not flagged.
- A failure that needs an unwritable path or another OS-level fault is not expressible — fixtures
  carry content, not permissions.

## Running

Cases collect as ordinary pytest items, one per `*.txtar` file, whose nodeid is the case path:

```
pytest tests/cases
pytest tests/cases -k smoke
```

Selection, parallelism, reporting and exit codes are pytest's. A failing case reports one labeled
unified diff per mismatched section; a malformed case is a collection error.

## Authoring a case

Write the comment, `cmd` and `fixtures/` sections by hand, then let the runner fill in the rest:

```
pytest tests/cases/my-case.txtar --txtar-update
```

`--txtar-update` rewrites each selected case whose assertions do not hold — its `stdout`, `stderr`,
`exit` and `expected/` sections come from the actual normalized run, `cmd` and `fixtures/` are left
untouched — and lists the rewritten cases in the terminal summary. A case that already passes is
never rewritten, so a holding `[..]` is not flattened into the run's literal text. Review the resulting diff as you would any other change —
a baseline is only as good as the reading it got. Re-running `--txtar-update` on an unchanged
corpus must produce no diff.

## Worked example

```txtar
Initializes a project from the template named in the user's config.

-- fixtures/xdg/mytool/config.yaml --
template: minimal
-- cmd --
mytool init demo
-- exit --
0
-- stdout --
created demo/ from template minimal (config: {XDG}/mytool/config.yaml)
-- expected/cwd/demo/mytool.yaml --
template: minimal
```

The fixture lands at `<sandbox>/xdg/mytool/config.yaml`, which the spec's `XDG_CONFIG_HOME` binding
makes the tool read as the user's config. The absolute path it echoes back is normalized to
`{XDG}`, while `demo` is relative to the working directory and needs no token. The trailing
`expected/cwd/` section asserts the file the run left behind.

## License

MIT. `src/pytest_txtar/txtar.py` is a port of `golang.org/x/tools/txtar` and carries the upstream
BSD-3-Clause notice — see [LICENSE](LICENSE).
