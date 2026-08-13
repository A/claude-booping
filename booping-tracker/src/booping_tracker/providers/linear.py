"""The `linear` provider: every facade operation as raw GraphQL over an injectable transport."""

from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, cast

import yaml

from booping_tracker.config import TrackerConfig
from booping_tracker.errors import ProviderError, UserError
from booping_tracker.facade import (
    CommentResult,
    IssueComment,
    IssueCreateResult,
    IssueUpdateResult,
    RelateResult,
    ShowResult,
    StatesResult,
    SyncResult,
    WorkflowState,
)
from booping_tracker.providers.transport import HttpTransport, Transport

# `blocked_by` is deliberately absent: Linear models it as the inverse view of `blocks`.
RELATION_TYPES = ("blocks", "duplicate", "related", "similar")

TEAMS_QUERY = """
query Teams($key: String!) {
  teams(filter: { key: { eq: $key } }) { nodes { id key } }
}
"""

STATES_QUERY = """
query WorkflowStates($team: String!) {
  workflowStates(filter: { team: { key: { eq: $team } } }) {
    nodes { id name type position }
  }
}
"""

LABELS_QUERY = """
query IssueLabels($team: String!) {
  issueLabels(filter: { team: { key: { eq: $team } } }) { nodes { id name } }
}
"""

ISSUE_STATE_QUERY = """
query IssueState($id: String!) {
  issue(id: $id) { identifier url state { name } team { key } }
}
"""

COMMENT_CREATE = """
mutation CommentCreate($input: CommentCreateInput!) {
  commentCreate(input: $input) { success comment { id url } }
}
"""

ISSUE_CREATE = """
mutation IssueCreate($input: IssueCreateInput!) {
  issueCreate(input: $input) { success issue { id identifier url } }
}
"""

ISSUE_UPDATE = """
mutation IssueUpdate($id: String!, $input: IssueUpdateInput!) {
  issueUpdate(id: $id, input: $input) { success issue { id identifier url } }
}
"""

ISSUE_RELATION_CREATE = """
mutation IssueRelationCreate($input: IssueRelationCreateInput!) {
  issueRelationCreate(input: $input) { success issueRelation { id } }
}
"""


def show_query(with_comments: bool) -> str:
    comments = "comments { nodes { user { name } body } }" if with_comments else ""
    return f"""
query Issue($id: String!) {{
  issue(id: $id) {{
    identifier
    url
    title
    description
    state {{ name }}
    labels {{ nodes {{ name }} }}
    assignee {{ name }}
    {comments}
  }}
}}
"""


