# E2E Contract Corpus — Case Format Spec

This document defines the case file format. The Python runner (`run.py`) is the reference implementation; a runner in any language conforming to this spec produces equivalent results.

## File Layout

```
booping-python/e2e/
  run.py                    reference runner
  _txtar.py                 vendored txtar parser
  README.md                 this file
  cases/<command>/<name>.txtar
```

Each `.txtar` file is one test case using Go-style [`txtar`](https://pkg.go.dev/archive/tar#txtar) format: `-- section_name --` delimiters with plain-text content.

## Section Vocabulary

Every case file must contain a `cmd` section. All other sections are optional unless noted. Unknown section names are a **hard error** (runner exits 2).

### `cmd` (required)

One or more command lines, each executed as a subprocess in the same sandbox. All lines except the last must exit 0. The last line must match the `exit` section (default `0`).

When multiple lines are present, the `stdout` section asserts against the concatenation of all commands' stdout.

### `exit` (optional, default `0`)

Single line: the expected exit code for the last `cmd` line.

### `stdout` (optional)

Expected stdout of the command(s). Asserted only when present. Multi-line content is compared as a whole.

### `stderr` (optional)

Expected stderr. Asserted only when present.

### `fixtures/{home|xdg|cwd}/<path>`

Files materialized into the sandbox before any command runs. The `{home|xdg|cwd}` prefix maps to:

| Prefix | Sandbox path | Environment |
|--------|-------------|-------------|
| `fixtures/home/` | `$HOME/` | `HOME` set to sandbox `home/` |
| `fixtures/xdg/` | `$XDG_CONFIG_HOME/` | `XDG_CONFIG_HOME` set to sandbox `xdg/` |
| `fixtures/cwd/` | `<cwd>/<path>` | working directory set to sandbox `cwd/` |

Section names after the prefix become relative paths. Example: `fixtures/cwd/.booping` creates a `.booping` file in the sandbox working directory.

### `expected/{home|xdg|cwd}/<path>`

Files whose contents are asserted after the command(s) complete. Same sandbox prefix mapping as `fixtures`. If a listed path does not exist in the sandbox after execution, the case fails. Extra files not listed are not flagged.

Asserted only when the section is present. Absent sections imply no assertion.

## Absent-Section Rule

If a section is absent, no assertion is made for that dimension:

- No `exit` section → last command must exit 0.
- No `stdout` section → stdout is not compared.
- No `stderr` section → stderr is not compared.
- No `expected/` sections → no file assertions beyond `cmd` exit codes.

## Normalization

### Path Tokens

Output is normalized before comparison by replacing sandbox absolute paths with tokens:

| Token | Replaces |
|-------|----------|
| `{CWD}` | sandbox working directory |
| `{HOME}` | sandbox `$HOME` directory |
| `{XDG}` | sandbox `$XDG_CONFIG_HOME` directory |

Expected sections are written in normalized form. Actual output is normalized before comparison.

### `[..]` Wildcard

Within any expected line, `[..]` matches a non-empty span of characters (one or more). It is an in-line wildcard for volatile content like commit hashes or timestamps. Lines without `[..]` are compared literally.

## Runner

Invocation: `uv run python e2e/run.py [--update] [pattern...]`

- **pattern**: zero or more substrings matched against case paths relative to `cases/`. No patterns = run all cases.
- **`--update`**: rewrites each selected case's `stdout`, `stderr`, `exit`, and `expected/**` sections from the actual (normalized) run output. `cmd` and `fixtures/**` are untouched. Prints `updated {case}` per rewritten file. Exit 0.
- **stdout**: one `PASS {case}` / `FAIL {case}` line per case; failures include labeled unified diffs. Summary line: `{N} passed, {M} failed`.
- **stderr**: runner diagnostics only (malformed case: path + reason).

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All selected cases passed |
| 1 | At least one case failed |
| 2 | Malformed case file or no case matched a pattern |

## Authoring Loop

1. Write a case file with `cmd` and `fixtures/` sections.
2. Run `uv run python e2e/run.py --update <pattern>` to populate expected sections.
3. Inspect the updated case; adjust `cmd`/`fixtures` if needed.
4. Run `uv run python e2e/run.py <pattern>` to verify.
5. Commit the `.txtar` file.

## Language-Neutrality Contract

The `.txtar` case files define observable behavior. `run.py` is the reference implementation. A runner in any language that:

1. Materializes `fixtures/` into a sandbox with the specified environment,
2. Executes `cmd` lines as subprocesses,
3. Normalizes output with `{CWD}`/`{HOME}`/`{XDG}` tokens and `[..]` wildcards,
4. Compares against `stdout`/`stderr`/`exit`/`expected/` sections,

produces equivalent results.

## Worked Example

```txtar
Example: booping scaffold creates a minimal vault structure.

-- cmd --
booping scaffold plans/default_plan /index.md
-- exit --
0
-- stdout --
scaffolded 1 file:
  plans/default_plan/index.md
-- fixtures/xdg/booping/config.yaml --
core:
  scaffold:
    default_plan:
      - path: index.md
        frontmatter:
          title: "Default Plan"
          type: "feature"
-- expected/cwd/plans/default_plan/index.md --
---
title: "Default Plan"
type: "feature"
---

# Default Plan
```
