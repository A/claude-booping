"""Config-declared argv macros, executed at render time.

A macro is an argv list at a dotted config path (`macros.now:
["date", "+%Y%m%d-%H-%M"]`). It runs through ``subprocess.run`` with
``shell=False``, so nothing a template supplies can be shell-interpreted.

Results are cached per argv tuple for the life of the process: one subprocess
however many bodies ask, and no two calls in one render straddling a minute
boundary. A macro is therefore expected to be idempotent within one render; a
macro that is not must not be declared.
"""
from __future__ import annotations

import subprocess
from collections.abc import Callable, Mapping, Sequence
from typing import Any, cast

from booping.utils import PathError, resolve_path

STUB_KEY = "macro_stubs"

_cache: dict[tuple[str, ...], str] = {}


class MacroError(Exception):
    """A macro could not be resolved or did not run."""


def clear_cache() -> None:
    _cache.clear()


def parse_stub_macros(pairs: Sequence[str]) -> dict[str, str]:
    """`macros.now=19700101-00-00` → `{"macros.now": "19700101-00-00"}`.

    The key stays a literal dotted string (unlike `--set`, which nests it).
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


def resolve_argv(config: Mapping[str, Any], dotted: str) -> list[str]:
    """The argv list declared at *dotted*, or a :class:`MacroError`."""
    try:
        value: Any = resolve_path(dict(config), dotted)
    except PathError as exc:
        raise MacroError(f"no macro declared at config path: {dotted}") from exc
    type_name = type(value).__name__
    if not isinstance(value, list) or not value:
        raise MacroError(
            f"macro {dotted} is a {type_name}, not a non-empty argv list"
        )
    return [str(item) for item in cast("list[Any]", value)]


def run_argv(dotted: str, argv: Sequence[str]) -> str:
    key = tuple(argv)
    cached = _cache.get(key)
    if cached is not None:
        return cached
    try:
        completed = subprocess.run(  # noqa: S603 — argv list, shell=False by default
            list(argv), capture_output=True, text=True, check=True
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


def make_macro(config: object = None) -> Callable[[str], str]:
    """The `macro` global a rendering env gets.

    A `macro_stubs` mapping in config (written by `--stub-macro`) short-circuits
    the named paths to a literal without executing anything — what makes a render
    byte-reproducible.
    """
    cfg = cast("dict[str, Any]", config) if isinstance(config, dict) else {}
    raw_stubs: Any = cfg.get(STUB_KEY) or {}
    stubs: dict[str, str] = (
        {str(k): str(v) for k, v in cast("dict[Any, Any]", raw_stubs).items()}
        if isinstance(raw_stubs, dict)
        else {}
    )

    def macro(path: str) -> str:
        dotted = str(path)
        if dotted in stubs:
            return stubs[dotted]
        return run_argv(dotted, resolve_argv(cfg, dotted))

    return macro
