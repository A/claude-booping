from __future__ import annotations

from pathlib import Path

import pytest

from booping.specs.rules import load_targeted_rules
from booping.specs.targets import Target
from booping.specs.tiers import Tier, TierName

_ACCEPTED = "status: accepted\ntargets: [groom]\nbrief: Do the thing.\n"


def _tier(name: TierName, namespace: str | None, root: Path, anchor: Path) -> Tier:
    return Tier(name=name, namespace=namespace, root=root, anchor=anchor)


def _rule(root: Path, filename: str, frontmatter: str, title: str = "A rule") -> Path:
    path = root / "rule" / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\ntitle: {title}\n{frontmatter}---\n\nBody.\n")
    return path


def test_loads_accepted_targeted_rule(tmp_path: Path) -> None:
    root = tmp_path / "specs"
    path = _rule(
        root,
        "0003-x.md",
        "status: accepted\ntargets: [groom, develop/sprint, 'agent:dev', 'skill:playbook']\n"
        "brief: Keep it short.\n",
        title="Keep it short",
    )

    rules, skips = load_targeted_rules([_tier("project", None, root, tmp_path)])

    assert skips == []
    assert len(rules) == 1
    rule = rules[0]
    assert (rule.ref, rule.title, rule.brief, rule.tier, rule.path) == (
        "rule/0003",
        "Keep it short",
        "Keep it short.",
        "project",
        path,
    )
    assert rule.parsed_targets == [
        Target(kind="playbook", playbook="groom"),
        Target(kind="step", playbook="develop", step="sprint"),
        Target(kind="agent", agent="dev"),
        Target(kind="skill", skill="playbook"),
    ]


def test_ignores_retired_untargeted_and_non_rule_records(tmp_path: Path) -> None:
    root = tmp_path / "specs"
    _rule(root, "0001-retired.md", "status: retired\ntargets: [groom]\nbrief: Old.\n")
    _rule(root, "0002-docs-only.md", "status: accepted\n")
    _rule(root, "0003-proposed.md", "status: proposed\ntargets: [groom]\n")
    value = root / "value" / "0004-v.md"
    value.parent.mkdir(parents=True)
    value.write_text(f"---\ntitle: V\n{_ACCEPTED}---\n")
    (root / "0005-top.md").write_text(f"---\ntitle: T\n{_ACCEPTED}---\n")

    assert load_targeted_rules([_tier("project", None, root, tmp_path)]) == ([], [])


@pytest.mark.parametrize(
    ("filename", "content", "reason"),
    [
        (
            "0001-x.md",
            "---\ntitle: X\nstatus: accepted\ntargets: [groom]\nbrief: B.\n",
            "frontmatter block is not closed",
        ),
        (
            "0001-x.md",
            "---\ntitle: X\nstatus: accepted\ntargets: [groom]\n---\n",
            "targets and brief must come together",
        ),
        (
            "0001-x.md",
            "---\ntitle: X\nstatus: accepted\nbrief: Lonely.\n---\n",
            "targets and brief must come together",
        ),
        (
            "0001-x.md",
            "---\ntitle: X\nstatus: accepted\ntargets: [groom]\nbrief: '  '\n---\n",
            "targets and brief must come together",
        ),
        (
            "0001-x.md",
            "---\ntitle: X\nstatus: accepted\ntargets: [groom, 'bad target']\nbrief: B.\n---\n",
            "target 'bad target': not a target expression",
        ),
        (
            "x.md",
            "---\ntitle: X\nstatus: accepted\ntargets: [groom]\nbrief: B.\n---\n",
            "filename is not NNNN-slug.md",
        ),
    ],
    ids=[
        "frontmatter-error",
        "targets-without-brief",
        "brief-without-targets",
        "blank-brief",
        "unparseable-target",
        "numberless-filename",
    ],
)
def test_skips_rule_it_cannot_take(
    tmp_path: Path, filename: str, content: str, reason: str
) -> None:
    root = tmp_path / "specs"
    path = root / "rule" / filename
    path.parent.mkdir(parents=True)
    path.write_text(content)

    rules, skips = load_targeted_rules([_tier("project", None, root, tmp_path)])

    assert rules == []
    assert [(skip.path, skip.reason) for skip in skips] == [(path, reason)]


