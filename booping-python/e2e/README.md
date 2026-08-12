# Contract corpus — case format

One txtar file per case under `cases/<command>/`. A case carries its fixture tree, the
invocation, and everything asserted about the result: stdout, stderr, exit code, and files left
behind.

**Language-neutrality contract**: this file defines the behavior. `run.py` is the reference
implementation, not the specification — where the two disagree, `run.py` is the bug. A runner in
another language is conformant when it agrees with everything below.

## Container — txtar

An archive is a leading comment followed by file sections. A section starts with a marker line
`-- name --`; everything up to the next marker line is its content.

- The marker line is exactly `--`, a space, the name, a space, `--`. Surrounding whitespace in the
  name is stripped; a name may contain `/`.
- A line whose name would be empty (`--  --`) is content, not a marker.
- Content that does not end in a newline is treated as if it did. A well-formed archive therefore
  round-trips byte-exactly through parse and serialize.
- A section name may appear only once per case; a repeat is a malformed case.
- There are no other syntax errors: any byte sequence parses.

`_txtar.py` implements this.

## Sections

| Section | Required | Meaning |
| --- | --- | --- |
| `cmd` | yes | One command per line, run in order in the sandbox. |
| `exit` | no (default `0`) | Expected exit code of the last `cmd` line, as a decimal integer. |
| `stdout` | no | Expected stdout, normalized. |
| `stderr` | no | Expected stderr, normalized. |
| `fixtures/home/<path>` | no | File written under the sandbox's `HOME` before the run. |
| `fixtures/xdg/<path>` | no | File written under the sandbox's `XDG_CONFIG_HOME`. |
| `fixtures/cwd/<path>` | no | File written under the sandbox's working directory. |
| `expected/home/<path>` | no | Expected content of that file after the run, normalized. |
| `expected/xdg/<path>` | no | Same, under `XDG_CONFIG_HOME`. |
| `expected/cwd/<path>` | no | Same, under the working directory. |

Any other section name is a hard error — the case is malformed and the run aborts. Unknown sections
are never ignored, so a typo (`stdOut`, `expect/cwd/x`) fails loudly instead of silently asserting
nothing.

Parent directories of a `fixtures/` path are created; an empty section creates an empty file.

## Sandbox

Each case runs in a fresh temporary directory holding three roots:

| Root | Bound to |
| --- | --- |
| `home/` | `$HOME` |
| `xdg/` | `$XDG_CONFIG_HOME` |
| `cwd/` | the process working directory |

Fixtures are materialized into those roots, then the `cmd` lines run. Nothing outside the sandbox is
read or written, and the sandbox is discarded after the case.

## Commands

Each `cmd` line is split with shell-like quoting and executed directly — there is no shell, so no
pipes, redirection, globbing or variable expansion. A leading `booping` word resolves to this
repository's `bin/booping`.

With more than one line:

- every line but the last must exit `0`; if one does not, the case fails;
- the last line's exit code is compared against `exit`;
- `stdout` and `stderr` are asserted against the concatenation of all lines' output, in order.

All lines share one sandbox, so a case can chain commands that build on each other's writes.

## Normalization

Before comparison, both sides are rewritten so that volatile values do not leak into the expected
text. Expected sections are written in normalized form.

Absolute sandbox paths in captured output are replaced by tokens:

| Token | Path |
| --- | --- |
| `{CWD}` | the sandbox's `cwd/` |
| `{HOME}` | the sandbox's `home/` |
| `{XDG}` | the sandbox's `xdg/` |

Comparison is line by line. Within a line, the literal `[..]` matches any run of characters,
including none, and never crosses a line boundary — it covers commit hashes, timestamps and
durations. A line without `[..]` must match exactly, whitespace included.

Tokens and `[..]` apply to `stdout`, `stderr` and every `expected/` section. They are not expanded
in `cmd` or `fixtures/`, which are taken literally.

## Assertions

- An absent section asserts nothing. A case with no `stderr` section does not require stderr to be
  empty; a file with no `expected/` section is not checked.
- An absent `exit` asserts exit `0`.
- An `expected/` section for a file that does not exist fails the case.
- Files created beyond those named by `expected/` are not flagged.
- A command whose failure needs an unwritable path or another OS-level fault (`booping` exit `2`) is
  not expressible — fixtures carry content, not permissions. That coverage is an accepted gap.

## Runner

```
uv run python e2e/run.py [--update] [pattern...]
```

Run from `booping-python/`. Cases are discovered as `cases/**/*.txtar`. Each *pattern* is a
substring matched against a case path relative to `cases/`; with no pattern, every case runs.

Stdout is one `PASS {case}` or `FAIL {case}` line per case, each `FAIL` followed by labeled unified
diffs — one per mismatched section — and a final `{N} passed, {M} failed` summary. Stderr carries
runner diagnostics only: a malformed case reports its path and reason.

| Exit | Meaning |
| --- | --- |
| `0` | every selected case passed |
| `1` | at least one case failed |
| `2` | a case file is malformed, or a pattern matched no case |

## Authoring a case

Write the comment, `cmd` and `fixtures/` sections by hand, then let the runner fill in the rest:

```
uv run python e2e/run.py --update cases/scaffold/my-case.txtar
```

`--update` rewrites each selected case's `stdout`, `stderr`, `exit` and `expected/` sections in
place from the actual normalized run, leaves `cmd` and `fixtures/` untouched, prints one
`updated {case}` line per rewritten file, and exits `0`. Review the resulting diff as you would any
other change — a baseline is only as good as the reading it got. Re-running `--update` on an
unchanged corpus must produce no diff.

## Worked example

`cases/scaffold/creates-tree-from-global-config.txtar`:

```txtar
Scaffolds a one-file tree from the global config tier into a fresh destination.

-- fixtures/xdg/booping/config.yaml --
demo:
  README.md: "hello {{ name }}\n"
-- cmd --
booping scaffold demo out --set name=world
-- exit --
0
-- stdout --
created dir out
--- /dev/null
+++ out/README.md
@@ -0,0 +1 @@
+hello world
scaffolded 2 paths — 1 dirs created, 1 files created, 0 files overwritten
-- expected/cwd/out/README.md --
hello world
```

The fixture lands at `<sandbox>/xdg/booping/config.yaml`, which the three-tier config merge picks up
as the global tier. `dest` is relative, so the receipt lines carry relative paths and need no token.
The trailing `expected/cwd/` section asserts the rendered file, `--set` and all.
