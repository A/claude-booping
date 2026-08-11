from __future__ import annotations

from typing import Any

import pytest

from booping.context.scaffold import (
    DirNode,
    FileNode,
    ScaffoldError,
    check_name,
    load,
    parse_node,
    resolve,
)

# ---------------------------------------------------------------------------
# check_name — the safety gate the command re-runs on rendered names
# ---------------------------------------------------------------------------

class TestCheckName:
    @pytest.mark.parametrize("name", ["a.md", "_references", "...", "a.b.c", "..hidden"])
    def test_accepts_a_plain_filename(self, name: str) -> None:
        check_name(name, "t.d")

    @pytest.mark.parametrize("name", ["a/b", "/abs", "trailing/", ".", ".."])
    def test_rejects_an_escaping_name(self, name: str) -> None:
        with pytest.raises(ScaffoldError) as exc:
            check_name(name, "t.d")
        assert exc.value.path == "t.d"
        assert repr(name) in str(exc.value)

# ---------------------------------------------------------------------------
# parse_node — valid shapes
# ---------------------------------------------------------------------------

class TestParseNode:
    def test_string_is_a_file_with_that_content(self) -> None:
        node = parse_node("hello\n", "a.md", "t.a.md")
        assert node == FileNode("a.md", "t.a.md", "hello\n")

    def test_mapping_without_type_is_a_dir(self) -> None:
        node = parse_node({"a.md": "A", "b.md": "B"}, "d", "t.d")
        assert node == DirNode(
            "d",
            "t.d",
            [FileNode("a.md", "t.d.a.md", "A"), FileNode("b.md", "t.d.b.md", "B")],
        )

    def test_children_keep_declaration_order(self) -> None:
        node = parse_node({"z": "", "a": "", "m": ""}, "d", "t.d")
        assert isinstance(node, DirNode)
        assert [c.name for c in node.children] == ["z", "a", "m"]

    def test_explicit_file_without_content_is_empty(self) -> None:
        node = parse_node({"type": "file"}, "a.md", "t.a.md")
        assert node == FileNode("a.md", "t.a.md", "")

    def test_explicit_file_carries_content(self) -> None:
        node = parse_node({"type": "file", "content": "x"}, "a.md", "t.a.md")
        assert node == FileNode("a.md", "t.a.md", "x")

    def test_explicit_dir_without_children_is_empty(self) -> None:
        node = parse_node({"type": "dir"}, "_references", "t._references")
        assert node == DirNode("_references", "t._references", [])

    def test_explicit_dir_carries_children(self) -> None:
        node = parse_node({"type": "dir", "children": {"a.md": "A"}}, "d", "t.d")
        assert node == DirNode(
            "d", "t.d", [FileNode("a.md", "t.d.children.a.md", "A")]
        )

    def test_three_levels_of_nesting(self) -> None:
        raw: dict[str, Any] = {
            "one": {
                "two": {
                    "three": {"leaf.md": "deep"},
                },
            },
        }
        node = parse_node(raw, "root", "t")
        assert node == DirNode(
            "root",
            "t",
            [
                DirNode(
                    "one",
                    "t.one",
                    [
                        DirNode(
                            "two",
                            "t.one.two",
                            [
                                DirNode(
                                    "three",
                                    "t.one.two.three",
                                    [FileNode("leaf.md", "t.one.two.three.leaf.md", "deep")],
                                )
                            ],
                        )
                    ],
                )
            ],
        )


# ---------------------------------------------------------------------------
# parse_node — invalid shapes
# ---------------------------------------------------------------------------