class LinearProvider:
    def __init__(
        self,
        *,
        transport: Transport,
        playbooks: Mapping[str, Any] | None = None,
    ) -> None:
        self._transport = transport
        self._playbooks: dict[str, Any] = dict(playbooks or {})
        self._team_ids: dict[str, str] = {}
        self._states: dict[str, list[WorkflowState]] = {}
        self._labels: dict[str, dict[str, str]] = {}

    @classmethod
    def from_config(cls, config: TrackerConfig) -> LinearProvider:
        settings = config.driver_settings()
        api_url = _text(settings.get("api_url"))
        if api_url is None:
            raise UserError("no api_url configured (core.tracker.linear.api_url)")
        key_env = _text(settings.get("api_key_env"))
        if key_env is None:
            raise UserError("no api_key_env configured (core.tracker.linear.api_key_env)")
        api_key = os.environ.get(key_env)
        if not api_key:
            raise UserError(f"{key_env} is unset; the linear driver needs an API key")
        playbooks: Any = settings.get("playbooks")
        return cls(
            transport=HttpTransport(api_url=api_url, api_key=api_key),
            playbooks=cast("dict[str, Any]", playbooks) if isinstance(playbooks, dict) else {},
        )

    def states(self, *, team: str) -> StatesResult:
        states = self._workflow_states(team)
        lines = [f"states {team}: {len(states)} states"]
        lines += [
            f"  {state.position:g} {state.name} ({state.type}) {state.id}" for state in states
        ]
        return StatesResult(
            verb="states", target=team, receipt="\n".join(lines), states=states
        )

    def show(self, *, issue: str, with_comments: bool) -> ShowResult:
        data = self._call("issue", show_query(with_comments), {"id": issue})
        node = _mapping(data.get("issue"))
        if not node:
            raise UserError(f"issue not found: {issue}")

        identifier = _text(node.get("identifier")) or issue
        title = _text(node.get("title"))
        state = _text(_mapping(node.get("state")).get("name"))
        url = _text(node.get("url"))
        labels = [
            name for label in _nodes(node.get("labels")) if (name := _text(label.get("name")))
        ]
        comments = [
            IssueComment(
                author=_text(_mapping(comment.get("user")).get("name")) or "unknown",
                body=_text(comment.get("body")) or "",
            )
            for comment in _nodes(node.get("comments"))
        ]
        return ShowResult(
            verb="show",
            target=identifier,
            receipt=f'show {identifier}: "{title}" [{state}] {url}',
            identifier=identifier,
            url=url,
            title=title,
            state=state,
            labels=labels,
            assignee=_text(_mapping(node.get("assignee")).get("name")),
            description=_text(node.get("description")),
            comments=comments,
        )

    def comment(self, *, issue: str, body: str) -> CommentResult:
        data = self._call(
            "commentCreate", COMMENT_CREATE, {"input": {"issueId": issue, "body": body}}
        )
        created = _mapping(self._payload(data, "commentCreate").get("comment"))
        url = _text(created.get("url"))
        return CommentResult(
            verb="comment", target=issue, receipt=f"comment {issue}: created {url}", url=url
        )

    def issue_create(
        self,
        *,
        team: str,
        title: str,
        body: str,
        parent: str | None,
        labels: Sequence[str],
        state: str | None,
    ) -> IssueCreateResult:
        payload: dict[str, Any] = {
            "teamId": self._team_id(team),
            "title": title,
            "description": body,
        }
        if parent:
            payload["parentId"] = parent
        if labels:
            payload["labelIds"] = [self._label_id(team, name) for name in labels]
        if state:
            payload["stateId"] = self._state_id(team, state)

        data = self._call("issueCreate", ISSUE_CREATE, {"input": payload})
        created = _mapping(self._payload(data, "issueCreate").get("issue"))
        identifier = _text(created.get("identifier"))
        url = _text(created.get("url"))
        suffix = f" (sub-issue of {parent})" if parent else ""
        return IssueCreateResult(
            verb="issue-create",
            target=team,
            receipt=f"issue-create {team}: created {identifier} {url}{suffix}",
            identifier=identifier,
            url=url,
        )

    def issue_update(
        self,
        *,
        issue: str,
        state: str | None,
        title: str | None,
        body: str | None,
        add_labels: Sequence[str],
        remove_labels: Sequence[str],
        assignee: str | None,
    ) -> IssueUpdateResult:
        payload: dict[str, Any] = {}
        if state or add_labels or remove_labels:
            team = self._issue_team(issue)
            if state:
                payload["stateId"] = self._state_id(team, state)
            # Added and removed discretely: a wholesale labelIds would clobber a label a
            # human set on the issue meanwhile.
            if add_labels:
                payload["addedLabelIds"] = [self._label_id(team, name) for name in add_labels]
            if remove_labels:
                payload["removedLabelIds"] = [self._label_id(team, name) for name in remove_labels]
        if title:
            payload["title"] = title
        if body is not None:
            payload["description"] = body
        if assignee:
            payload["assigneeId"] = assignee

        if not payload:
            return IssueUpdateResult(
                verb="issue-update",
                target=issue,
                receipt=f"issue-update {issue}: nothing to update",
            )
        return self._update(issue, payload, f"issue-update {issue}: updated")

    def relate(self, *, issue: str, to: str, relation: str) -> RelateResult:
        if relation not in RELATION_TYPES:
            raise UserError(
                f"unknown relation type: {relation} (accepted: {', '.join(RELATION_TYPES)})"
            )
        data = self._call(
            "issueRelationCreate",
            ISSUE_RELATION_CREATE,
            {"input": {"issueId": issue, "relatedIssueId": to, "type": relation}},
        )
        created = _mapping(self._payload(data, "issueRelationCreate").get("issueRelation"))
        relation_id = _text(created.get("id"))
        return RelateResult(
            verb="relate",
            target=issue,
            receipt=f"relate {issue}: {relation} {to}",
            relation_id=relation_id,
        )

    def sync(self, *, artifact: Path, playbook: str | None) -> SyncResult:
        frontmatter = _frontmatter(artifact)
        issue = _text(frontmatter.get("tracker_issue"))
        if issue is None:
            return SyncResult(
                verb="sync",
                target=str(artifact),
                receipt=f"sync {artifact}: no tracker_issue, nothing to push",
            )

        name = self._playbook_name(playbook)
        status = _text(frontmatter.get("status"))
        statuses = _statuses(self._playbooks, name)
        target_state = _text(statuses.get(status)) if status is not None else None
        if target_state is None:
            raise UserError(
                f"no Linear state mapped for status {status!r} "
                f"(core.tracker.linear.playbooks.{name}.statuses)"
            )

        current = _mapping(self._call("issue", ISSUE_STATE_QUERY, {"id": issue}).get("issue"))
        if not current:
            raise UserError(f"issue not found: {issue}")
        identifier = _text(current.get("identifier")) or issue
        current_state = _text(_mapping(current.get("state")).get("name"))
        if current_state == target_state:
            return SyncResult(
                verb="sync",
                target=identifier,
                receipt=f'sync {identifier}: state "{target_state}" (unchanged)',
                issue=identifier,
                state=target_state,
            )

        team = _text(_mapping(current.get("team")).get("key"))
        if team is None:
            raise ProviderError(f"issue {identifier} carries no team")
        result = self._update(
            issue,
            {"stateId": self._state_id(team, target_state)},
            f'sync {identifier}: state "{target_state}" (was "{current_state}")',
        )
        return SyncResult(
            verb="sync",
            target=identifier,
            receipt=result.receipt,
            issue=identifier,
            state=target_state,
            changed=True,
        )

    def _update(self, issue: str, payload: dict[str, Any], receipt: str) -> IssueUpdateResult:
        data = self._call("issueUpdate", ISSUE_UPDATE, {"id": issue, "input": payload})
        updated = _mapping(self._payload(data, "issueUpdate").get("issue"))
        return IssueUpdateResult(
            verb="issue-update",
            target=issue,
            receipt=receipt,
            identifier=_text(updated.get("identifier")),
            url=_text(updated.get("url")),
        )

    def _call(self, operation: str, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        return self._transport.execute(operation=operation, query=query, variables=variables)

    def _payload(self, data: dict[str, Any], operation: str) -> dict[str, Any]:
        payload = _mapping(data.get(operation))
        if not payload:
            raise ProviderError(f"{operation}: response carried no payload")
        if payload.get("success") is False:
            raise ProviderError(f"{operation}: Linear reported failure")
        return payload

    def _playbook_name(self, playbook: str | None) -> str:
        if playbook is None:
            if len(self._playbooks) != 1:
                raise UserError(
                    "no playbook given and none can be inferred "
                    f"(configured: {', '.join(sorted(self._playbooks)) or 'none'})"
                )
            playbook = next(iter(self._playbooks))
        if playbook not in self._playbooks:
            raise UserError(
                f"no tracker mapping for playbook {playbook} "
                f"(configured: {', '.join(sorted(self._playbooks)) or 'none'})"
            )
        return playbook

    def _team_id(self, team: str) -> str:
        if team not in self._team_ids:
            nodes = _nodes(self._call("teams", TEAMS_QUERY, {"key": team}).get("teams"))
            found = _mapping(next((node for node in nodes if _text(node.get("key")) == team), None))
            team_id = _text(found.get("id"))
            if team_id is None:
                keys = [key for node in nodes if (key := _text(node.get("key")))]
                raise UserError(f"unknown team: {team} (available: {_listing(keys)})")
            self._team_ids[team] = team_id
        return self._team_ids[team]

    def _issue_team(self, issue: str) -> str:
        node = _mapping(self._call("issue", ISSUE_STATE_QUERY, {"id": issue}).get("issue"))
        team = _text(_mapping(node.get("team")).get("key"))
        if team is None:
            raise UserError(f"issue not found: {issue}")
        return team

    def _workflow_states(self, team: str) -> list[WorkflowState]:
        if team not in self._states:
            data = self._call("workflowStates", STATES_QUERY, {"team": team})
            nodes = _nodes(data.get("workflowStates"))
            states = [
                WorkflowState(
                    id=_text(node.get("id")) or "",
                    name=_text(node.get("name")) or "",
                    type=_text(node.get("type")) or "",
                    position=_number(node.get("position")),
                )
                for node in nodes
            ]
            self._states[team] = sorted(states, key=lambda state: state.position)
        return self._states[team]

    def _state_id(self, team: str, name: str) -> str:
        for state in self._workflow_states(team):
            if state.name == name:
                return state.id
        available = [state.name for state in self._workflow_states(team)]
        raise UserError(f"unknown state: {name} (team {team} has: {_listing(available)})")

    def _label_id(self, team: str, name: str) -> str:
        if team not in self._labels:
            data = self._call("issueLabels", LABELS_QUERY, {"team": team})
            nodes = _nodes(data.get("issueLabels"))
            self._labels[team] = {
                label: identifier
                for node in nodes
                if (label := _text(node.get("name"))) and (identifier := _text(node.get("id")))
            }
        labels = self._labels[team]
        if name not in labels:
            raise UserError(f"unknown label: {name} (team {team} has: {_listing(sorted(labels))})")
        return labels[name]


def _statuses(playbooks: Mapping[str, Any], name: str) -> dict[str, Any]:
    return _mapping(_mapping(playbooks.get(name)).get("statuses"))


def _frontmatter(artifact: Path) -> dict[str, Any]:
    try:
        text = artifact.read_text(encoding="utf-8")
    except OSError as exc:
        raise UserError(f"could not read artifact {artifact}: {exc}") from exc
    if not text.startswith("---\n"):
        raise UserError(f"artifact carries no frontmatter: {artifact}")
    _, _, rest = text.partition("---\n")
    block, fence, _ = rest.partition("\n---")
    if not fence:
        raise UserError(f"artifact carries no frontmatter: {artifact}")
    try:
        loaded: Any = yaml.safe_load(block)
    except yaml.YAMLError as exc:
        raise UserError(f"could not parse frontmatter of {artifact}: {exc}") from exc
    return cast("dict[str, Any]", loaded) if isinstance(loaded, dict) else {}


def _listing(names: Sequence[str]) -> str:
    return ", ".join(names) if names else "none"


def _mapping(value: Any) -> dict[str, Any]:
    return cast("dict[str, Any]", value) if isinstance(value, dict) else {}


def _nodes(connection: Any) -> list[dict[str, Any]]:
    raw: Any = _mapping(connection).get("nodes")
    if not isinstance(raw, list):
        return []
    return [
        cast("dict[str, Any]", item) for item in cast("list[Any]", raw) if isinstance(item, dict)
    ]


def _text(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


def _number(value: Any) -> float:
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else 0.0
