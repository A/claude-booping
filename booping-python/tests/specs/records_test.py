from __future__ import annotations

from pathlib import Path

import pytest

from booping.specs.records import Ref, load_tier, parse_filename, parse_ref
from booping.specs.tiers import Tier


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("0003-compact-artefact-first.md", (3, "compact-artefact-first")),
        ("0010-x.md", (10, "x")),
        ("0001-rule2-v3.md", (1, "rule2-v3")),
        ("003-short.md", None),
        ("00003-long.md", None),
        ("0003-Upper.md", None),
        ("0003-trailing-.md", None),
        ("0003--double.md", None),
        ("0003_underscore.md", None),
        ("0003-slug.txt", None),
        ("README.md", None),
    ],
)
def test_parse_filename(name: str, expected: tuple[int, str] | None) -> None:
    assert parse_filename(name) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("rule/0003", Ref(namespace=None, type="rule", number=3)),
        ("booping:rule/0003", Ref(namespace="booping", type="rule", number=3)),
        ("anton:value/0120", Ref(namespace="anton", type="value", number=120)),
        ("rule/3", None),
        ("rule/00003", None),
        ("rule", None),
        (":rule/0003", None),
        ("booping:rule", None),
        ("rule/0003/extra", None),
        ("a:b:rule/0003", None),
    ],
)
def test_parse_ref(text: str, expected: Ref | None) -> None:
    assert parse_ref(text) == expected


def _tier(root: Path) -> Tier:
    return Tier(name="project", namespace=None, root=root, anchor=root.parent)


def test_load_tier_reads_every_type_directory(tmp_path: Path) -> None:
    root = tmp_path / "specs"
    (root / "rule").mkdir(parents=True)
    (root / "value").mkdir()
    (root / "stray").mkdir()
    (root / "README.md").write_text("# format\n")
    (root / "rule" / "0002-b.md").write_text("---\ntype: rule\n---\nsecond\n")
    (root / "rule" / "0001-a.md").write_text("---\ntype: rule\n---\nfirst\n")
    (root / "value" / "0001-v.md").write_text("---\ntype: value\n---\nvalue\n")
    (root / "stray" / "notes.md").write_text("no frontmatter\n")

    records = load_tier(_tier(root), ["rule", "value"])

    assert [(r.type, r.path.name) for r in records] == [
        ("rule", "0001-a.md"),
        ("rule", "0002-b.md"),
        ("value", "0001-v.md"),
        ("stray", "notes.md"),
    ]
    first = records[0]
    assert (first.number, first.slug) == (1, "a")
    assert first.frontmatter == {"type": "rule"}
    assert first.body == "first\n"
    assert first.frontmatter_error is None
    stray = records[-1]
    assert (stray.number, stray.slug) == (None, None)
    assert stray.body == "no frontmatter\n"


def test_load_tier_captures_broken_yaml(tmp_path: Path) -> None:
    root = tmp_path / "specs"
    (root / "rule").mkdir(parents=True)
    (root / "rule" / "0001-broken.md").write_text("---\ntitle: [unclosed\n---\nbody\n")

    [record] = load_tier(_tier(root), ["rule"])

    assert record.frontmatter == {}
    assert record.frontmatter_error
    assert record.body == "body\n"


def test_load_tier_missing_root(tmp_path: Path) -> None:
    assert load_tier(_tier(tmp_path / "nope"), ["rule"]) == []
