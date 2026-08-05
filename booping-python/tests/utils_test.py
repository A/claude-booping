from typing import Any

import pytest

from booping.utils import PathError, deep_merge, resolve_path


class TestResolvePath:
    def test_returns_the_value_at_a_nested_path(self) -> None:
        cfg: dict[str, Any] = {"a": {"b": {"c": 42}}}
        assert resolve_path(cfg, "a.b.c") == 42

    def test_missing_segment_names_segment_and_walked_prefix(self) -> None:
        cfg: dict[str, Any] = {"a": {"b": {}}}
        with pytest.raises(PathError) as exc:
            resolve_path(cfg, "a.b.c")
        assert exc.value.dotted_path == "a.b.c"
        assert exc.value.segment == "c"
        assert exc.value.walked == "a.b"
        assert exc.value.found_type is None
        assert "'c'" in str(exc.value)
        assert "'a.b.c'" in str(exc.value)

    def test_segment_under_a_scalar_reports_the_found_type(self) -> None:
        cfg: dict[str, Any] = {"a": "scalar"}
        with pytest.raises(PathError) as exc:
            resolve_path(cfg, "a.b")
        assert exc.value.segment == "b"
        assert exc.value.walked == "a"
        assert exc.value.found_type == "str"

    def test_empty_path_raises(self) -> None:
        with pytest.raises(PathError):
            resolve_path({}, "")


def test_deep_merge_recurses_into_nested_dicts() -> None:
    base = {"a": {"b": 1, "c": 2}}
    override = {"a": {"c": 99, "d": 3}}
    assert deep_merge(base, override) == {"a": {"b": 1, "c": 99, "d": 3}}


def test_deep_merge_lists_replace_wholesale() -> None:
    base = {"x": [1, 2, 3]}
    override = {"x": [9]}
    assert deep_merge(base, override) == {"x": [9]}


def test_deep_merge_scalars_replace() -> None:
    assert deep_merge({"a": 1, "b": 2}, {"a": 99}) == {"a": 99, "b": 2}


def test_deep_merge_does_not_mutate_base() -> None:
    base = {"a": {"b": 1}}
    override = {"a": {"c": 2}}
    _ = deep_merge(base, override)
    assert base == {"a": {"b": 1}}


def test_shallow_merge_keys_replace_children_per_id() -> None:
    """Containers named in `shallow_merge_keys` get per-child replacement —
    each child of the override's value replaces the matching child verbatim;
    base-only children survive."""
    base = {
        "agents": {
            "a": {"internal": True, "good_for": ["one"]},
            "b": {"internal": True, "good_for": ["two"]},
        }
    }
    override = {"agents": {"a": {"type": "cli", "command": "x"}}}
    merged = deep_merge(base, override, shallow_merge_keys=["agents"])
    assert merged["agents"]["a"] == {"type": "cli", "command": "x"}
    assert merged["agents"]["b"] == {"internal": True, "good_for": ["two"]}


def test_shallow_merge_keys_does_not_affect_other_keys() -> None:
    """Keys not named in `shallow_merge_keys` continue to deep-merge."""
    base = {"agents": {"a": {"internal": True}}, "other": {"x": 1, "y": 2}}
    override = {"agents": {"a": {"type": "cli"}}, "other": {"y": 99}}
    merged = deep_merge(base, override, shallow_merge_keys=["agents"])
    assert merged["agents"] == {"a": {"type": "cli"}}
    # `other` deep-merged.
    assert merged["other"] == {"x": 1, "y": 99}


def test_shallow_merge_keys_works_at_any_nesting_depth() -> None:
    """`shallow_merge_keys` matches by key name anywhere during recursion,
    not by absolute path."""
    base = {"core": {"develop_playbook": {"agents": {"a": {"internal": True}}}}}
    override = {"core": {"develop_playbook": {"agents": {"a": {"type": "cli"}}}}}
    merged = deep_merge(base, override, shallow_merge_keys=["agents"])
    assert merged["core"]["develop_playbook"]["agents"]["a"] == {"type": "cli"}


def test_shallow_merge_keys_none_behaves_like_pure_deep_merge() -> None:
    base = {"agents": {"a": {"internal": True, "good_for": ["one"]}}}
    override = {"agents": {"a": {"type": "cli"}}}
    merged = deep_merge(base, override)
    # Without shallow flag, the agent entry deep-merges — internal survives.
    assert merged["agents"]["a"] == {"internal": True, "good_for": ["one"], "type": "cli"}
