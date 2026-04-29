from booping.context import Context
from tests.helpers import get_fixture_path


def test_assemble_populates_all_fields() -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    vault = get_fixture_path("vault-full")
    ctx = Context.assemble(plugin_root, vault)

    assert ctx.project is not None
    assert ctx.project.name == "full-test"
    assert ctx.plans  # non-empty
    assert ctx.lessons  # non-empty
    assert ctx.retros  # non-empty
    assert ctx.plan_templates  # non-empty
    assert ctx.skills  # non-empty
    assert ctx.agents  # non-empty
    assert ctx.config  # non-empty dict
    assert ctx.extra_instructions  # non-empty dict


def test_assemble_no_vault() -> None:
    plugin_root = get_fixture_path("plugin-root-minimal")
    ctx = Context.assemble(plugin_root, vault=None)

    assert ctx.project is None
    assert ctx.plans == []
    assert ctx.lessons == []
    assert ctx.retros == []
    assert ctx.extra_instructions == {}
    assert ctx.skills  # still loaded from plugin root
    assert ctx.agents  # still loaded from plugin root
    assert ctx.config  # core config loaded