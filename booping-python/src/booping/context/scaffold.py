"""Scaffold tree parser — a config sub-tree into a validated file/dir node tree.

Operates on the merged config: a dotted path addresses a mapping whose entries
are a directory's children.  Pure logic — no disk reads, no rendering; seed
content is carried verbatim as declared.

Node encoding:

===============================  ==========================================
Config value                     Meaning
===============================  ==========================================
string                           File; the string is its content
mapping without ``type``         Directory; entries are its children
``{type: file}``                 File; optional ``content`` (absent → empty)
``{type: dir}``                  Directory; optional ``children``
===============================  ==========================================

Anything else — ``null``, a list, a number, a bool — is a
:class:`ScaffoldError` reported against the offending node's dotted path.
"""
from __future__ import annotations

from typing import Any, cast

from booping.utils import PathError, resolve_path

TYPE_KEY = "type"
CONTENT_KEY = "content"
CHILDREN_KEY = "children"

_TYPE_FILE = "file"
_TYPE_DIR = "dir"


class ScaffoldError(Exception):
    """Raised for any malformed scaffold tree, carrying the dotted config path
    of the offending node in :attr:`path`."""

    __slots__ = ("path",)

    def __init__(self, path: str, message: str) -> None:
        super().__init__(f"{path}: {message}")
        self.path = path


# ---------------------------------------------------------------------------
# Node representation
# ---------------------------------------------------------------------------

class Node:
    """Base for a scaffold node. ``path`` is the dotted config path it came from."""

    __slots__ = ("name", "path")

    def __init__(self, name: str, path: str) -> None:
        self.name = name
        self.path = path


class FileNode(Node):
    """A file with literal (unrendered) seed content."""

    __slots__ = ("content",)

    def __init__(self, name: str, path: str, content: str = "") -> None:
        super().__init__(name, path)
        self.content = content

    def __repr__(self) -> str:  # pragma: no cover
        return f"FileNode(name={self.name!r}, path={self.path!r}, content={self.content!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FileNode):
            return NotImplemented
        return self.name == other.name and self.path == other.path and self.content == other.content

    def __hash__(self) -> int:
        return hash((self.name, self.path, self.content))


class DirNode(Node):
    """A directory and its children, in declaration order."""

    __slots__ = ("children",)

    def __init__(self, name: str, path: str, children: list[Node] | None = None) -> None:
        super().__init__(name, path)
        self.children: list[Node] = children or []

    def __repr__(self) -> str:  # pragma: no cover
        return f"DirNode(name={self.name!r}, path={self.path!r}, children={self.children!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DirNode):
            return NotImplemented
        return (
            self.name == other.name
            and self.path == other.path
            and self.children == other.children
        )

    def __hash__(self) -> int:
        return hash((self.name, self.path, tuple(self.children)))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _join(path: str, segment: str) -> str:
    return f"{path}.{segment}" if path else segment


def _type_name(value: object) -> str:
    return type(value).__name__


def _check_name(name: str, parent_path: str) -> None:
    if "/" in name or name in {".", ".."}:
        raise ScaffoldError(parent_path, f"unsafe filename key {name!r}")


def _parse_children(raw: dict[str, Any], path: str) -> list[Node]:
    children: list[Node] = []
    for key, value in raw.items():
        name = str(key)
        _check_name(name, path)
        children.append(parse_node(value, name, _join(path, name)))
    return children


def _parse_mapping(raw: dict[str, Any], name: str, path: str) -> Node:
    if TYPE_KEY not in raw:
        return DirNode(name, path, _parse_children(raw, path))

    declared = raw[TYPE_KEY]
    if declared == _TYPE_FILE:
        content = raw.get(CONTENT_KEY, "")
        if not isinstance(content, str):
            raise ScaffoldError(
                _join(path, CONTENT_KEY),
                f"content must be a string, found {_type_name(content)}",
            )
        return FileNode(name, path, content)

    if declared == _TYPE_DIR:
        children = raw.get(CHILDREN_KEY, {})
        if not isinstance(children, dict):
            raise ScaffoldError(
                _join(path, CHILDREN_KEY),
                f"children must be a mapping, found {_type_name(children)}",
            )
        child_map = cast("dict[str, Any]", children)
        return DirNode(name, path, _parse_children(child_map, _join(path, CHILDREN_KEY)))

    raise ScaffoldError(
        _join(path, TYPE_KEY),
        f"unknown type {declared!r} — expected {_TYPE_FILE!r} or {_TYPE_DIR!r}",
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_node(value: Any, name: str, path: str) -> Node:
    """Parse one config *value* into a node named *name*, reported against *path*."""
    if isinstance(value, str):
        return FileNode(name, path, value)
    if isinstance(value, dict):
        return _parse_mapping(cast("dict[str, Any]", value), name, path)
    if value is None:
        raise ScaffoldError(
            path,
            'node is null — use "" for an empty file or {} for an empty dir',
        )
    raise ScaffoldError(
        path,
        f"invalid node — expected a string or a mapping, found {_type_name(value)}",
    )


def resolve(config: dict[str, Any], dotted_path: str) -> Any:
    """Return the merged-config value at *dotted_path*.

    Raises :class:`ScaffoldError` naming the full path and the first segment
    that does not resolve.
    """
    try:
        return resolve_path(config, dotted_path)
    except PathError as exc:
        raise ScaffoldError(dotted_path, _resolve_message(exc)) from exc


def _resolve_message(exc: PathError) -> str:
    if not exc.dotted_path:
        return "empty config path"
    if exc.found_type is not None:
        return (
            f"no tree at {exc.dotted_path!r} — {exc.walked!r} is a {exc.found_type}, "
            f"not a mapping, so segment {exc.segment!r} cannot resolve"
        )
    return f"no tree at {exc.dotted_path!r} — segment {exc.segment!r} is missing"


def load(config: dict[str, Any], dotted_path: str) -> DirNode:
    """Resolve *dotted_path* in *config* and parse it into the root directory node."""
    value = resolve(config, dotted_path)
    if not isinstance(value, dict):
        found = "null" if value is None else _type_name(value)
        raise ScaffoldError(
            dotted_path,
            f"value at {dotted_path!r} is not a tree — expected a mapping, found {found}",
        )
    node = _parse_mapping(cast("dict[str, Any]", value), "", dotted_path)
    if not isinstance(node, DirNode):
        raise ScaffoldError(
            dotted_path,
            f"value at {dotted_path!r} is not a tree — the root node must be a directory",
        )
    return node
