from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from booping.commands.render_cli_agent import render_cli_agent
from booping.context import Context
from tests.helpers import get_fixture_path


def _assemble_fixture_ctx() -> Context:
    plugin_root = Path(__file__).resolve().parents[3]
    vault = get_fixture_path("vault-with-cli-agent")
    return Context.assemble(start=vault, plugin_root=plugin_root, vault_override=vault)


def _plugin_root() -> Path:
    return Path(__file__).resolve().parents[3]


def test_renders_cli_agent_body() -> None:
    ctx = _assemble_fixture_ctx()
    body = render_cli_agent(ctx, "pi-mesh", _plugin_root())
    assert "name: cli_agent_pi-mesh" in body
    # id baked into the run-agent call
    assert "booping run-agent pi-mesh --briefing-file" in body
    # frontmatter fields
    assert "model: opus" in body
    assert "effort: low" in body
    assert "tools: Read, Bash, Bash(booping:*)" in body
    # no jinja placeholder leaks
    assert "{{" not in body and "}}" not in body


def test_description_from_good_for() -> None:
    ctx = _assemble_fixture_ctx()
    body = render_cli_agent(ctx, "pi-mesh", _plugin_root())
    assert "Concrete code change" in body


def test_unknown_id_exits_2() -> None:
    ctx = _assemble_fixture_ctx()
    with pytest.raises(SystemExit) as ei:
        render_cli_agent(ctx, "no-such-agent", _plugin_root())
    assert ei.value.code == 2


def test_non_cli_id_exits_2() -> None:
    ctx = _assemble_fixture_ctx()
    # test-no-type defaults to type: agent
    with pytest.raises(SystemExit) as ei:
        render_cli_agent(ctx, "test-no-type", _plugin_root())
    assert ei.value.code == 2


def test_internal_native_agent_exits_2() -> None:
    """Internal native agents have no type: cli, so they have no wrapper."""
    plugin_root = _plugin_root()
    vault = get_fixture_path("vault-minimal")
    ctx = Context.assemble(start=vault, plugin_root=plugin_root, vault_override=vault)
    with pytest.raises(SystemExit) as ei:
        render_cli_agent(ctx, "booping-developer", plugin_root)
    assert ei.value.code == 2


def test_render_cli_agent_help_lists_subcommand() -> None:
    booping_bin = _plugin_root() / "bin" / "booping"
    result = subprocess.run(
        [str(booping_bin), "render-cli-agent", "--help"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "render-cli-agent" in result.stdout or "id" in result.stdout