def test_ref_and_link_per_tier(tmp_path: Path) -> None:
    plugin, home, repo = tmp_path / "plugin", tmp_path / "home", tmp_path / "repo"
    _rule(plugin / "vault" / "specs", "0004-x.md", _ACCEPTED)
    _rule(home / "_specs", "0005-y.md", _ACCEPTED)
    _rule(repo / "specs", "0006-z.md", _ACCEPTED)
    tiers = [
        _tier("core", "booping", plugin / "vault" / "specs", plugin),
        _tier("global", "alice", home / "_specs", home),
        _tier("project", None, repo / "specs", repo),
    ]

    rules, _ = load_targeted_rules(tiers)

    assert [(rule.ref, rule.link, rule.tier) for rule in rules] == [
        ("booping:rule/0004", "${CLAUDE_PLUGIN_ROOT}/vault/specs/rule/0004-x.md", "core"),
        ("alice:rule/0005", f"{home.as_posix()}/_specs/rule/0005-y.md", "global"),
        ("rule/0006", "specs/rule/0006-z.md", "project"),
    ]


@pytest.mark.parametrize(("name", "namespace"), [("core", "booping"), ("project", None)])
def test_record_outside_anchor_links_absolute(
    tmp_path: Path, name: TierName, namespace: str | None
) -> None:
    root = tmp_path / "elsewhere" / "specs"
    _rule(root, "0004-x.md", _ACCEPTED)

    rules, _ = load_targeted_rules([_tier(name, namespace, root, tmp_path / "plugin")])

    assert [rule.link for rule in rules] == [
        f"{tmp_path.as_posix()}/elsewhere/specs/rule/0004-x.md"
    ]


def test_shared_directory_yields_each_rule_once_with_first_tier(tmp_path: Path) -> None:
    root = tmp_path / "vault"
    _rule(root, "0001-a.md", _ACCEPTED)
    _rule(root, "0002-b.md", "status: accepted\ntargets: [groom]\n")
    tiers = [
        _tier("core", "booping", root, tmp_path),
        _tier("project", None, root, tmp_path),
    ]

    rules, skips = load_targeted_rules(tiers)

    assert [(rule.ref, rule.tier) for rule in rules] == [("booping:rule/0001", "core")]
    assert [skip.path.name for skip in skips] == ["0002-b.md"]


def test_orders_by_tier_then_number(tmp_path: Path) -> None:
    core, home = tmp_path / "core", tmp_path / "home"
    for number in ("0010", "0002"):
        _rule(core, f"{number}-c.md", _ACCEPTED)
    for number in ("0003", "0001"):
        _rule(home, f"{number}-g.md", _ACCEPTED)
    tiers = [
        _tier("core", "booping", core, tmp_path),
        _tier("global", "me", home, home),
    ]

    rules, _ = load_targeted_rules(tiers)

    assert [rule.ref for rule in rules] == [
        "booping:rule/0002",
        "booping:rule/0010",
        "me:rule/0001",
        "me:rule/0003",
    ]


def test_collapses_multiline_brief(tmp_path: Path) -> None:
    root = tmp_path / "specs"
    _rule(
        root,
        "0001-x.md",
        "status: accepted\ntargets: [groom]\nbrief: |\n  First line,\n    then   the second.\n",
    )

    rules, _ = load_targeted_rules([_tier("project", None, root, tmp_path)])

    assert [rule.brief for rule in rules] == ["First line, then the second."]


def test_missing_tier_root_contributes_nothing(tmp_path: Path) -> None:
    root = tmp_path / "project"
    _rule(root, "0001-x.md", _ACCEPTED)
    tiers = [
        _tier("core", "booping", tmp_path / "absent", tmp_path),
        _tier("project", None, root, tmp_path),
    ]

    rules, skips = load_targeted_rules(tiers)

    assert ([rule.ref for rule in rules], skips) == (["rule/0001"], [])
