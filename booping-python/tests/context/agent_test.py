from booping.context.agent import Agent
from tests.helpers import get_fixture_path


def test_load_all() -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    agents = Agent.load_all(plugin_root)
    assert len(agents) == 2
    assert "booping-researcher" in agents
    assert "booping-developer" in agents

    researcher = agents["booping-researcher"]
    assert researcher.description == "Researcher agent"
    assert researcher.model == "sonnet"
    assert researcher.effort == "high"
    assert researcher.color == "green"
    assert "Read" in researcher.allowed_tools

    developer = agents["booping-developer"]
    assert developer.model == "opus"
    assert developer.color == "blue"