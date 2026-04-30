from __future__ import annotations

from booping.context.agent import Agent
from tests.helpers import get_fixture_path


def test_load_all_count() -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    agents = Agent.load_all(plugin_root)
    assert len(agents) == 1


def test_load_all_fields() -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    agents = Agent.load_all(plugin_root)
    agent = agents["sample-agent"]
    assert agent.name == "sample-agent"
    assert agent.description == "A sample agent for testing"
    assert agent.effort == "medium"
    assert agent.model == "claude-sonnet-4-5"
    assert agent.allowed_tools == ["Bash(git:*)"]
    assert agent.color == "blue"
