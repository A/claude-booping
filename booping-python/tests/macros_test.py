from __future__ import annotations

import subprocess
from typing import Any

import pytest

from booping import macros


def _cfg(**extra: Any) -> dict[str, Any]:
    return {"macros": {"now": ["echo", "stamped"]}, **extra}


def test_macro_returns_stripped_stdout() -> None:
    macros.clear_cache()
    macro = macros.make_macro(_cfg())

    assert macro("macros.now") == "stamped"


def test_repeated_calls_spawn_one_subprocess(monkeypatch: pytest.MonkeyPatch) -> None:
    macros.clear_cache()
    calls: list[list[str]] = []

    def counting_run(
        argv: list[str], **_kwargs: Any
    ) -> subprocess.CompletedProcess[str]:
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 0, "stamped\n", "")

    monkeypatch.setattr(macros.subprocess, "run", counting_run)
    macro = macros.make_macro(_cfg())

    assert macro("macros.now") == macro("macros.now") == "stamped"
    assert len(calls) == 1


def test_positional_args_append_to_the_declared_prefix() -> None:
    macros.clear_cache()
    macro = macros.make_macro({"macros": {"say": ["echo"]}})

    assert macro("macros.say", "hello", "there") == "hello there"


def test_distinct_args_are_distinct_cache_entries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    macros.clear_cache()
    calls: list[list[str]] = []

    def counting_run(
        argv: list[str], **_kwargs: Any
    ) -> subprocess.CompletedProcess[str]:
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 0, f"{argv[-1]}\n", "")

    monkeypatch.setattr(macros.subprocess, "run", counting_run)
    macro = macros.make_macro({"macros": {"date": ["date"]}})

    assert macro("macros.date", "+%H") == "+%H"
    assert macro("macros.date", "+%M") == "+%M"
    assert macro("macros.date", "+%H") == "+%H"
    assert calls == [["date", "+%H"], ["date", "+%M"]]


def test_nonzero_exit_names_macro_and_code() -> None:
    macro = macros.make_macro({"macros": {"boom": ["sh", "-c", "exit 3"]}})

    with pytest.raises(macros.MacroError) as exc:
        macro("macros.boom")

    assert "macros.boom" in str(exc.value)
    assert "exited 3" in str(exc.value)


def test_failure_message_carries_the_args_that_produced_it() -> None:
    macros.clear_cache()
    macro = macros.make_macro({"macros": {"boom": ["sh", "-c"]}})

    with pytest.raises(macros.MacroError) as exc:
        macro("macros.boom", "exit 4")

    assert "macros.boom exit 4" in str(exc.value)


def test_missing_executable_is_a_distinct_message() -> None:
    macro = macros.make_macro({"macros": {"gone": ["booping-no-such-binary-xyz"]}})

    with pytest.raises(macros.MacroError) as exc:
        macro("macros.gone")

    assert "executable not found" in str(exc.value)
    assert "booping-no-such-binary-xyz" in str(exc.value)


def test_unresolvable_path_names_the_path() -> None:
    macro = macros.make_macro(_cfg())

    with pytest.raises(macros.MacroError) as exc:
        macro("macros.absent")

    assert "macros.absent" in str(exc.value)


def test_non_list_value_is_rejected() -> None:
    macro = macros.make_macro({"macros": {"now": "date +%s"}})

    with pytest.raises(macros.MacroError) as exc:
        macro("macros.now")

    assert "argv list" in str(exc.value)


def test_stub_returns_literal_without_executing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden(*_args: Any, **_kwargs: Any) -> Any:
        raise AssertionError("subprocess must not run for a stubbed macro")

    monkeypatch.setattr(macros.subprocess, "run", forbidden)
    macro = macros.make_macro(
        _cfg(macro_stubs={"macros.now": "19700101-00-00"}),
    )

    assert macro("macros.now") == "19700101-00-00"


def test_path_stub_covers_every_argument_variant(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden(*_args: Any, **_kwargs: Any) -> Any:
        raise AssertionError("subprocess must not run for a stubbed macro")

    monkeypatch.setattr(macros.subprocess, "run", forbidden)
    macro = macros.make_macro(
        {"macros": {"date": ["date"]}, "macro_stubs": {"macros.date": "1970"}},
    )

    assert macro("macros.date", "+%Y") == macro("macros.date", "+%H:%M") == "1970"


def test_args_qualified_stub_pins_one_call_and_wins_over_the_path_stub(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden(*_args: Any, **_kwargs: Any) -> Any:
        raise AssertionError("subprocess must not run for a stubbed macro")

    monkeypatch.setattr(macros.subprocess, "run", forbidden)
    macro = macros.make_macro(
        {
            "macros": {"date": ["date"]},
            "macro_stubs": {
                "macros.date": "fallback",
                "macros.date +%Y%m%d%H%M": "197001010000",
                "macros.date +%Y-%m-%d %H:%M": "1970-01-01 00:00",
            },
        },
    )

    assert macro("macros.date", "+%Y%m%d%H%M") == "197001010000"
    assert macro("macros.date", "+%Y-%m-%d %H:%M") == "1970-01-01 00:00"
    assert macro("macros.date", "+%s") == "fallback"


def test_stub_of_undeclared_macro_still_resolves() -> None:
    macro = macros.make_macro({"macro_stubs": {"macros.ghost": "x"}})

    assert macro("macros.ghost") == "x"


def test_parse_stub_macros_keeps_dotted_key_literal() -> None:
    assert macros.parse_stub_macros(["macros.now=19700101-00-00"]) == {
        "macros.now": "19700101-00-00"
    }


def test_parse_stub_macros_keeps_args_in_the_key() -> None:
    assert macros.parse_stub_macros(["macros.date +%Y-%m-%d %H:%M=1970-01-01 00:00"]) == {
        "macros.date +%Y-%m-%d %H:%M": "1970-01-01 00:00"
    }


def test_parse_stub_macros_rejects_pair_without_equals() -> None:
    with pytest.raises(ValueError, match="nope"):
        macros.parse_stub_macros(["nope"])


def test_parse_stub_overrides_wraps_under_the_stub_key() -> None:
    assert macros.parse_stub_overrides(["a.b=c"]) == {macros.STUB_KEY: {"a.b": "c"}}
    assert macros.parse_stub_overrides([]) == {}
