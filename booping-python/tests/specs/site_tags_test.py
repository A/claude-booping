from __future__ import annotations

from pathlib import Path

from booping.specs.site.model import SiteRoot, SiteWarning, load_site
from booping.specs.site.tags import TagNode, tag_page_path, tag_tree, tagged

TYPES = ["value", "adr"]


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def _tier(tmp_path: Path, dictionary: str | None) -> SiteRoot:
    root = tmp_path / "s"
    if dictionary is not None:
        _write(root / "tags.yaml", dictionary)
    _write(root / "adr" / "0001-one.md", "---\ntitle: One\ntags: [a:b]\n---\nx\n")
    _write(root / "adr" / "0002-two.md", "---\ntitle: Two\ntags: [a:b:c]\n---\nx\n")
    _write(root / "value" / "0001-three.md", "---\ntitle: Three\ntags: [x]\n---\nx\n")
    _write(root / "value" / "0002-odd.md", "---\ntitle: Odd\ntags: q\n---\nx\n")
    return SiteRoot("s", root)


def _leaf(tag: str, description: str, count: int) -> TagNode:
    return TagNode(tag=tag, description=description, count=count, children=())


def test_tree_merges_dictionary_and_used_tags_with_inclusive_counts(tmp_path: Path) -> None:
    root = _tier(tmp_path, "a: A\na:b: AB\n")
    site = load_site([root], TYPES)

    assert tag_tree(root, site.records) == (
        [
            TagNode(
                tag="a",
                description="A",
                count=2,
                children=(
                    TagNode(
                        tag="a:b",
                        description="AB",
                        count=2,
                        children=(_leaf("a:b:c", "", 1),),
                    ),
                ),
            ),
            _leaf("x", "", 1),
        ],
        [],
    )


def test_tagged_includes_descendants_in_page_order(tmp_path: Path) -> None:
    root = _tier(tmp_path, None)
    site = load_site([root], TYPES)

    assert [r.ref for r in tagged("a", site.records)] == ["adr/0001", "adr/0002"]
    assert [r.ref for r in tagged("a:b:c", site.records)] == ["adr/0002"]


def test_no_dictionary_builds_the_tree_from_used_tags(tmp_path: Path) -> None:
    root = _tier(tmp_path, None)
    site = load_site([root], TYPES)

    nodes, warnings = tag_tree(root, site.records)

    assert [(n.tag, n.description, n.count) for n in nodes] == [("a", "", 2), ("x", "", 1)]
    assert warnings == []


def test_malformed_dictionary_is_one_warning_and_the_used_tag_tree(tmp_path: Path) -> None:
    root = _tier(tmp_path, "- a\n- b\n")
    site = load_site([root], TYPES)

    nodes, warnings = tag_tree(root, site.records)

    assert [(n.tag, n.count) for n in nodes] == [("a", 2), ("x", 1)]
    assert len(warnings) == 1
    assert isinstance(warnings[0], SiteWarning)
    assert warnings[0].path == (root.path / "tags.yaml").resolve()


def test_tag_page_path_replaces_colons() -> None:
    assert tag_page_path("s", "a:b:c") == "s/tags/a.b.c.html"
