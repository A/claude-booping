from typing import Any


def deep_merge(
    base: dict[str, Any],
    override: dict[str, Any],
    shallow_merge_keys: list[str] | None = None,
) -> dict[str, Any]:
    """Recursively merge `override` into `base`, returning a new dict.

    Default behaviour: dict values recurse, scalars and lists replace wholesale.

    `shallow_merge_keys`: container keys whose dict values are shallow-merged —
    each child of the override's value replaces the matching child in base
    instead of recursing further. Use for id-keyed collections whose entries
    are atomic (e.g. `agents` — flipping one field on an entry must restate
    the rest of that entry).
    """
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
