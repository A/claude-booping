# Framing brief

## Request

> groom: could you please refactor booping-python/e2e/run.py and other module related code. Now it just placed in the e2e dir, but i want it to be in, let's say {root}/textar-python as an independent module. Motivation: this tool can be reused in different projects. Another option to move it into a separate git repo and publish. Risks: the runner shouldn't be bound into the booping case, should be flexible, so can be used for different projects

## Task type

`refactoring` — internal structure change: the txtar contract runner moves out of `booping-python/e2e/` into an independent module, with the corpus behavior unchanged (`just e2e` keeps passing on the same cases). Not `feature`: no new user-facing capability in this project — reusability is a structural property, not new behavior. Not `bug`: nothing diverges from expected behavior today.

## Problem

The contract-corpus runner (`booping-python/e2e/run.py`, 360 lines, plus `_txtar.py` and the case-format spec in `e2e/README.md`) lives inside the booping repo's e2e directory and is hard-wired to booping: the binary under test is a fixed relative path (`../../bin/booping`), the sandbox roots (`home`, `xdg`, `cwd`) and normalization tokens (`{CWD}`, `{HOME}`, `{XDG}`) are module constants. The tool is generic in concept — txtar cases, sandboxed runs, normalized assertions, `--update` rebaselining — but cannot be reused in another project without copying and editing source. It must become an independent, project-agnostic module (working name `{root}/txtar-python`), with booping's e2e suite as its first consumer via configuration rather than hard-coded constants.

## Clarifications and Decisions

- Destination: separate git repo, published — booping consumes it as an external dependency.
- Name: `txtar-python`.
- Configuration surface: Python API — a small config object/entry point; booping keeps a thin `e2e/run.py` shim passing its constants (binary path, roots, tokens, normalizers).
- Booping wiring unchanged: cases stay in `booping-python/e2e/cases/`, `just e2e` entry identical, CI contract identical.
- Open for design: publish channel (PyPI vs git dependency in uv) and repo bootstrap ownership.
