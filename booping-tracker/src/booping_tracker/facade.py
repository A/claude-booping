"""The operation set every tracker provider implements, and the results they return."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class OperationResult:
    verb: str
    target: str
    receipt: str


@dataclass(frozen=True)
class WorkflowState:
    id: str
    name: str
    type: str
    position: float


@dataclass(frozen=True)
class IssueComment:
    author: str
    body: str


@dataclass(frozen=True)
class StatesResult(OperationResult):
    states: list[WorkflowState] = field(default_factory=list[WorkflowState])


@dataclass(frozen=True)
class ShowResult(OperationResult):
    identifier: str | None = None
    url: str | None = None
    title: str | None = None
    state: str | None = None
    labels: list[str] = field(default_factory=list[str])
    assignee: str | None = None
    description: str | None = None
    comments: list[IssueComment] = field(default_factory=list[IssueComment])


@dataclass(frozen=True)
class CommentResult(OperationResult):
    url: str | None = None


@dataclass(frozen=True)
class IssueCreateResult(OperationResult):
    identifier: str | None = None
    url: str | None = None


@dataclass(frozen=True)
class IssueUpdateResult(OperationResult):
    identifier: str | None = None
    url: str | None = None


@dataclass(frozen=True)
class RelateResult(OperationResult):
    relation_id: str | None = None


@dataclass(frozen=True)
class SyncResult(OperationResult):
    issue: str | None = None
    state: str | None = None
    changed: bool = False


class TrackerProvider(Protocol):
    def states(self, *, team: str) -> StatesResult: ...

    def show(self, *, issue: str, with_comments: bool) -> ShowResult: ...

    def comment(self, *, issue: str, body: str) -> CommentResult: ...

    def issue_create(
        self,
        *,
        team: str,
        title: str,
        body: str,
        parent: str | None,
        labels: Sequence[str],
        state: str | None,
    ) -> IssueCreateResult: ...

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
    ) -> IssueUpdateResult: ...

    def relate(self, *, issue: str, to: str, relation: str) -> RelateResult: ...

    def sync(self, *, artifact: Path, playbook: str | None) -> SyncResult: ...
