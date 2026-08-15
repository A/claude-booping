from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

from booping_tracker import cli
from booping_tracker.config import load as load_config
from booping_tracker.errors import ProviderError, UserError
from booping_tracker.providers import linear as linear_mod
from booping_tracker.providers.linear import LinearProvider
from tests.fake_transport import FakeTransport

FIXTURE_CONFIG = Path(__file__).parent / "fixtures" / "tracker.yaml"

TEAMS = {"teams": {"nodes": [{"id": "team-uuid", "key": "ENG"}]}}
STATES = {
    "workflowStates": {
        "nodes": [
            {"id": "s-done", "name": "Done", "type": "completed", "position": 3},
            {"id": "s-todo", "name": "Todo", "type": "unstarted", "position": 1},
            {"id": "s-progress", "name": "In Progress", "type": "started", "position": 2},
        ]
    }
}
LABELS = {"issueLabels": {"nodes": [{"id": "l-plan", "name": "plan"},
                                    {"id": "l-request", "name": "request"}]}}
ISSUE_TEAM = {
    "issue": {
        "identifier": "LIN-5",
        "url": "https://linear.app/acme/issue/LIN-5",
        "state": {"name": "Todo"},
        "team": {"key": "ENG"},
    }
}
ISSUE_IN_PROGRESS = {
    "issue": {
        "identifier": "LIN-5",
        "url": "https://linear.app/acme/issue/LIN-5",
        "state": {"name": "In Progress"},
        "team": {"key": "ENG"},
    }
}
CREATED = {"issueCreate": {"success": True,
                           "issue": {"id": "i-9", "identifier": "LIN-9",
                                     "url": "https://linear.app/acme/issue/LIN-9"}}}
UPDATED = {"issueUpdate": {"success": True,
                           "issue": {"id": "i-5", "identifier": "LIN-5",
                                     "url": "https://linear.app/acme/issue/LIN-5"}}}
PLAYBOOKS = {"groom": {"statuses": {"framing": "In Progress", "ready-for-dev": "Done"}}}


def canned(*payloads: dict[str, Any]) -> dict[str, Any]:
    """Response map keyed by operation — each GraphQL payload is named after its own root."""
    return {operation: payload for payload in payloads for operation in payload}


def provider(responses: dict[str, Any]) -> tuple[LinearProvider, FakeTransport]:
    transport = FakeTransport(responses)
    return LinearProvider(transport=transport, playbooks=PLAYBOOKS), transport


def artifact(tmp_path: Path, frontmatter: str) -> Path:
    path = tmp_path / "index.md"
    path.write_text(f"---\n{frontmatter}---\n\n# Plan\n", encoding="utf-8")
    return path


# --- reads ---------------------------------------------------------------------------


def test_states_queries_the_team_by_key_and_orders_by_position() -> None:
    linear, transport = provider(canned(STATES))

    result = linear.states(team="ENG")

    assert transport.last("workflowStates").variables == {"team": "ENG"}
    assert [state.name for state in result.states] == ["Todo", "In Progress", "Done"]


def test_the_states_receipt_carries_each_position_and_type() -> None:
    linear, _ = provider(canned(STATES))

    receipt = linear.states(team="ENG").receipt

    assert receipt.splitlines() == [
        "states ENG: 3 states",
        "  1 Todo (unstarted) s-todo",
        "  2 In Progress (started) s-progress",
        "  3 Done (completed) s-done",
    ]


@pytest.mark.parametrize("ref", ["LIN-1", "0f9a1e2c-1111-2222-3333-444455556666"])
def test_show_passes_a_human_identifier_or_a_uuid_straight_through(ref: str) -> None:
    linear, transport = provider(
        {
            "issue": {
                "issue": {
                    "identifier": "LIN-1",
                    "url": "https://linear.app/acme/issue/LIN-1",
                    "title": "Ship it",
                    "description": "the request body",
                    "state": {"name": "In Progress"},
                    "labels": {"nodes": [{"name": "request"}]},
                    "assignee": {"name": "Ada"},
                }
            }
        }
    )

    result = linear.show(issue=ref, with_comments=False)

    assert transport.operations == ["issue"]
    assert transport.last("issue").variables == {"id": ref}
    assert (result.title, result.state, result.labels, result.assignee) == (
        "Ship it",
        "In Progress",
        ["request"],
        "Ada",
    )


