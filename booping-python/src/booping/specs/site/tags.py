"""A root's tag tree: its `tags.yaml` keys, the tags its records carry and their
ancestors, nested by `:` segment, each counting the records under it."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

from booping.specs import tags as tag_dictionary
from booping.specs.site.model import SiteRecord, SiteRoot, SiteWarning


@dataclass(frozen=True)
class TagNode:
    tag: str
    description: str
    count: int
    children: tuple[TagNode, ...]


def record_tags(record: SiteRecord) -> list[str]:
    """The record's `tags:`, or [] when it is not a list of strings — the checker's to report."""
    value: Any = record.frontmatter.get("tags")
    if not isinstance(value, list):
        return []
    items = cast("list[Any]", value)
    if not all(isinstance(t, str) for t in items):
        return []
    return [str(t) for t in items]


def _matches(carried: str, tag: str) -> bool:
    return carried == tag or carried.startswith(f"{tag}:")


def tagged(tag: str, records: list[SiteRecord]) -> list[SiteRecord]:
    """Records carrying `tag` or any of its descendants, in the given order."""
    return [r for r in records if any(_matches(t, tag) for t in record_tags(r))]


def tag_page_path(root: str, tag: str) -> str:
    return f"{root}/tags/{tag.replace(':', '.')}.html"


def _parent(tag: str) -> str:
    return tag.rsplit(":", 1)[0] if ":" in tag else ""


def tag_tree(root: SiteRoot, records: list[SiteRecord]) -> tuple[list[TagNode], list[SiteWarning]]:
    own = [r for r in records if r.root == root.name]
    warnings: list[SiteWarning] = []
    try:
        dictionary = tag_dictionary.load(root.path) or {}
    except tag_dictionary.MalformedDictionary as exc:
        dictionary = {}
        warnings.append(SiteWarning((root.path / tag_dictionary.DICTIONARY).resolve(), 1, str(exc)))
    used = {t for r in own for t in record_tags(r)}
    nodes: set[str] = set()
    for tag in {*dictionary, *used}:
        parts = tag.split(":")
        nodes.update(":".join(parts[:n]) for n in range(1, len(parts) + 1))

    def build(parent: str) -> tuple[TagNode, ...]:
        return tuple(
            TagNode(
                tag=tag,
                description=dictionary.get(tag, ""),
                count=len(tagged(tag, own)),
                children=build(tag),
            )
            for tag in sorted(n for n in nodes if _parent(n) == parent)
        )

    return list(build("")), warnings
