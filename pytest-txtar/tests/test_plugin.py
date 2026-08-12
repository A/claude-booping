from __future__ import annotations

import pytest

pytest_plugins = ["pytester"]

CONFTEST = """
import sys
from pathlib import Path

from pytest_txtar.case import TxtarSpec


def pytest_txtar_spec(config):
    return TxtarSpec(
        commands={"py": Path(sys.executable)},
        roots=("home", "cwd"),
        cwd_root="cwd",
        env={"HOME": "home"},
    )
"""

PASSING = '-- cmd --\npy -c "print(\'hello\')"\n-- exit --\n0\n-- stdout --\nhello\n'
MISMATCHING = '-- cmd --\npy -c "print(\'actual\')"\n-- exit --\n0\n-- stdout --\nwanted\n'


def write_cases(pytester: pytest.Pytester, **cases: str) -> None:
    directory = pytester.path / "cases"
    directory.mkdir(exist_ok=True)
    for name, text in cases.items():
        _ = (directory / f"{name}.txtar").write_text(text, encoding="utf-8")


def write_corpus(pytester: pytest.Pytester, **cases: str) -> None:
    _ = pytester.makeconftest(CONFTEST)
    write_cases(pytester, **cases)


def test_a_case_whose_assertions_hold_passes(pytester: pytest.Pytester):
    write_corpus(pytester, greet=PASSING)

    result = pytester.runpytest()

    result.assert_outcomes(passed=1)


def test_a_txtar_file_is_collected_without_any_test_module(pytester: pytest.Pytester):
    write_corpus(pytester, greet=PASSING)

    result = pytester.runpytest("--collect-only", "-q")

    result.stdout.fnmatch_lines(["cases/greet.txtar"])


def test_a_case_whose_output_differs_fails_with_the_unified_diff(pytester: pytest.Pytester):
    write_corpus(pytester, greet=MISMATCHING)

    result = pytester.runpytest()

    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines(
        ["=== stdout ===", "--- expected", "+++ actual", "@@ -1 +1 @@", "-wanted", "+actual"]
    )


def test_a_case_expecting_the_wrong_exit_code_fails(pytester: pytest.Pytester):
    write_corpus(pytester, boom='-- cmd --\npy -c "raise SystemExit(3)"\n-- exit --\n0\n')

    result = pytester.runpytest()

    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines(["=== exit ===", "*-0", "*+3"])


def test_a_malformed_case_is_an_error_naming_the_case_file(pytester: pytest.Pytester):
    write_corpus(pytester, broken="-- stdout --\nno command here\n")

    result = pytester.runpytest()

    result.assert_outcomes(errors=1)
    result.stdout.fnmatch_lines(["*broken.txtar: missing section: cmd*"])


def test_a_case_addressing_a_root_outside_the_spec_is_an_error(pytester: pytest.Pytester):
    write_corpus(pytester, stray='-- cmd --\npy -c "pass"\n-- fixtures/xdg/note.md --\nseed\n')

    result = pytester.runpytest()

    result.assert_outcomes(errors=1)
    result.stdout.fnmatch_lines(["*stray.txtar: fixtures/ path must start with*"])


def test_a_case_is_selected_by_name_with_dash_k(pytester: pytest.Pytester):
    write_corpus(pytester, greet=PASSING, other=PASSING)

    result = pytester.runpytest("-k", "greet", "-v")

    result.assert_outcomes(passed=1, deselected=1)
    result.stdout.fnmatch_lines(["cases/greet.txtar*PASSED*"])


def test_update_rewrites_a_mismatching_case_so_the_next_run_passes(pytester: pytest.Pytester):
    write_corpus(pytester, greet=MISMATCHING)
    case = pytester.path / "cases" / "greet.txtar"

    updated = pytester.runpytest("--txtar-update")

    updated.assert_outcomes(passed=1)
    assert case.read_text(encoding="utf-8") == (
        '-- cmd --\npy -c "print(\'actual\')"\n-- exit --\n0\n-- stdout --\nactual\n'
    )
    assert pytester.runpytest().ret == pytest.ExitCode.OK


def test_update_leaves_a_passing_case_untouched(pytester: pytest.Pytester):
    write_corpus(pytester, greet=PASSING)
    case = pytester.path / "cases" / "greet.txtar"
    before = case.stat().st_mtime_ns

    result = pytester.runpytest("--txtar-update")

    result.assert_outcomes(passed=1)
    assert case.read_text(encoding="utf-8") == PASSING
    assert case.stat().st_mtime_ns == before


def test_a_session_without_the_spec_hook_aborts_naming_it(pytester: pytest.Pytester):
    write_cases(pytester, greet=PASSING)

    result = pytester.runpytest()

    assert result.ret == pytest.ExitCode.USAGE_ERROR
    result.stderr.fnmatch_lines(["*pytest_txtar_spec*"])


def test_a_session_with_no_txtar_files_needs_no_spec_hook(pytester: pytest.Pytester):
    _ = pytester.makepyfile(test_ordinary="def test_ordinary():\n    assert True\n")

    result = pytester.runpytest()

    result.assert_outcomes(passed=1)