def test_with_comments_adds_the_comment_connection_and_reads_it_back() -> None:
    linear, transport = provider(
        {
            "issue": {
                "issue": {
                    "identifier": "LIN-1",
                    "title": "Ship it",
                    "state": {"name": "Todo"},
                    "comments": {"nodes": [{"user": {"name": "Ada"}, "body": "which team?"}]},
                }
            }
        }
    )

    result = linear.show(issue="LIN-1", with_comments=True)

    assert "comments" in transport.last("issue").query
    assert [(c.author, c.body) for c in result.comments] == [("Ada", "which team?")]


def test_show_without_comments_does_not_ask_for_them() -> None:
    linear, transport = provider({"issue": {"issue": {"identifier": "LIN-1", "title": "Ship it"}}})

    linear.show(issue="LIN-1", with_comments=False)

    assert "comments" not in transport.last("issue").query


# --- writes --------------------------------------------------------------------------


def test_comment_posts_the_body_against_the_issue() -> None:
    linear, transport = provider(
        {"commentCreate": {"commentCreate": {"success": True,
                                             "comment": {"id": "c-1", "url": "https://c/1"}}}}
    )

    result = linear.comment(issue="LIN-1", body="## Q1\nwhich team?")

    assert transport.last("commentCreate").variables == {
        "input": {"issueId": "LIN-1", "body": "## Q1\nwhich team?"}
    }
    assert result.url == "https://c/1"


def test_issue_create_with_a_parent_sends_a_resolved_sub_issue_input() -> None:
    linear, transport = provider(canned(TEAMS, STATES, LABELS, CREATED))

    result = linear.issue_create(
        team="ENG", title="T", body="B", parent="LIN-1", labels=["plan"], state="Todo"
    )

    assert transport.last("issueCreate").variables == {
        "input": {
            "teamId": "team-uuid",
            "title": "T",
            "description": "B",
            "parentId": "LIN-1",
            "labelIds": ["l-plan"],
            "stateId": "s-todo",
        }
    }
    assert result.identifier == "LIN-9"


def test_issue_create_without_a_parent_sends_no_parent_id() -> None:
    linear, transport = provider(canned(TEAMS, CREATED))

    linear.issue_create(team="ENG", title="T", body="B", parent=None, labels=[], state=None)

    assert transport.last("issueCreate").variables["input"] == {
        "teamId": "team-uuid",
        "title": "T",
        "description": "B",
    }


def test_labels_are_added_and_removed_discretely_never_replaced() -> None:
    linear, transport = provider(canned(ISSUE_TEAM, LABELS, UPDATED))

    linear.issue_update(
        issue="LIN-5",
        state=None,
        title=None,
        body=None,
        add_labels=["plan"],
        remove_labels=["request"],
        assignee=None,
    )

    sent: dict[str, Any] = transport.last("issueUpdate").variables["input"]
    assert sent == {"addedLabelIds": ["l-plan"], "removedLabelIds": ["l-request"]}
    assert "labelIds" not in sent


def test_issue_update_resolves_a_state_name_against_the_issues_own_team() -> None:
    linear, transport = provider(canned(ISSUE_TEAM, STATES, UPDATED))

    linear.issue_update(
        issue="LIN-5",
        state="Done",
        title="Renamed",
        body="new body",
        add_labels=[],
        remove_labels=[],
        assignee="user-uuid",
    )

    assert transport.last("workflowStates").variables == {"team": "ENG"}
    assert transport.last("issueUpdate").variables == {
        "id": "LIN-5",
        "input": {
            "stateId": "s-done",
            "title": "Renamed",
            "description": "new body",
            "assigneeId": "user-uuid",
        },
    }


