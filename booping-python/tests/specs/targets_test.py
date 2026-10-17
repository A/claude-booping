from __future__ import annotations

import pytest

from booping.specs.targets import Target, TargetRejection, parse_target


@pytest.mark.parametrize(
    ("entry", "expected"),
    [
        ("groom", Target(kind="playbook", playbook="groom")),
        ("groom/draft-plan", Target(kind="step", playbook="groom", step="draft-plan")),
        ("agent:booping-developer", Target(kind="agent", agent="booping-developer")),
        (
            "agent:booping:booping-researcher",
            Target(kind="agent", agent="booping:booping-researcher"),
        ),
        ("skill:playbook", Target(kind="skill", skill="playbook")),
        ("skill:code-review", Target(kind="skill", skill="code-review")),
    ],
)
def test_accepted_forms_classify_by_kind(entry: str, expected: Target) -> None:
    assert parse_target(entry) == expected


@pytest.mark.parametrize(
    ("entry", "expected"),
    [
        ("", TargetRejection(entry="", reason="not a target expression")),
        ("  ", TargetRejection(entry="  ", reason="not a target expression")),
        (" groom", TargetRejection(entry=" groom", reason="not a target expression")),
        ("groom*", TargetRejection(entry="groom*", reason="not a target expression")),
        ("!groom", TargetRejection(entry="!groom", reason="not a target expression")),
        ("groom/*", TargetRejection(entry="groom/*", reason="not a target expression")),
        (
            "groom/draft-plan/extra",
            TargetRejection(entry="groom/draft-plan/extra", reason="not a target expression"),
        ),
        ("/groom", TargetRejection(entry="/groom", reason="not a target expression")),
        ("groom/", TargetRejection(entry="groom/", reason="not a target expression")),
        ("agent:", TargetRejection(entry="agent:", reason="not a target expression")),
        ("agent:*", TargetRejection(entry="agent:*", reason="not a target expression")),
        ("skill:", TargetRejection(entry="skill:", reason="not a target expression")),
        ("skill:*", TargetRejection(entry="skill:*", reason="not a target expression")),
        (
            "some playbook",
            TargetRejection(entry="some playbook", reason="not a target expression"),
        ),
        (42, TargetRejection(entry="42", reason="not a string")),
        (
            {"playbook": "groom"},
            TargetRejection(entry="{'playbook': 'groom'}", reason="not a string"),
        ),
        (None, TargetRejection(entry="None", reason="not a string")),
    ],
)
def test_malformed_entries_are_rejected_with_a_reason(
    entry: object, expected: TargetRejection
) -> None:
    assert parse_target(entry) == expected
