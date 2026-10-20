from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any

import pytest

from booping.context import config as config_mod
from booping.rendering import get_plugin_root
from booping.specs.site.labels import Labels, load_labels


def _site_config(tmp_path: Path, project_yaml: str) -> dict[str, Any]:
    project = tmp_path / "config.yaml"
    project.write_text(project_yaml)
    merged = config_mod.load(get_plugin_root(), [project])
    return merged["core"]["specs"]["site"]


def _labels(tmp_path: Path, project_yaml: str) -> tuple[Labels, str, list[str]]:
    return load_labels(_site_config(tmp_path, project_yaml))


def test_ru_type_plural(tmp_path: Path) -> None:
    labels, lang, warnings = _labels(tmp_path, "core: {specs: {site: {lang: ru}}}\n")
    assert (labels.type_plural("adr"), lang, warnings) == ("Решения", "ru", [])


def test_key_missing_in_ru_falls_back_to_en(tmp_path: Path) -> None:
    labels, _, _ = _labels(
        tmp_path,
        "core: {specs: {site: {lang: ru, labels: {en: {ui: {extra: Extra}}}}}}\n",
    )
    assert labels.ui("extra") == "Extra"
    assert labels.ui("overview") == "Обзор"


def test_unknown_lang_uses_en_and_warns_once(tmp_path: Path) -> None:
    labels, lang, warnings = _labels(tmp_path, "core: {specs: {site: {lang: de}}}\n")
    assert labels.type_plural("adr") == "ADRs"
    assert lang == "de"
    assert len(warnings) == 1
    assert "de" in warnings[0]


def test_unknown_type_renders_its_id(tmp_path: Path) -> None:
    labels, _, _ = _labels(tmp_path, "core: {specs: {site: {lang: ru}}}\n")
    assert labels.type_name("mechanic") == "mechanic"
    assert labels.type_plural("mechanic") == "mechanic"
    assert labels.scenario("mechanic") == ""


def test_project_tier_labels_its_own_type(tmp_path: Path) -> None:
    labels, _, _ = _labels(
        tmp_path,
        "core:\n  specs:\n    site:\n      lang: ru\n      labels:\n        ru:\n"
        "          types:\n            mechanic: {name: Механика, plural: Механики,"
        " scenario: Как устроен мир игры}\n",
    )
    assert labels.type_plural("mechanic") == "Механики"
    assert labels.scenario("mechanic") == "Как устроен мир игры"
    assert labels.type_plural("rule") == "Правила"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2026-10-15", "15 октября 2026"),
        (datetime.date(2026, 1, 3), "3 января 2026"),
        ("someday", "someday"),
    ],
)
def test_ru_dates(tmp_path: Path, value: object, expected: str) -> None:
    labels, _, _ = _labels(tmp_path, "core: {specs: {site: {lang: ru}}}\n")
    assert labels.date(value) == expected


def test_en_date() -> None:
    labels, _, _ = load_labels({})
    assert labels.date("2026-10-15") == "15 October 2026"


@pytest.mark.parametrize(
    ("n", "expected"),
    [
        (1, "1 вопрос к тебе"),
        (3, "3 вопроса к тебе"),
        (5, "5 вопросов к тебе"),
        (11, "11 вопросов к тебе"),
        (21, "21 вопрос к тебе"),
        (22, "22 вопроса к тебе"),
    ],
)
def test_ru_plural(tmp_path: Path, n: int, expected: str) -> None:
    labels, _, _ = _labels(tmp_path, "core: {specs: {site: {lang: ru}}}\n")
    assert labels.plural("clarify", n) == expected


def test_en_plural() -> None:
    labels, _, _ = load_labels({})
    assert [labels.plural("clarify", n) for n in (1, 2)] == [
        "1 question for you",
        "2 questions for you",
    ]


def test_empty_config_is_english() -> None:
    labels, lang, warnings = load_labels({})
    assert (labels.ui("overview"), labels.status("accepted"), lang, warnings) == (
        "Overview",
        "accepted",
        "en",
        [],
    )