@pytest.mark.parametrize("relation", ["blocks", "duplicate", "related", "similar"])
def test_relate_sends_each_accepted_enum_member(relation: str) -> None:
    linear, transport = provider(
        {"issueRelationCreate": {"issueRelationCreate": {"success": True,
                                                         "issueRelation": {"id": "rel-1"}}}}
    )

    result = linear.relate(issue="LIN-1", to="LIN-2", relation=relation)

    assert transport.last("issueRelationCreate").variables == {
        "input": {"issueId": "LIN-1", "relatedIssueId": "LIN-2", "type": relation}
    }
    assert result.relation_id == "rel-1"


@pytest.mark.parametrize("relation", ["blocked_by", "Blocks", "parent"])
def test_a_relation_outside_the_enum_is_a_user_error_listing_the_set(relation: str) -> None:
    linear, transport = provider({})

    with pytest.raises(UserError, match="accepted: blocks, duplicate, related, similar"):
        linear.relate(issue="LIN-1", to="LIN-2", relation=relation)
    assert transport.calls == []


def test_an_unknown_label_names_it_and_lists_the_teams_labels() -> None:
    linear, _ = provider(canned(TEAMS, LABELS))

    with pytest.raises(UserError, match="unknown label: epic \\(team ENG has: plan, request\\)"):
        linear.issue_create(
            team="ENG", title="T", body="B", parent=None, labels=["epic"], state=None
        )


def test_an_unknown_state_names_it_and_lists_the_teams_states() -> None:
    linear, _ = provider(canned(TEAMS, STATES))

    with pytest.raises(UserError, match="unknown state: Shipped \\(team ENG has: Todo, "):
        linear.issue_create(
            team="ENG", title="T", body="B", parent=None, labels=[], state="Shipped"
        )


def test_an_unknown_team_names_it_and_lists_the_available_keys() -> None:
    linear, _ = provider({"teams": {"teams": {"nodes": [{"id": "t-1", "key": "OPS"}]}}})

    with pytest.raises(UserError, match="unknown team: ENG \\(available: OPS\\)"):
        linear.issue_create(team="ENG", title="T", body="B", parent=None, labels=[], state=None)


# --- sync ----------------------------------------------------------------------------


def test_sync_moves_the_issue_to_the_state_its_status_maps_to(tmp_path: Path) -> None:
    linear, transport = provider(canned(ISSUE_TEAM, STATES, UPDATED))
    path = artifact(tmp_path, "status: ready-for-dev\ntracker_issue: LIN-5\n")

    result = linear.sync(artifact=path, playbook="groom")

    assert transport.last("issueUpdate").variables == {
        "id": "LIN-5",
        "input": {"stateId": "s-done"},
    }
    assert result.changed is True
    assert result.receipt == 'sync LIN-5: state "Done" (was "Todo")'


def test_a_second_sync_of_an_unchanged_artifact_sends_no_mutation(tmp_path: Path) -> None:
    linear, transport = provider(canned(ISSUE_IN_PROGRESS, STATES, UPDATED))
    path = artifact(tmp_path, "status: framing\ntracker_issue: LIN-5\n")

    result = linear.sync(artifact=path, playbook="groom")

    assert transport.operations == ["issue"]
    assert result.changed is False
    assert result.receipt == 'sync LIN-5: state "In Progress" (unchanged)'


def test_an_artifact_without_a_tracker_issue_touches_nothing(tmp_path: Path) -> None:
    linear, transport = provider({})
    path = artifact(tmp_path, "status: framing\ntracker_issue: null\n")

    result = linear.sync(artifact=path, playbook="groom")

    assert transport.calls == []
    assert result.changed is False
    assert "no tracker_issue" in result.receipt


