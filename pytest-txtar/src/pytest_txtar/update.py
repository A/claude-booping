"""Rewriting a case's assertions from an actual run."""

from __future__ import annotations

from pytest_txtar import txtar
from pytest_txtar.case import Case
from pytest_txtar.compare import Outcome


def updated_archive(case: Case, outcome: Outcome) -> txtar.Archive:
    """The case with its assertions taken from the run; `cmd` and `fixtures/` kept.

    Sections already present keep their position; new ones are appended, so a
    second update over the same run is byte-identical.
    """
    fresh: dict[str, str] = {"exit": f"{outcome.exit_code}\n", "stdout": outcome.stdout}
    if outcome.stderr or case.stderr is not None:
        fresh["stderr"] = outcome.stderr
    for name, previous in case.expected:
        actual = outcome.files[name]
        fresh[name] = previous if actual is None else actual

    files: list[tuple[str, str]] = []
    for name, data in case.archive.files:
        files.append((name, fresh.pop(name, data)))
    files.extend(fresh.items())
    return txtar.Archive(comment=case.archive.comment, files=files)
