from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from booping import rendering
from booping.commands import build as build_cmd


def _make_fixture_plugin(tmp_path: Path) -> Path:
    """Build a minimal plugin tree with src/files/ + src/config_files.yaml."""
    plugin = tmp_path / "plugin"
    (plugin / "bin").mkdir(parents=True)
    (plugin / "bin" / "booping").write_text("#!/bin/sh\n")
    (plugin / "src").mkdir()

    (plugin / "src" / "config_files.yaml").write_text(
        "skills:\n  foo: { effort: low }\nagents:\n  bar: { effort: high }\n"
    )

    skill_tpl = plugin / "src" / "files" / "skills" / "foo" / "SKILL.md.j2"
    skill_tpl.parent.mkdir(parents=True)
    skill_tpl.write_text(
        "---\nname: foo\neffort: {{ skills.foo.effort }}\n---\n\nbody\n"
    )

    agent_tpl = plugin / "src" / "files" / "agents" / "bar.md.j2"
    agent_tpl.parent.mkdir(parents=True)
    agent_tpl.write_text(
        '---\nname: bar\neffort: {{ agents["bar"].effort }}\n---\n\nbody\n'
    )

    return plugin


@pytest.fixture
def fixture_plugin(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    plugin = _make_fixture_plugin(tmp_path)
    monkeypatch.setattr(rendering, "_plugin_root", plugin)
    return plugin


def test_build_writes_rendered_files(
    fixture_plugin: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    build_cmd.run(argparse.Namespace())

    skill_out = fixture_plugin / "skills" / "foo" / "SKILL.md"
    agent_out = fixture_plugin / "agents" / "bar.md"
    assert skill_out.read_text() == "---\nname: foo\neffort: low\n---\n\nbody\n"
    assert agent_out.read_text() == "---\nname: bar\neffort: high\n---\n\nbody\n"

    captured = capsys.readouterr()
    assert "wrote 2 files" in captured.err


def test_build_is_idempotent(fixture_plugin: Path) -> None:
    build_cmd.run(argparse.Namespace())
    skill_out = fixture_plugin / "skills" / "foo" / "SKILL.md"
    agent_out = fixture_plugin / "agents" / "bar.md"
    first_skill = skill_out.read_text()
    first_agent = agent_out.read_text()

    build_cmd.run(argparse.Namespace())

    assert skill_out.read_text() == first_skill
    assert agent_out.read_text() == first_agent


def test_build_missing_files_dir_exits_2(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    plugin = tmp_path / "plugin"
    (plugin / "bin").mkdir(parents=True)
    (plugin / "bin" / "booping").write_text("#!/bin/sh\n")
    (plugin / "src").mkdir()
    (plugin / "src" / "config_files.yaml").write_text("skills: {}\nagents: {}\n")
    monkeypatch.setattr(rendering, "_plugin_root", plugin)

    with pytest.raises(SystemExit) as excinfo:
        build_cmd.run(argparse.Namespace())

    assert excinfo.value.code == 2
    captured = capsys.readouterr()
    assert "missing" in captured.err
