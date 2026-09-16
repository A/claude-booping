"""The `cli` provider: every operation is a receipt-printing no-op."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from booping_tracker.facade import (
    CommentResult,
    IssueCreateResult,
    IssueUpdateResult,
    RelateResult,
    ShowResult,
    StatesResult,
    SyncResult,
)

NO_OP = "cli driver, no-op"


def _receipt(verb: str, target: str) -> str:
    return f"{verb} {target}: {NO_OP}"


class CliProvider:
    def states(self, *, team: str) -> StatesResult:
        return StatesResult(verb="states", target=team, receipt=_receipt("states", team))

    def show(self, *, issue: str, with_comments: bool) -> ShowResult:
        return ShowResult(verb="show", target=issue, receipt=_receipt("show", issue))

    def comment(self, *, issue: str, body: str) -> CommentResult:
        return CommentResult(verb="comment", target=issue, receipt=_receipt("comment", issue))

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
        return IssueCreateResult(
            verb="issue-create", target=team, receipt=_receipt("issue-create", team)
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
        return IssueUpdateResult(
            verb="issue-update", target=issue, receipt=_receipt("issue-update", issue)
        )

    def relate(self, *, issue: str, to: str, relation: str) -> RelateResult:
        return RelateResult(verb="relate", target=issue, receipt=_receipt("relate", issue))

    def sync(self, *, artifact: Path, playbook: str | None) -> SyncResult:
        target = str(artifact)
        return SyncResult(verb="sync", target=target, receipt=_receipt("sync", target))