def test_a_status_with_no_mapping_names_the_status(tmp_path: Path) -> None:
    linear, _ = provider({})
    path = artifact(tmp_path, "status: presenting\ntracker_issue: LIN-5\n")

    with pytest.raises(UserError, match="no Linear state mapped for status 'presenting'"):
        linear.sync(artifact=path, playbook="groom")


def test_the_playbook_is_inferred_when_exactly_one_is_configured(tmp_path: Path) -> None:
    linear, transport = provider(canned(ISSUE_IN_PROGRESS, STATES, UPDATED))
    path = artifact(tmp_path, "status: framing\ntracker_issue: LIN-5\n")

    assert linear.sync(artifact=path, playbook=None).receipt.endswith("(unchanged)")
    assert transport.operations == ["issue"]


def test_a_playbook_with_no_tracker_mapping_is_a_user_error(tmp_path: Path) -> None:
    linear, _ = provider({})
    path = artifact(tmp_path, "status: framing\ntracker_issue: LIN-5\n")

    with pytest.raises(UserError, match="no tracker mapping for playbook develop"):
        linear.sync(artifact=path, playbook="develop")


# --- wiring --------------------------------------------------------------------------


@pytest.fixture
def stub_http(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """Swap the network transport for a fake, recording how it was constructed."""
    built: dict[str, Any] = {"responses": {}}

    def build(*, api_url: str, api_key: str) -> FakeTransport:
        built["api_url"] = api_url
        built["api_key"] = api_key
        return FakeTransport(built["responses"])

    monkeypatch.setattr(linear_mod, "HttpTransport", build)
    monkeypatch.setenv("LINEAR_API_KEY", "lin_api_from_env")
    return built


def test_the_api_key_comes_from_the_variable_named_in_config(stub_http: dict[str, Any]) -> None:
    LinearProvider.from_config(load_config(config_file=FIXTURE_CONFIG))

    assert stub_http["api_key"] == "lin_api_from_env"
    assert stub_http["api_url"] == "https://api.linear.app/graphql"


def test_an_unset_key_variable_is_a_user_error(monkeypatch: pytest.MonkeyPatch) -> None:
    config = load_config(config_file=FIXTURE_CONFIG, require_api_key=False)
    monkeypatch.delenv("LINEAR_API_KEY", raising=False)

    with pytest.raises(UserError, match="LINEAR_API_KEY is unset"):
        LinearProvider.from_config(config)


@pytest.mark.parametrize(
    ("responses", "expected_exit"),
    [
        ({"issueRelationCreate": ProviderError("issueRelationCreate: rate limited")}, 2),
        ({"issueRelationCreate": UserError("nope")}, 1),
    ],
)
def test_provider_failures_reach_the_cli_as_their_exit_codes(
    monkeypatch: pytest.MonkeyPatch,
    stub_http: dict[str, Any],
    responses: dict[str, Any],
    expected_exit: int,
) -> None:
    stub_http["responses"] = responses
    monkeypatch.setattr(
        sys,
        "argv",
        ["booping-tracker", "--config-file", str(FIXTURE_CONFIG),
         "relate", "--issue", "LIN-1", "--to", "LIN-2"],
    )

    with pytest.raises(SystemExit) as raised:
        cli.main()

    assert raised.value.code == expected_exit


def test_a_linear_run_prints_its_receipt_and_returns(
    monkeypatch: pytest.MonkeyPatch, stub_http: dict[str, Any], capsys: pytest.CaptureFixture[str]
) -> None:
    stub_http["responses"] = {
        "issueRelationCreate": {"issueRelationCreate": {"success": True,
                                                        "issueRelation": {"id": "rel-1"}}}
    }
    monkeypatch.setattr(
        sys,
        "argv",
        ["booping-tracker", "--config-file", str(FIXTURE_CONFIG),
         "relate", "--issue", "LIN-1", "--to", "LIN-2", "--type", "blocks"],
    )

    cli.main()

    assert capsys.readouterr().out == "relate LIN-1: blocks LIN-2\n"
