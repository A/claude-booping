"""Argument parsing and dispatch for `booping-tracker`."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, NoReturn

from booping_tracker.config import ConfigError
from booping_tracker.config import load as load_config
from booping_tracker.errors import ProviderError, UserError
from booping_tracker.facade import OperationResult, TrackerProvider
from booping_tracker.logging import log, resolve_vault
from booping_tracker.providers import PROVIDERS


@dataclass(frozen=True)
class DryRunResult(OperationResult):
    driver: str = ""
    arguments: dict[str, str] = field(default_factory=dict[str, str])


@dataclass(frozen=True)
class Call:
    verb: str
    target: str
    arguments: dict[str, object]
    invoke: Callable[[TrackerProvider], OperationResult]


class TrackerParser(argparse.ArgumentParser):
    """Argparse exits 2 on a usage error; the tracker's contract says 1."""

    def error(self, message: str) -> NoReturn:
        self.exit(1, f"error: {message}\n")


def _add_global_flags(parser: argparse.ArgumentParser, *, suppress: bool) -> None:
    default: Any = argparse.SUPPRESS if suppress else None
    parser.add_argument("--driver", default=default, help="override core.tracker.driver")
    parser.add_argument(
        "--config-file",
        default=default,
        help="read the tracker config from this YAML file instead of booping config-get",
    )
    parser.add_argument(
        "--output",
        choices=("text", "json"),
        default=argparse.SUPPRESS if suppress else "text",
        help="receipt format (default: text)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=argparse.SUPPRESS if suppress else False,
        help="print the intended call and perform no write",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = TrackerParser(prog="booping-tracker", description="booping tracker CLI")
    _add_global_flags(parser, suppress=False)
    sub = parser.add_subparsers(dest="verb", metavar="<verb>")
    sub.required = True

    states = sub.add_parser("states", help="list a team's workflow states")
    states.add_argument("--team", required=True)

    show = sub.add_parser("show", help="read one issue")
    show.add_argument("--issue", required=True)
    show.add_argument("--with-comments", action="store_true")

    comment = sub.add_parser("comment", help="post a comment on an issue")
    comment.add_argument("--issue", required=True)
    body = comment.add_mutually_exclusive_group(required=True)
    body.add_argument("--body")
    body.add_argument("--body-file")

    create = sub.add_parser("issue-create", help="create an issue, or a sub-issue with --parent")
    create.add_argument("--team", required=True)
    create.add_argument("--title", required=True)
    create_body = create.add_mutually_exclusive_group(required=True)
    create_body.add_argument("--body")
    create_body.add_argument("--body-file")
    create.add_argument("--parent")
    create.add_argument("--label", action="append", default=[])
    create.add_argument("--state")

    update = sub.add_parser("issue-update", help="update an issue")
    update.add_argument("--issue", required=True)
    update.add_argument("--state")
    update.add_argument("--title")
    update.add_argument("--body-file")
    update.add_argument("--add-label", action="append", default=[])
    update.add_argument("--remove-label", action="append", default=[])
    update.add_argument("--assignee")

    relate = sub.add_parser("relate", help="create a relation between two issues")
    relate.add_argument("--issue", required=True)
    relate.add_argument("--to", required=True)
    relate.add_argument(
        "--type", dest="relation", choices=("related", "blocks", "duplicate", "similar"),
        default="related",
    )

    sync = sub.add_parser("sync", help="push an artifact's state to its issue")
    sync.add_argument("--artifact", required=True)
    sync.add_argument("--playbook")

    for verb_parser in (states, show, comment, create, update, relate, sync):
        _add_global_flags(verb_parser, suppress=True)

    return parser


def _read_body(text: str | None, path: str | None) -> str | None:
    if text is not None:
        return text
    if path is None:
        return None
    body_file = Path(path)
    if not body_file.is_file():
        raise UserError(f"body file not found: {path}")
    try:
        return body_file.read_text(encoding="utf-8")
    except OSError as exc:
        raise UserError(f"could not read body file {path}: {exc}") from exc


def _require_body(text: str | None, path: str | None) -> str:
    body = _read_body(text, path)
    if body is None:
        raise UserError("a body is required (--body or --body-file)")
    return body


def _plan(args: argparse.Namespace) -> Call:
    verb: str = args.verb
    if verb == "states":
        team: str = args.team
        return Call(verb, team, {"team": team}, lambda p: p.states(team=team))

    if verb == "show":
        issue: str = args.issue
        with_comments: bool = args.with_comments
        return Call(
            verb,
            issue,
            {"issue": issue, "with_comments": with_comments},
            lambda p: p.show(issue=issue, with_comments=with_comments),
        )

    if verb == "comment":
        issue = args.issue
        body = _require_body(args.body, args.body_file)
        return Call(
            verb,
            issue,
            {"issue": issue, "body": body},
            lambda p: p.comment(issue=issue, body=body),
        )

    if verb == "issue-create":
        team = args.team
        title: str = args.title
        body = _require_body(args.body, args.body_file)
        parent: str | None = args.parent
        labels: list[str] = args.label
        state: str | None = args.state
        return Call(
            verb,
            team,
            {
                "team": team,
                "title": title,
                "body": body,
                "parent": parent,
                "labels": labels,
                "state": state,
            },
            lambda p: p.issue_create(
                team=team, title=title, body=body, parent=parent, labels=labels, state=state
            ),
        )

    if verb == "issue-update":
        issue = args.issue
        state = args.state
        title_or_none: str | None = args.title
        body = _read_body(None, args.body_file)
        add_labels: list[str] = args.add_label
        remove_labels: list[str] = args.remove_label
        assignee: str | None = args.assignee
        return Call(
            verb,
            issue,
            {
                "issue": issue,
                "state": state,
                "title": title_or_none,
                "body": body,
                "add_labels": add_labels,
                "remove_labels": remove_labels,
                "assignee": assignee,
            },
            lambda p: p.issue_update(
                issue=issue,
                state=state,
                title=title_or_none,
                body=body,
                add_labels=add_labels,
                remove_labels=remove_labels,
                assignee=assignee,
            ),
        )

    if verb == "relate":
        issue = args.issue
        to: str = args.to
        relation: str = args.relation
        return Call(
            verb,
            issue,
            {"issue": issue, "to": to, "relation": relation},
            lambda p: p.relate(issue=issue, to=to, relation=relation),
        )

    artifact = Path(args.artifact)
    playbook: str | None = args.playbook
    return Call(
        verb,
        str(artifact),
        {"artifact": str(artifact), "playbook": playbook},
        lambda p: p.sync(artifact=artifact, playbook=playbook),
    )


def _dry_run(call: Call, driver: str) -> DryRunResult:
    arguments = {key: str(value) for key, value in call.arguments.items()}
    rendered = " ".join(f"{key}={value!r}" for key, value in sorted(arguments.items()))
    return DryRunResult(
        verb=call.verb,
        target=call.target,
        receipt=f"dry-run {call.verb} {call.target}: {driver} driver, would call {rendered}",
        driver=driver,
        arguments=arguments,
    )


def _emit(result: OperationResult, output: str) -> None:
    if output == "json":
        print(json.dumps(asdict(result), sort_keys=True))
    else:
        print(result.receipt)


def _fail(message: str, code: int) -> NoReturn:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(code)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        config = load_config(
            config_file=Path(args.config_file) if args.config_file else None,
            driver_override=args.driver,
            # A dry run reaches no provider, so it needs no API key.
            require_api_key=not args.dry_run,
        )
        factory = PROVIDERS.get(config.driver)
        if factory is None:
            raise UserError(f"driver not implemented: {config.driver}")
        call = _plan(args)
        result = _dry_run(call, config.driver) if args.dry_run else call.invoke(factory(config))
    except (ConfigError, UserError) as exc:
        _fail(str(exc), 1)
    except ProviderError as exc:
        _fail(str(exc), 2)

    _emit(result, args.output)
    log(resolve_vault(), result.verb, result.receipt)
