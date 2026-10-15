from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any, Literal, NamedTuple
from urllib.parse import unquote

from booping.specs.links import relative_links
from booping.specs.records import load_record, parse_filename, parse_ref
from booping.specs.tiers import own_types

_URI_SCHEME = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*:")


class SiteWarning(NamedTuple):
    path: Path
    line: int
    message: str


@dataclass(frozen=True)
class SiteRoot:
    name: str
    path: Path


@dataclass(frozen=True, eq=False)
class SiteRecord:
    root: str
    type: str
    number: int
    slug: str
    path: Path
    frontmatter: dict[str, Any]
    body: str
    body_first_line: int

    @property
    def stem(self) -> str:
        return f"{self.number:04d}-{self.slug}"

    @property
    def ref(self) -> str:
        return f"{self.type}/{self.number:04d}"

    @property
    def page(self) -> str:
        return f"{self.root}/{self.type}/{self.stem}.html"


@dataclass(frozen=True)
class RefMiss:
    # True when the target root is rendered but holds no such record; false when the
    # namespace names no rendered root — a reference outside the site is not an error.
    warn: bool


LinkKind = Literal["external", "anchor", "record", "offsite", "unresolved"]


@dataclass(frozen=True)
class LinkTarget:
    kind: LinkKind
    record: SiteRecord | None = None
    anchor: str | None = None


@dataclass
class Site:
    roots: list[SiteRoot]
    records: list[SiteRecord] = field(default_factory=lambda: [])

    @cached_property
    def statuses(self) -> set[str]:
        return {
            str(r.frontmatter["status"])
            for r in self.records
            if r.frontmatter.get("status") is not None
        }

    @cached_property
    def _by_ref(self) -> dict[tuple[str, str, int], SiteRecord]:
        return {(r.root, r.type, r.number): r for r in self.records}

    @cached_property
    def _by_path(self) -> dict[Path, SiteRecord]:
        by_path: dict[Path, SiteRecord] = {}
        for record in self.records:
            by_path.setdefault(record.path, record)
        return by_path

    @cached_property
    def _root_names(self) -> set[str]:
        return {root.name for root in self.roots}

    def resolve_ref(self, text: str, from_root: str) -> SiteRecord | RefMiss | None:
        ref = parse_ref(text)
        if ref is None:
            return None
        root = ref.namespace or from_root
        if root not in self._root_names:
            return RefMiss(warn=False)
        record = self._by_ref.get((root, ref.type, ref.number))
        return record if record is not None else RefMiss(warn=True)

    def resolve_link(self, dest: str, from_record: SiteRecord) -> LinkTarget:
        if _URI_SCHEME.match(dest) or dest.startswith("/"):
            return LinkTarget(kind="external")
        if dest.startswith("#"):
            return LinkTarget(kind="anchor")
        local, _, anchor = dest.partition("#")
        try:
            target = (from_record.path.parent / unquote(local)).resolve()
            exists = target.exists()
        except (OSError, RuntimeError):
            return LinkTarget(kind="unresolved")
        record = self._by_path.get(target)
        if record is not None:
            return LinkTarget(kind="record", record=record, anchor=anchor or None)
        return LinkTarget(kind="offsite" if exists else "unresolved")

    @cached_property
    def _backlinks(self) -> dict[int, list[SiteRecord]]:
        index: dict[int, list[SiteRecord]] = {}
        for source in self.records:
            targets: list[SiteRecord] = []
            for text in _strings(source.frontmatter):
                resolved = self.resolve_ref(text, source.root)
                if isinstance(resolved, SiteRecord):
                    targets.append(resolved)
            for link in relative_links(source.body, source.body_first_line):
                resolved = self.resolve_link(link.dest, source)
                if resolved.record is not None:
                    targets.append(resolved.record)
            seen: set[int] = set()
            for target in targets:
                if target is source or id(target) in seen:
                    continue
                seen.add(id(target))
                index.setdefault(id(target), []).append(source)
        return index

    def backlinks(self, record: SiteRecord) -> list[SiteRecord]:
        return list(self._backlinks.get(id(record), []))

    @cached_property
    def _relations(self) -> dict[int, dict[str, list[SiteRecord]]]:
        index: dict[int, dict[str, list[SiteRecord]]] = {}
        for source in self.records:
            relations: dict[str, list[SiteRecord]] = {}
            for key in sorted(ref_keys(source.frontmatter)):
                targets: list[SiteRecord] = []
                for text in ref_values(source.frontmatter[key]):
                    resolved = self.resolve_ref(text, source.root)
                    if isinstance(resolved, SiteRecord) and resolved not in targets:
                        targets.append(resolved)
                if targets:
                    relations[key] = targets
            index[id(source)] = relations
        return index

    def relations(self, record: SiteRecord) -> dict[str, list[SiteRecord]]:
        """Frontmatter ref keys, sorted, each with the records its refs resolve to in
        frontmatter order, once each; a key resolving to nothing is absent."""
        return {key: list(targets) for key, targets in self._relations[id(record)].items()}

    @cached_property
    def _superseded_by(self) -> dict[int, list[SiteRecord]]:
        index: dict[int, list[SiteRecord]] = {}
        for source in self.records:
            for target in self._relations[id(source)].get("supersedes", []):
                index.setdefault(id(target), []).append(source)
        return index

    def superseded_by(self, record: SiteRecord) -> list[SiteRecord]:
        return list(self._superseded_by.get(id(record), []))


def ref_values(value: Any) -> list[str]:
    """The ref strings of a frontmatter value that is a ref or a list of refs, else []."""
    items: list[Any] = value if isinstance(value, list) else [value]  # pyright: ignore[reportUnknownVariableType]
    if not items or not all(isinstance(i, str) and parse_ref(i) is not None for i in items):
        return []
    return [str(i) for i in items]


def ref_keys(frontmatter: dict[str, Any]) -> list[str]:
    """Frontmatter keys whose value is a ref or a list of refs, in frontmatter order."""
    return [key for key, value in frontmatter.items() if ref_values(value)]


def _strings(value: Any) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():  # pyright: ignore[reportUnknownVariableType]
            yield from _strings(item)
    elif isinstance(value, list):
        for item in value:  # pyright: ignore[reportUnknownVariableType]
            yield from _strings(item)


def load_site(roots: list[SiteRoot], known_types: list[str]) -> Site:
    """Roots as given, types in `known_types` order then the types a root's own
    `_schemas/` adds, records by number. Each root reads its own type set; unknown type
    directories and unparseable filenames are skipped — reporting them is `specs check`'s job."""
    records: list[SiteRecord] = []
    for root in roots:
        added = [t for t in own_types(root.path) if t not in known_types]
        for type_ in [*known_types, *added]:
            type_dir = root.path / type_
            if not type_dir.is_dir():
                continue
            files: list[tuple[int, str, Path]] = []
            for path in type_dir.iterdir():
                parsed = parse_filename(path.name)
                if parsed is not None and path.is_file():
                    files.append((parsed[0], parsed[1], path))
            for number, slug, path in sorted(files):
                text = path.read_text()
                record = load_record(path, type_)
                records.append(
                    SiteRecord(
                        root=root.name,
                        type=type_,
                        number=number,
                        slug=slug,
                        path=path.resolve(),
                        frontmatter=record.frontmatter,
                        body=record.body,
                        body_first_line=text[: len(text) - len(record.body)].count("\n") + 1,
                    )
                )
    return Site(roots=list(roots), records=records)
