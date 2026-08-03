from collections.abc import Sequence
from typing import Any


def parse_set_overrides(pairs: Sequence[str]) -> dict[str, Any]:
    """`a.b=c` → `{"a": {"b": "c"}}`, accumulated later-wins across pairs. Values stay
    strings. Raises ValueError carrying the offending pair when it has no `=`.
    """
    overrides: dict[str, Any] = {}
    for pair in pairs:
        key, sep, value = pair.partition("=")
        if not sep:
            raise ValueError(pair)
        nested: dict[str, Any] = {}
        cursor = nested
        parts = key.split(".")
        for part in parts[:-1]:
            child: dict[str, Any] = {}
            cursor[part] = child
            cursor = child
        cursor[parts[-1]] = value
        overrides = deep_merge(overrides, nested)
    return overrides


def deep_merge(
    base: dict[str, Any],
    override: dict[str, Any],
    shallow_merge_keys: list[str] | None = None,
) -> dict[str, Any]:
    shallow_keys = set(shallow_merge_keys or [])
    result: dict[str, Any] = dict(base)
    for key, val in override.items():
        base_val: Any = result.get(key)
        if isinstance(base_val, dict) and isinstance(val, dict):
            if key in shallow_keys:
                # Shallow-merge: each child of override replaces base's child verbatim.
                shallow: dict[str, Any] = dict(base_val)  # type: ignore[arg-type]
                for child_key, child_val in val.items():  # type: ignore[misc]
                    shallow[child_key] = child_val
                result[key] = shallow
            else:
                # type: ignore because isinstance narrowing produces
                # dict[Unknown, Unknown] in basedpyright strict mode for Any values.
                result[key] = deep_merge(base_val, val, shallow_merge_keys)  # type: ignore[arg-type]
        else:
            result[key] = val
    return result
