from __future__ import annotations

from pathlib import Path

import pytest

from booping.commands.compile import cli_agent_ids, compile_wrappers
from booping.context import Context
from tests.helpers import get_fixture_path


def _plugin_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _ctx_with_repo(repo: Path) -> Context:
    plugin_root = _plugin_root()
    vault = get_fixture_path("vault-with-cli-agent")
    ctx = Context.assemble(start=vault, plugin_root=plugin_root, vault_override=vault)
    assert ctx.project is not None
    ctx.project.repo_directory = repo
    ctx.project.directory = vault
    return ctx


def _agents_dir(repo: Path) -> Path:
    return repo / ".claude" / "agents"


def test_cli_agent_ids_dedupes_and_sorts() -> None:
    cfg = {
        "skills": {
            "a": {
                "agents": {
                    "x": {"type": "cli", "command": "c"},
                    "n": {"type": "agent"},
                }
            },
            "b": {
                "agents": {
                    "x": {"type": "cli", "command": "c"},
                    "y": {"type": "cli", "command": "c"},
                }
            },
        }
    }
    assert cli_agent_ids(cfg) == ["x", "y"]


def test_creates_agents_dir_when_missing(tmp_path: Path) -> None:
    ctx = _ctx_with_repo(tmp_path)
    compile_wrappers(ctx, _plugin_root())
    assert _agents_dir(tmp_path).is_dir()


def test_writes_wrapper_for_each_cli_id(tmp_path: Path) -> None:
    ctx = _ctx_with_repo(tmp_path)
    compile_wrappers(ctx, _plugin_root())
    # fixture has two cli agents with no command-template issues: pi-mesh, test-cli,
    # test-cli-with-placeholder, test-cli-fail are all type: cli.
    files = {p.name for p in _agents_dir(tmp_path).glob("cli_agent_*.md")}
    assert "cli_agent_pi-mesh.md" in files
    body = (_agents_dir(tmp_path) / "cli_agent_pi-mesh.md").read_text()
    assert "name: cli_agent_pi-mesh" in body


def test_prune_removes_ids_no_longer_configured(tmp_path: Path) -> None:
    ctx = _ctx_with_repo(tmp_path)
    compile_wrappers(ctx, _plugin_root())
    # drop pi-mesh from config and recompile
    del ctx.config["skills"]["develop"]["agents"]["pi-mesh"]
    diff = compile_wrappers(ctx, _plugin_root())
    assert not (_agents_dir(tmp_path) / "cli_agent_pi-mesh.md").exists()
    assert any("removed cli_agent_pi-mesh.md" == line for line in diff)


def test_idempotent_rerun_reproduces_identical_files(tmp_path: Path) -> None:
    ctx = _ctx_with_repo(tmp_path)
    compile_wrappers(ctx, _plugin_root())
    first = {
        p.name: p.read_text() for p in _agents_dir(tmp_path).glob("cli_agent_*.md")
    }
    diff = compile_wrappers(ctx, _plugin_root())
    second = {
        p.name: p.read_text() for p in _agents_dir(tmp_path).glob("cli_agent_*.md")
    }
    assert first == second
    assert all(line.startswith("unchanged ") for line in diff)


def test_no_cli_agents_no_op(tmp_path: Path) -> None:
    ctx = _ctx_with_repo(tmp_path)
    ctx.config["skills"]["develop"]["agents"] = {}
    diff = compile_wrappers(ctx, _plugin_root())
    assert diff == []
    assert list(_agents_dir(tmp_path).glob("cli_agent_*.md")) == []


def test_non_prefixed_agents_untouched(tmp_path: Path) -> None:
    ctx = _ctx_with_repo(tmp_path)
    agents = _agents_dir(tmp_path)
    agents.mkdir(parents=True)
    hand = agents / "my-custom-agent.md"
    hand.write_text("hand-authored")
    compile_wrappers(ctx, _plugin_root())
    assert hand.read_text() == "hand-authored"


def test_absent_project_exits_2(tmp_path: Path) -> None:
    plugin_root = _plugin_root()
    # assemble from a dir with no .booping marker → project None
    ctx = Context.assemble(start=tmp_path, plugin_root=plugin_root)
    ctx.project = None
    with pytest.raises(SystemExit) as ei:
        compile_wrappers(ctx, plugin_root)
    assert ei.value.code == 2
