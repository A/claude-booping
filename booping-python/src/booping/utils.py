from collections.abc import Sequence
from typing import Any, cast

# A plan is a directory carrying its body at this filename; the directory name is
# the slug.
DIR_PLAN_NAME = "index.md"


class PathError(Exception):
    """Raised when a dotted path does not resolve in a mapping.

    Carries the structured pieces of the failure so each caller can phrase its
    own message: the full ``dotted_path``, the ``segment`` that did not
    resolve, the ``walked`` prefix that did, and ``found_type`` — the type name
    of the non-mapping value the walk stopped on, or ``None`` when the segment
    was simply missing.
    """

    __slots__ = ("dotted_path", "found_type", "segment", "walked")

    def __init__(
        self,
        dotted_path: str,
        message: str,
        *,
        segment: str = "",
        walked: str = "",
        found_type: str | None = None,
    ) -> None:
        super().__init__(message)
        self.dotted_path = dotted_path
        self.segment = segment
        self.walked = walked
        self.found_type = found_type


def resolve_path(config: dict[str, Any], dotted_path: str) -> Any:
    """Return the merged-config value at *dotted_path*.

    Raises :class:`PathError` naming the first segment that does not resolve.
    """
    if not dotted_path:
        raise PathError(dotted_path, "empty config path")

    current: Any = config
    walked = ""
    for segment in dotted_path.split("."):
        if not isinstance(current, dict):
            found = type(current).__name__
            raise PathError(
                dotted_path,
                f"no value at {dotted_path!r} — {walked!r} is a {found}, not a mapping, "
                f"so segment {segment!r} cannot resolve",
                segment=segment,
                walked=walked,
                found_type=found,
            )
        node = cast("dict[str, Any]", current)
        if segment not in node:
            raise PathError(
                dotted_path,
                f"no value at {dotted_path!r} — segment {segment!r} is missing",
                segment=segment,
                walked=walked,
            )
        current = node[segment]
        walked = f"{walked}.{segment}" if walked else segment
    return current


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