class TestParseNodeErrors:
    def test_null_names_both_fixes(self) -> None:
        with pytest.raises(ScaffoldError) as exc:
            parse_node(None, "a.md", "t.a.md")
        assert exc.value.path == "t.a.md"
        assert '""' in str(exc.value)
        assert "{}" in str(exc.value)

    @pytest.mark.parametrize(
        ("value", "found"),
        [([1, 2], "list"), (3, "int"), (True, "bool"), (1.5, "float")],
    )
    def test_other_scalars_report_path_and_type(self, value: Any, found: str) -> None:
        with pytest.raises(ScaffoldError) as exc:
            parse_node(value, "a", "t.a")
        assert exc.value.path == "t.a"
        assert found in str(exc.value)

    def test_nested_error_carries_the_nested_path(self) -> None:
        with pytest.raises(ScaffoldError) as exc:
            parse_node({"one": {"two": None}}, "root", "t")
        assert exc.value.path == "t.one.two"

    @pytest.mark.parametrize("key", ["a/b", "/abs", ".", ".."])
    def test_unsafe_filename_key(self, key: str) -> None:
        with pytest.raises(ScaffoldError) as exc:
            parse_node({key: ""}, "root", "t.d")
        assert exc.value.path == "t.d"
        assert repr(key) in str(exc.value)

    def test_unsafe_filename_key_under_explicit_children(self) -> None:
        with pytest.raises(ScaffoldError) as exc:
            parse_node({"type": "dir", "children": {"../x": ""}}, "d", "t.d")
        assert exc.value.path == "t.d.children"

    def test_unknown_type(self) -> None:
        with pytest.raises(ScaffoldError) as exc:
            parse_node({"type": "symlink"}, "a", "t.a")
        assert exc.value.path == "t.a.type"

    def test_non_string_content(self) -> None:
        with pytest.raises(ScaffoldError) as exc:
            parse_node({"type": "file", "content": 3}, "a", "t.a")
        assert exc.value.path == "t.a.content"

    def test_non_mapping_children(self) -> None:
        with pytest.raises(ScaffoldError) as exc:
            parse_node({"type": "dir", "children": ["a"]}, "d", "t.d")
        assert exc.value.path == "t.d.children"


# ---------------------------------------------------------------------------
# resolve
# ---------------------------------------------------------------------------

class TestResolve:
    def test_resolves_a_nested_path(self) -> None:
        cfg: dict[str, Any] = {"playbook": {"scaffold": {"a.md": "A"}}}
        assert resolve(cfg, "playbook.scaffold") == {"a.md": "A"}

    def test_missing_segment_names_path_and_segment(self) -> None:
        cfg: dict[str, Any] = {"playbook": {}}
        with pytest.raises(ScaffoldError) as exc:
            resolve(cfg, "playbook.scaffold.deep")
        assert exc.value.path == "playbook.scaffold.deep"
        message = str(exc.value)
        assert "'playbook.scaffold.deep'" in message
        assert "'scaffold'" in message

    def test_segment_under_a_scalar_names_path_and_segment(self) -> None:
        cfg: dict[str, Any] = {"playbook": "not-a-tree"}
        with pytest.raises(ScaffoldError) as exc:
            resolve(cfg, "playbook.scaffold")
        assert exc.value.path == "playbook.scaffold"
        assert "'scaffold'" in str(exc.value)

    def test_empty_path(self) -> None:
        with pytest.raises(ScaffoldError):
            resolve({}, "")


# ---------------------------------------------------------------------------
# load
# ---------------------------------------------------------------------------

class TestLoad:
    def test_parses_the_tree_at_the_path(self) -> None:
        cfg: dict[str, Any] = {
            "playbook": {
                "scaffold": {
                    "playbook.md": "---\nname: x\n---\n",
                    "_references": {"type": "dir"},
                }
            }
        }
        root = load(cfg, "playbook.scaffold")
        assert root == DirNode(
            "",
            "playbook.scaffold",
            [
                FileNode(
                    "playbook.md",
                    "playbook.scaffold.playbook.md",
                    "---\nname: x\n---\n",
                ),
                DirNode("_references", "playbook.scaffold._references", []),
            ],
        )

    @pytest.mark.parametrize(
        ("value", "found"),
        [("a string", "str"), ([1], "list"), (3, "int"), (True, "bool"), (None, "null")],
    )
    def test_non_tree_value_names_path_and_type(self, value: Any, found: str) -> None:
        cfg: dict[str, Any] = {"playbook": {"scaffold": value}}
        with pytest.raises(ScaffoldError) as exc:
            load(cfg, "playbook.scaffold")
        assert exc.value.path == "playbook.scaffold"
        message = str(exc.value)
        assert "'playbook.scaffold'" in message
        assert found in message

    def test_root_declared_as_a_file_is_not_a_tree(self) -> None:
        cfg: dict[str, Any] = {"playbook": {"scaffold": {"type": "file", "content": "x"}}}
        with pytest.raises(ScaffoldError) as exc:
            load(cfg, "playbook.scaffold")
        assert exc.value.path == "playbook.scaffold"
        assert "directory" in str(exc.value)
