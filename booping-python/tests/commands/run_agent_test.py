from __future__ import annotations

import argparse
import io
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from booping.commands import run_agent as ra
from booping.context import Context
from tests.helpers import get_fixture_path


@pytest.fixture(autouse=True)
def clean_booping_log() -> Any:
    """Remove `.booping.log` from the shared fixture vault before and after each test
    so cli-run tests don't accumulate log lines across runs."""
    log = get_fixture_path("vault-with-cli-agent") / "_booping" / ".booping.log"
    log.unlink(missing_ok=True)
    yield
    log.unlink(missing_ok=True)


def _make_args(agent_id: str, briefing_file: Path | None = None) -> argparse.Namespace:
    return argparse.Namespace(id=agent_id, briefing_file=briefing_file)


def _assemble_fixture_ctx() -> Context:
    plugin_root = Path(__file__).resolve().parents[3]
    vault = get_fixture_path("vault-with-cli-agent")
    ctx = Context.assemble(start=vault, plugin_root=plugin_root, vault_override=vault)
    # Point project.directory at the fixture vault so extension lookup hits the
    # fixture's _booping/ rather than the real ~/Claude/<name>/_booping/.
    if ctx.project is not None:
        ctx.project.directory = vault
    return ctx


def _stdin(monkeypatch: pytest.MonkeyPatch, content: str) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO(content))
    monkeypatch.setattr(ra, "stdin_is_tty", lambda: False)


# ---- Unit-level helpers ----


def test_render_command_appends_prompt_when_no_placeholder() -> None:
    argv = ra.render_command("cat", "hello world")
    assert argv == ["cat", "hello world"]


def test_render_command_substitutes_placeholder() -> None:
    argv = ra.render_command('echo {{ prompt }}', "hi")
    assert argv == ["echo", "hi"]


def test_render_command_quotes_shell_metacharacters() -> None:
    # When no placeholder, prompt is appended raw as an argv element (no shell sees it).
    argv = ra.render_command("cat", "$VAR `boom` 'q' \"q\"\nnewline")
    assert argv == ["cat", "$VAR `boom` 'q' \"q\"\nnewline"]


def test_render_command_quotes_metachars_in_placeholder() -> None:
    """`shlex.quote` makes the prompt a single argv element regardless of metachars."""
    argv = ra.render_command("echo {{ prompt }}", "$VAR `boom` two words")
    assert argv == ["echo", "$VAR `boom` two words"]


def test_compose_prompt_with_extension() -> None:
    assert ra.compose_prompt("ext", "brief") == "ext\n\n---\n\nbrief"


def test_compose_prompt_empty_extension() -> None:
    assert ra.compose_prompt("", "brief") == "brief"
    assert ra.compose_prompt("   \n", "brief") == "brief"


def test_read_extension_missing_file_returns_empty(tmp_path: Path) -> None:
    assert ra.read_extension(tmp_path, "no-such-agent") == ""


def test_read_extension_none_vault_returns_empty() -> None:
    assert ra.read_extension(None, "anything") == ""


# ---- Handler-level (calls _run_with_context with fixture ctx) ----


def _run_capture(
    ctx: Context,
    monkeypatch: pytest.MonkeyPatch,
    capfd: pytest.CaptureFixture[str],
    args: argparse.Namespace,
    stdin_text: str | None = None,
) -> tuple[int, str, str]:
    """Invoke the handler and capture (exit_code, stdout, stderr)."""
    if stdin_text is not None:
        _stdin(monkeypatch, stdin_text)
    with pytest.raises(SystemExit) as ei:
        ra.run_with_context(args, ctx)
    out = capfd.readouterr()
    code = ei.value.code if isinstance(ei.value.code, int) else 1
    return code, out.out, out.err


