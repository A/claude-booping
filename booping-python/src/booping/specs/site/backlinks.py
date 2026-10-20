from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from booping.specs.site.labels import Labels
from booping.specs.site.markdown import Heading, Rendered
from booping.specs.site.model import Site, SiteRecord, ref_keys


@dataclass(frozen=True)
class Backlink:
    record: SiteRecord
    via: list[str]


@dataclass(frozen=True)
class TypeGroup:
    type: str
    label: str
    items: list[Backlink]


@dataclass(frozen=True)
class SectionGroup:
    heading: Heading
    sources: list[SiteRecord]


@dataclass(frozen=True)
class Backlinks:
    by_type: list[TypeGroup]
    by_section: list[SectionGroup]


def _title(record: SiteRecord) -> str:
    title = record.frontmatter.get("title")
    return str(title) if title else record.stem


def _via(
    site: Site, source: SiteRecord, record: SiteRecord, rendered: Rendered, labels: Labels
) -> list[str]:
    """Relation labels in the source's frontmatter key order, then the `h2` text of each
    section holding a link here in body order; a link before any `h2` reads as the
    source's title. Each label once."""
    relations = site.relations(source)
    via = [
        labels.fact(key) for key in ref_keys(source.frontmatter) if record in relations.get(key, [])
    ]
    h2s = [h for h in rendered.headings if h.level == 2]
    for line, dest in rendered.links:
        if site.resolve_link(dest, source).record is not record:
            continue
        section = next((h.text for h in reversed(h2s) if h.line <= line), _title(source))
        via.append(section)
    return list(dict.fromkeys(via))


def backlink_groups(
    site: Site,
    record: SiteRecord,
    rendered: Mapping[int, Rendered],
    labels: Labels,
    types: Sequence[str],
) -> Backlinks:
    """Citing records grouped by type in `types` order, each in page order with the
    relations and sections it links here through; then this record's headings an
    incoming body link's `#anchor` names, in document order, with their citing records.
    `rendered` maps `id(record)` to every record's rendered body."""
    sources = site.backlinks(record)
    by_type = [
        TypeGroup(
            type_,
            labels.type_plural(type_),
            [
                Backlink(s, _via(site, s, record, rendered[id(s)], labels))
                for s in sources
                if s.type == type_
            ],
        )
        for type_ in types
        if any(s.type == type_ for s in sources)
    ]
    cited: dict[str, list[SiteRecord]] = {}
    for source in sources:
        for _, dest in rendered[id(source)].links:
            target = site.resolve_link(dest, source)
            if target.record is record and target.anchor is not None:
                named = cited.setdefault(target.anchor, [])
                if source not in named:
                    named.append(source)
    by_section = [
        SectionGroup(h, cited[h.id]) for h in rendered[id(record)].headings if h.id in cited
    ]
    return Backlinks(by_type, by_section)
