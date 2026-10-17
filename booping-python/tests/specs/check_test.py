from __future__ import annotations

from pathlib import Path

import pytest

from booping.cli import build_parser


def test_check_without_mdcheck_on_path_is_an_internal_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    project = tmp_path / "project"
    record = project / "vault" / "specs" / "value" / "0001-first.md"
    record.parent.mkdir(parents=True)
    record.write_text("---\ntype: value\ntitle: First\n---\n\nWhy.\n")
    (project / ".booping").write_text(
        "project_name: probe\nvault_path: ./vault\nlatest_migration: 9999\n"
    )
    empty = tmp_path / "empty-bin"
    empty.mkdir()
    monkeypatch.chdir(project)
    monkeypatch.setenv("PATH", str(empty))

    args = build_parser().parse_args(["specs", "check"])
    with pytest.raises(SystemExit) as exc:
        args.func(args)

    assert exc.value.code == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "error: mdcheck not found on PATH — cargo install markdown-checker\n"
