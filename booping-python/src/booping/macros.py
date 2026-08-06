"""Config-declared argv macros, executed at render time.

A macro is an argv list at a dotted config path (`core.macros.date:
["date", "+%Y%m%d-%H-%M"]`), or a mapping carrying that list under `command:`
plus an optional `cwd:` of `repo` or `vault` naming the directory it runs in
(omitted → the process cwd). It runs through ``subprocess.run`` with
``shell=False``, so nothing a template supplies can be shell-interpreted.

The declared list is an argv *prefix*: a call site may append positional
arguments (`macro('core.macros.date', '+%H:%M')`), so a macro declared complete
(`["date", "+%Y%m%d-%H-%M"]`) and one declared partial (`["date"]`) are the
same shape.

Results are cached per argv tuple and resolved cwd for the life of the process: one subprocess
however many bodies ask the same way, and no two such calls in one render
straddling a minute boundary. Distinct arguments are distinct argv tuples and
so distinct runs — two formats of the same clock can disagree. A macro is
expected to be idempotent within one render; a macro that is not must not be
declared.
"""
from __future__ import annotations

import subprocess
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any, cast

from booping.utils import PathError, resolve_path

STUB_KEY = "macro_stubs"

NODE_KEYS = ("command", "cwd")
CWD_VALUES = ("repo", "vault")

_cache: dict[tuple[str, ...], str] = {}


class MacroError(Exception):
    """A macro could not be resolved or did not run."""


def clear_cache() -> None:
    _cache.clear()


def parse_stub_macros(pairs: Sequence[str]) -> dict[str, str]:
    """`core.macros.date=19700101-00-00` → `{"core.macros.date": "19700101-00-00"}`.

    The key stays a literal string (unlike `--set`, which nests it) and may
    carry the call's arguments after the path — `core.macros.date +%H:%M=00:00`.
    Split on the first `=`, so an argument containing one cannot be pinned.
    Raises ValueError carrying the offending pair when it has no `=`.
    """
    stubs: dict[str, str] = {}
    for pair in pairs:
        key, sep, value = pair.partition("=")
        if not sep or not key:
            raise ValueError(pair)
        stubs[key] = value
    return stubs


def parse_stub_overrides(pairs: Sequence[str]) -> dict[str, Any]:
    """The config fragment `--stub-macro` pairs merge in as, or `{}` for none."""
    stubs = parse_stub_macros(pairs)
    return {STUB_KEY: stubs} if stubs else {}


def _argv_list(value: Any, message: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise MacroError(message)
    return [str(item) for item in cast("list[Any]", value)]


def _resolve_mapping_node(node: Mapping[str, Any], dotted: str) -> tuple[list[str], str | None]:
    unknown = sorted(str(k) for k in node if str(k) not in NODE_KEYS)
    if unknown:
        raise MacroError(
            f"macro {dotted}: unknown key(s) {', '.join(unknown)}; "
            f"legal keys: {', '.join(NODE_KEYS)}"
        )
    if "command" not in node:
        raise MacroError(f"macro {dotted}: mapping node has no `command` argv list")
    argv = _argv_list(
        node["command"], f"macro {dotted}: `command` is not a non-empty argv list"
    )
    raw_cwd: Any = node.get("cwd")
    if raw_cwd is None:
        return argv, None
    cwd = str(raw_cwd)
    if cwd not in CWD_VALUES:
        raise MacroError(
            f"macro {dotted}: unknown cwd {cwd!r}; legal values: {', '.join(CWD_VALUES)}"
        )
    return argv, cwd


def resolve_argv(config: Mapping[str, Any], dotted: str) -> tuple[list[str], str | None]:
    """The argv list declared at *dotted* plus its `cwd` kind, or a :class:`MacroError`."""
    try:
        value: Any = resolve_path(dict(config), dotted)
    except PathError as exc:
        raise MacroError(f"no macro declared at config path: {dotted}") from exc
    if isinstance(value, dict):
        return _resolve_mapping_node(cast("dict[str, Any]", value), dotted)
    type_name = type(value).__name__
    return (
        _argv_list(value, f"macro {dotted} is a {type_name}, not a non-empty argv list"),
        None,
    )


def label(dotted: str, args: Sequence[str]) -> str:
    """How a call is named in diagnostics — path alone, or path plus its args."""
    return " ".join([dotted, *args])


def run_argv(dotted: str, argv: Sequence[str], cwd: Path | None = None) -> str:
    key = (str(cwd) if cwd is not None else "", *argv)
    cached = _cache.get(key)
    if cached is not None:
        return cached
    try:
        completed = subprocess.run(  # noqa: S603 — argv list, shell=False by default
            list(argv), capture_output=True, text=True, check=True, cwd=cwd
        )
    except FileNotFoundError as exc:
        raise MacroError(
            f"macro {dotted}: executable not found: {argv[0]}"
        ) from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or "").strip().splitlines()
        tail = f": {detail[-1]}" if detail else ""
        raise MacroError(
            f"macro {dotted}: command exited {exc.returncode}{tail}"
        ) from exc
    result = completed.stdout.strip()
    _cache[key] = result
    return result


def make_macro(
    config: object = None,
    *,
    repo_dir: Path | None = None,
    vault_dir: Path | None = None,
) -> Callable[..., str]:
    """The `macro` global a rendering env gets.

    Extra positional arguments append to the declared argv prefix.

    A node's `cwd:` resolves against *repo_dir* / *vault_dir*; a call site that
    knows neither still works until a macro asks for the directory it lacks.

    A `macro_stubs` mapping in config (written by `--stub-macro`) short-circuits
    the named paths to a literal without executing anything — what makes a render
    byte-reproducible. A stub key is either the path plus its arguments
    (`core.macros.date +%H:%M`), pinning one call, or the path alone, pinning every
    argument variant of that macro; the specific key wins.
    """
    cfg = cast("dict[str, Any]", config) if isinstance(config, dict) else {}
    raw_stubs: Any = cfg.get(STUB_KEY) or {}
    stubs: dict[str, str] = (
        {str(k): str(v) for k, v in cast("dict[Any, Any]", raw_stubs).items()}
        if isinstance(raw_stubs, dict)
        else {}
    )

    dirs: dict[str, Path | None] = {"repo": repo_dir, "vault": vault_dir}

    def resolve_cwd(keyed: str, kind: str | None) -> Path | None:
        if kind is None:
            return None
        directory = dirs[kind]
        if directory is None:
            raise MacroError(f"macro {keyed}: cwd: {kind} — no {kind} directory resolved")
        return directory

    def macro(path: str, *args: object) -> str:
        dotted = str(path)
        extra = [str(arg) for arg in args]
        keyed = label(dotted, extra)
        for key in (keyed, dotted):
            if key in stubs:
                return stubs[key]
        argv, cwd_kind = resolve_argv(cfg, dotted)
        return run_argv(keyed, [*argv, *extra], resolve_cwd(keyed, cwd_kind))

    return macro
