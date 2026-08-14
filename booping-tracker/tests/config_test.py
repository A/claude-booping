from __future__ import annotations

from pathlib import Path

import pytest

from booping_tracker import config as config_mod
from booping_tracker.config import ConfigError, load

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def unreachable_booping(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Point the config-get shell-out at nothing, so any use of it is observable."""
    monkeypatch.setattr(config_mod, "BOOPING", tmp_path / "no-such-booping")


def _write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "tracker.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def test_config_file_is_read_without_shelling_out(
    tmp_path: Path, unreachable_booping: None
) -> None:
    config = load(config_file=_write(tmp_path, "driver: cli\n"))

    assert config.driver == "cli"


def test_config_get_resolves_the_shipped_tracker_block() -> None:
    config = load(cwd=REPO_ROOT)

    assert config.driver == "cli"
    assert config.settings["linear"]["api_url"] == "https://api.linear.app/graphql"


def test_missing_config_file_is_an_error(tmp_path: Path, unreachable_booping: None) -> None:
    with pytest.raises(ConfigError, match="could not read config file"):
        load(config_file=tmp_path / "absent.yaml")


def test_unresolvable_config_get_is_an_error(unreachable_booping: None) -> None:
    with pytest.raises(ConfigError, match="could not run"):
        load()


@pytest.mark.parametrize(
    ("body", "override", "expected"),
    [
        ("driver: jira\n", None, "unknown driver: jira"),
        ("driver: cli\n", "linaer", "unknown driver: linaer"),
        ("linear:\n  api_key_env: TOKEN\n", None, "no tracker driver configured"),
        ("[]\n", None, "tracker config is not a mapping"),
    ],
)
def test_rejected_drivers_and_shapes(
    tmp_path: Path,
    unreachable_booping: None,
    body: str,
    override: str | None,
    expected: str,
) -> None:
    with pytest.raises(ConfigError, match=expected):
        load(config_file=_write(tmp_path, body), driver_override=override)


def test_driver_override_wins_over_the_configured_driver(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, unreachable_booping: None
) -> None:
    monkeypatch.setenv("LINEAR_API_KEY", "lin_api_x")
    config = load(
        config_file=_write(tmp_path, "driver: cli\nlinear:\n  api_key_env: LINEAR_API_KEY\n"),
        driver_override="linear",
    )

    assert config.driver == "linear"


def test_unset_api_key_variable_is_an_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, unreachable_booping: None
) -> None:
    monkeypatch.delenv("LINEAR_API_KEY", raising=False)
    path = _write(tmp_path, "driver: linear\nlinear:\n  api_key_env: LINEAR_API_KEY\n")

    with pytest.raises(ConfigError, match="LINEAR_API_KEY is unset"):
        load(config_file=path)


def test_api_key_is_only_required_by_the_driver_that_needs_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, unreachable_booping: None
) -> None:
    monkeypatch.delenv("LINEAR_API_KEY", raising=False)
    path = _write(tmp_path, "driver: cli\nlinear:\n  api_key_env: LINEAR_API_KEY\n")

    assert load(config_file=path).driver == "cli"


def test_driver_settings_expose_the_selected_driver_block(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, unreachable_booping: None
) -> None:
    monkeypatch.setenv("LINEAR_API_KEY", "lin_api_x")
    path = _write(tmp_path, "driver: linear\nlinear:\n  api_key_env: LINEAR_API_KEY\n  team: ENG\n")

    assert load(config_file=path).driver_settings()["team"] == "ENG"
