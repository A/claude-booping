from __future__ import annotations

from pathlib import Path

from booping import migrations


def _plugin_root(tmp_path: Path, *ids: object) -> Path:
    root = tmp_path / "plugin"
    for index, value in enumerate(ids, start=1):
        directory = root / "migrations" / f"{index:03d}_thing"
        directory.mkdir(parents=True)
        (directory / "migration.md").write_text(
            f"---\nid: {value}\ntitle: Thing {index}\n---\n\nbody\n"
        )
    root.mkdir(parents=True, exist_ok=True)
    return root


def _vault(tmp_path: Path, marker: str | None) -> Path:
    directory = tmp_path / "repo"
    directory.mkdir(parents=True, exist_ok=True)
    if marker is not None:
        (directory / ".booping").write_text(marker)
    return directory


def test_no_migrations_shipped_yields_no_notice(tmp_path: Path) -> None:
    start = _vault(tmp_path, "project_name: x\n")
    assert migrations.render_gate(start=start, plugin_root=_plugin_root(tmp_path)) is None


def test_current_vault_yields_no_notice(tmp_path: Path) -> None:
    start = _vault(tmp_path, "project_name: x\nlatest_migration: 2\n")
    assert (
        migrations.render_gate(start=start, plugin_root=_plugin_root(tmp_path, 1, 2))
        is None
    )


def test_behind_vault_names_the_remedy_command(tmp_path: Path) -> None:
    start = _vault(tmp_path, "project_name: x\nlatest_migration: 1\n")
    notice = migrations.render_gate(start=start, plugin_root=_plugin_root(tmp_path, 1, 2))
    assert notice is not None
    assert notice.startswith("**STOP — tell the user:**")
    assert "/playbook migrate" in notice
    assert "recorded id 1" in notice
    assert "latest shipped 2" in notice
    assert notice.count("\n") == 0


def test_marker_read_tolerates_unknown_keys(tmp_path: Path) -> None:
    """A migration may change the marker's schema; the gate still has to work."""
    start = _vault(
        tmp_path,
        "project_name: x\nlatest_migration: 2\nfuture_key: {nested: [1, 2]}\n",
    )
    assert (
        migrations.render_gate(start=start, plugin_root=_plugin_root(tmp_path, 1, 2))
        is None
    )


def test_non_integer_watermark_counts_as_behind(tmp_path: Path) -> None:
    start = _vault(tmp_path, "project_name: x\nlatest_migration: oops\n")
    notice = migrations.render_gate(start=start, plugin_root=_plugin_root(tmp_path, 1))
    assert notice is not None
    assert "recorded id -1" in notice


def test_unparseable_marker_counts_as_behind(tmp_path: Path) -> None:
    start = _vault(tmp_path, "project_name: [unclosed\n")
    notice = migrations.render_gate(start=start, plugin_root=_plugin_root(tmp_path, 1))
    assert notice is not None
    assert "recorded id -1" in notice


def test_no_marker_anywhere_yields_no_notice(tmp_path: Path) -> None:
    start = _vault(tmp_path, None)
    assert migrations.render_gate(start=start, plugin_root=_plugin_root(tmp_path, 1)) is None


def test_highest_id_comes_from_frontmatter_not_the_directory_prefix(
    tmp_path: Path,
) -> None:
    root = _plugin_root(tmp_path, 5, 3)
    assert migrations.latest_shipped_id(root) == 5


def test_migrate_playbook_is_exempt(tmp_path: Path) -> None:
    start = _vault(tmp_path, "project_name: x\n")
    root = _plugin_root(tmp_path, 1)
    assert migrations.render_gate("groom", start=start, plugin_root=root) is not None
    assert migrations.render_gate("migrate", start=start, plugin_root=root) is None
