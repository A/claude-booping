"""Pytest integration: `*.txtar` files collect and run as test items."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING, cast

import pytest

from pytest_txtar import hooks, txtar
from pytest_txtar.case import Case, CaseError, TxtarSpec, load_case
from pytest_txtar.compare import Mismatch, Outcome, compare, report
from pytest_txtar.sandbox import run_case
from pytest_txtar.update import updated_archive

if TYPE_CHECKING:
    from _pytest._code.code import TerminalRepr, TracebackStyle
    from _pytest.terminal import TerminalReporter

SPEC_KEY = pytest.StashKey[TxtarSpec]()
ASKED_KEY = pytest.StashKey[bool]()
SEEN_KEY = pytest.StashKey[bool]()
REWRITTEN_KEY = pytest.StashKey[list[str]]()


class Mismatched(Exception):
    def __init__(self, mismatches: list[Mismatch]) -> None:
        super().__init__(", ".join(mismatch.label for mismatch in mismatches))
        self.mismatches = mismatches


def pytest_addhooks(pluginmanager: pytest.PytestPluginManager) -> None:
    pluginmanager.add_hookspecs(hooks)


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--txtar-update",
        action="store_true",
        default=False,
        help="Rewrite mismatching txtar cases' assertions from the actual run",
    )


def pytest_configure(config: pytest.Config) -> None:
    config.stash[REWRITTEN_KEY] = []


def pytest_collect_file(file_path: Path, parent: pytest.Collector) -> TxtarFile | None:
    if file_path.suffix != ".txtar":
        return None
    parent.config.stash[SEEN_KEY] = True
    if session_spec(parent.config) is None:
        return None
    return TxtarFile.from_parent(parent, path=file_path)  # pyright: ignore[reportUnknownMemberType]


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if config.stash.get(SEEN_KEY, False) and SPEC_KEY not in config.stash:
        raise pytest.UsageError(
            "txtar cases collected but no pytest_txtar_spec hook implementation was found: "
            "implement pytest_txtar_spec(config) in conftest.py, returning a TxtarSpec"
        )


def pytest_terminal_summary(
    terminalreporter: TerminalReporter, exitstatus: int, config: pytest.Config
) -> None:
    rewritten = config.stash[REWRITTEN_KEY]
    if not rewritten:
        return
    terminalreporter.write_sep("-", "txtar cases rewritten")
    for nodeid in rewritten:
        terminalreporter.write_line(nodeid)


def session_spec(config: pytest.Config) -> TxtarSpec | None:
    """The consumer's spec, asked of the hook once per session."""
    if not config.stash.get(ASKED_KEY, False):
        config.stash[ASKED_KEY] = True
        resolved = cast(TxtarSpec | None, config.hook.pytest_txtar_spec(config=config))
        if resolved is not None:
            config.stash[SPEC_KEY] = resolved
    return config.stash.get(SPEC_KEY, None)


class TxtarFile(pytest.File):
    def collect(self) -> Iterator[TxtarItem]:
        spec = self.config.stash[SPEC_KEY]
        try:
            case = load_case(self.path, spec)
        except CaseError as exc:
            raise self.CollectError(f"{self.path}: {exc}") from exc
        yield TxtarItem.from_parent(  # pyright: ignore[reportUnknownMemberType]
            self, name=self.path.name, nodeid=self.nodeid, case=case, spec=spec
        )


class TxtarItem(pytest.Item):
    def __init__(
        self,
        *,
        name: str,
        parent: TxtarFile,
        nodeid: str,
        case: Case,
        spec: TxtarSpec,
    ) -> None:
        super().__init__(  # pyright: ignore[reportUnknownMemberType]
            name=name, parent=parent, nodeid=nodeid
        )
        self.case: Case = case
        self.spec: TxtarSpec = spec

    def runtest(self) -> None:
        outcome = run_case(self.case, self.spec)
        if cast(bool, self.config.getoption("--txtar-update")):
            self.rewrite(outcome)
            return
        mismatches = compare(self.case, outcome)
        if mismatches:
            raise Mismatched(mismatches)

    def rewrite(self, outcome: Outcome) -> None:
        text = txtar.serialize(updated_archive(self.case, outcome))
        if text == self.path.read_text(encoding="utf-8"):
            return
        _ = self.path.write_text(text, encoding="utf-8")
        self.config.stash[REWRITTEN_KEY].append(self.nodeid)

    def repr_failure(
        self,
        excinfo: pytest.ExceptionInfo[BaseException],
        style: TracebackStyle | None = None,
    ) -> str | TerminalRepr:
        if isinstance(excinfo.value, Mismatched):
            return "\n".join(report(mismatch) for mismatch in excinfo.value.mismatches)
        return super().repr_failure(excinfo, style)

    # The domain is the stem, not the file name: pytest rewrites a domain the
    # nodeid ends with, which would turn "greet.txtar" into "greet::txtar".
    def reportinfo(self) -> tuple[Path, int, str]:
        return self.path, 0, self.path.stem
