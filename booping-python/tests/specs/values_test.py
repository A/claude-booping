from __future__ import annotations

from pathlib import Path

from booping.specs.tiers import Tier, TierName
from booping.specs.values import SpecValue, has_specs, load_values


def _tier(name: TierName, namespace: str | None, root: Path) -> Tier:
    return Tier(
        name=name,
        namespace=namespace,
        root=root,
        anchor=root.parent,
        schemas={"rule": Path("rule.yaml"), "value": Path("value.yaml")},
    )


def _value(root: Path, filename: str, frontmatter: str) -> None:
    path = root / "value" / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{frontmatter}---\n\nBody.\n")


def test_values_come_global_first_by_number_with_namespace(tmp_path: Path) -> None:
    glob, project, core = tmp_path / "g", tmp_path / "p", tmp_path / "c"
    _value(glob, "0001-calm.md", "title: Calm\nsummary: Nothing\n  shouts.\nkind: value\n")
    _value(project, "0010-polish.md", "title: Polish\nsummary: Not this.\nkind: non-value\n")
    _value(project, "0002-speed.md", "title: Speed\nsummary: Ship fast.\nkind: value\n")
    _value(core, "0001-core.md", "title: Core\nsummary: Never listed.\n")

    tiers = [
        _tier("core", "booping", core),
        _tier("global", "anton", glob),
        _tier("project", None, project),
    ]
    values = load_values(tiers)

    assert values == [
        SpecValue(ref="anton:value/0001", title="Calm", summary="Nothing shouts."),
        SpecValue(ref="value/0002", title="Speed", summary="Ship fast."),
        SpecValue(ref="value/0010", title="Polish", summary="Not this.", non_value=True),
    ]


def test_broken_records_are_left_to_check(tmp_path: Path) -> None:
    root = tmp_path / "p"
    _value(root, "0001-ok.md", "title: Ok\nsummary: Fine.\n")
    _value(root, "0002-bad.md", "title: [unclosed\n")
    _value(root, "no-number.md", "title: Loose\nsummary: Loose.\n")

    values = load_values([_tier("project", None, root)])

    assert [v.ref for v in values] == ["value/0001"]


def test_has_specs_needs_a_type_directory(tmp_path: Path) -> None:
    tier = _tier("project", None, tmp_path)
    (tmp_path / "plans").mkdir()
    assert not has_specs(tier)
    (tmp_path / "rule").mkdir()
    assert has_specs(tier)