def test_agent_not_found_exits_2(
    monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    ctx = _assemble_fixture_ctx()
    code, _out, err = _run_capture(ctx, monkeypatch, capfd, _make_args("no-such"))
    assert code == 2
    assert "not found" in err


def test_internal_agent_exits_2(
    monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    ctx = _assemble_fixture_ctx()
    code, _out, err = _run_capture(ctx, monkeypatch, capfd, _make_args("booping-developer"))
    assert code == 2
    assert "internal" in err


def test_type_agent_default_exits_2(
    monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    ctx = _assemble_fixture_ctx()
    code, _out, err = _run_capture(ctx, monkeypatch, capfd, _make_args("test-no-type"))
    assert code == 2
    assert "agent" in err.lower()


def test_cli_agent_without_extension_briefing_only(
    monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    ctx = _assemble_fixture_ctx()
    _stdin(monkeypatch, "BRIEFING")
    args = _make_args("test-cli-with-placeholder")
    with pytest.raises(SystemExit) as ei:
        ra.run_with_context(args, ctx)
    out = capfd.readouterr()
    assert ei.value.code == 0
    assert out.out == "BRIEFING"


def test_no_placeholder_appends_prompt_as_last_arg(
    monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    """Fixture `test-cli` uses `printf %s` (no placeholder). The composed prompt
    (extension + separator + briefing) must be appended as the last positional arg
    and printed verbatim."""
    ctx = _assemble_fixture_ctx()
    _stdin(monkeypatch, "BRIEFING")
    args = _make_args("test-cli")
    with pytest.raises(SystemExit) as ei:
        ra.run_with_context(args, ctx)
    out = capfd.readouterr()
    assert ei.value.code == 0
    assert out.out == "EXTENSION CONTENT for test-cli agent.\n\n\n---\n\nBRIEFING"


def test_cli_agent_extension_prepended(
    monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """test-cli has an extension file but command is `cat` (no placeholder).
    Use a custom fixture-on-the-fly: rewrite ctx config's command to use the placeholder
    so we can observe extension+separator+briefing on stdout via printf."""
    ctx = _assemble_fixture_ctx()
    # Swap command on test-cli to use placeholder so stdout shows the composed prompt
    ctx.config["skills"]["develop"]["agents"]["test-cli"]["command"] = (
        'sh -c "printf %s \\"$1\\"" -- {{ prompt }}'
    )
    _stdin(monkeypatch, "BRIEFING")
    args = _make_args("test-cli")
    with pytest.raises(SystemExit) as ei:
        ra.run_with_context(args, ctx)
    out = capfd.readouterr()
    assert ei.value.code == 0
    # extension file ends in `\n`; separator is `\n\n---\n\n`
    assert out.out == "EXTENSION CONTENT for test-cli agent.\n\n\n---\n\nBRIEFING"


def test_briefing_file_path(
    monkeypatch: pytest.MonkeyPatch,
    capfd: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    ctx = _assemble_fixture_ctx()
    briefing = tmp_path / "brief.md"
    briefing.write_text("FROM FILE")
    args = _make_args("test-cli-with-placeholder", briefing_file=briefing)
    with pytest.raises(SystemExit) as ei:
        ra.run_with_context(args, ctx)
    out = capfd.readouterr()
    assert ei.value.code == 0
    assert out.out == "FROM FILE"


def test_nonzero_child_exit_propagates(
    monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    ctx = _assemble_fixture_ctx()
    _stdin(monkeypatch, "x")
    args = _make_args("test-cli-fail")
    with pytest.raises(SystemExit) as ei:
        ra.run_with_context(args, ctx)
    assert ei.value.code == 7


def test_tty_stdin_guard(
    monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    ctx = _assemble_fixture_ctx()
    monkeypatch.setattr(ra, "stdin_is_tty", lambda: True)
    args = _make_args("test-cli-with-placeholder")
    with pytest.raises(SystemExit) as ei:
        ra.run_with_context(args, ctx)
    out = capfd.readouterr()
    assert ei.value.code == 2
    assert "TTY" in out.err or "tty" in out.err


def test_metachars_in_prompt_no_injection(
    monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    """Shell metacharacters in the briefing must reach the child process as literal
    text — not expanded by the shell that `command: 'sh -c ...'` invokes."""
    ctx = _assemble_fixture_ctx()
    _stdin(monkeypatch, "$HOME `whoami` 'q' \"q\"\nnewline")
    args = _make_args("test-cli-with-placeholder")
    with pytest.raises(SystemExit) as ei:
        ra.run_with_context(args, ctx)
    out = capfd.readouterr()
    assert ei.value.code == 0
    assert out.out == "$HOME `whoami` 'q' \"q\"\nnewline"


# ---- Subprocess --help integration ----


def test_run_agent_help_lists_subcommand() -> None:
    plugin_root = Path(__file__).resolve().parents[3]
    booping_bin = plugin_root / "bin" / "booping"
    result = subprocess.run(
        [str(booping_bin), "run-agent", "--help"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "run-agent" in result.stdout or "id" in result.stdout
    assert "--briefing-file" in result.stdout


# ---- type: agent (no-type defaults to agent) explicit case ----


def test_log_invocation_appends_line_to_booping_log(
    monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    """A successful cli-agent invocation appends one line to
    `<vault>/_booping/.booping.log` with the documented format."""
    import re

    ctx = _assemble_fixture_ctx()
    _stdin(monkeypatch, "BRIEFING")
    args = _make_args("test-cli")
    with pytest.raises(SystemExit) as ei:
        ra.run_with_context(args, ctx)
    _ = capfd.readouterr()
    assert ei.value.code == 0

    assert ctx.project is not None
    log_path = ctx.project.directory / "_booping" / ".booping.log"
    assert log_path.is_file()
    lines = log_path.read_text().splitlines()
    assert len(lines) == 1
    # Format: `<iso8601-utc>: [run-agent] <id>: `<command>``
    pattern = (
        r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z: \[run-agent\] test-cli: `printf %s`$"
    )
    assert re.match(pattern, lines[0]), f"unexpected log line: {lines[0]!r}"


def test_log_invocation_no_project_no_file(tmp_path: Path) -> None:
    """When ctx.project is None, log_invocation is a no-op (no crash, no file)."""
    ra.log_invocation(None, "any-id", "any-command")
    # Sanity: passing a real vault writes the file.
    ra.log_invocation(tmp_path, "x", "y")
    assert (tmp_path / "_booping" / ".booping.log").is_file()


def test_log_invocation_appends_not_overwrites(tmp_path: Path) -> None:
    ra.log_invocation(tmp_path, "first", "cmd1")
    ra.log_invocation(tmp_path, "second", "cmd2")
    lines = (tmp_path / "_booping" / ".booping.log").read_text().splitlines()
    assert len(lines) == 2
    assert "first: `cmd1`" in lines[0]
    assert "second: `cmd2`" in lines[1]


def test_resolve_agent_returns_first_match() -> None:
    cfg: dict[str, Any] = {
        "skills": {
            "a": {"agents": {"x": {"type": "cli", "command": "cat"}}},
            "b": {"agents": {"x": {"type": "cli", "command": "echo"}}},
        }
    }
    resolved = ra.resolve_agent(cfg, "x")
    assert resolved is not None
    skill, entry = resolved
    assert skill == "a"
    assert entry["command"] == "cat"
