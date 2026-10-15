from __future__ import annotations

import datetime
import re
from functools import cache
from typing import Any, cast

from booping.context import config as config_mod
from booping.rendering import get_plugin_root
from booping.utils import deep_merge

_FALLBACK = "en"
_ISO_DATE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")


@cache
def _shipped() -> dict[str, Any]:
    core = config_mod.load(get_plugin_root(), [])
    return cast(dict[str, Any], core["core"]["specs"]["site"]["labels"])


def _get(table: Any, *keys: str) -> Any:
    for key in keys:
        if not isinstance(table, dict):
            return None
        table = cast(dict[str, Any], table).get(key)
    return table


class Labels:
    """Label lookup for one language: `labels.{lang}` → `labels.en` → the raw id."""

    def __init__(self, tables: dict[str, Any], lang: str) -> None:
        self._chain = [tables.get(lang), tables.get(_FALLBACK)]

    def _lookup(self, *keys: str) -> Any:
        for table in self._chain:
            value = _get(table, *keys)
            if value is not None:
                return value
        return None

    def _text(self, default: str, *keys: str) -> str:
        value = self._lookup(*keys)
        return default if value is None else str(value)

    def ui(self, id: str, **fmt: Any) -> str:
        text = self._text(id, "ui", id)
        return text.format(**fmt) if fmt else text

    def plural(self, id: str, n: int) -> str:
        forms = self._lookup("ui", id)
        if not isinstance(forms, list) or not forms:
            return self.ui(id, n=n)
        forms = [str(f) for f in cast(list[Any], forms)]
        if len(forms) >= 3:
            if n % 10 == 1 and n % 100 != 11:
                index = 0
            elif 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
                index = 1
            else:
                index = 2
        else:
            index = 0 if n == 1 else len(forms) - 1
        return forms[index].format(n=n)

    def type_name(self, type_: str) -> str:
        return self._text(type_, "types", type_, "name")

    def type_plural(self, type_: str) -> str:
        return self._text(type_, "types", type_, "plural")

    def scenario(self, type_: str) -> str:
        return self._text("", "types", type_, "scenario")

    def status(self, status: str) -> str:
        return self._text(status, "statuses", status)

    def fact(self, key: str) -> str:
        return self._text(key, "facts", key)

    def author(self, value: str) -> str:
        return self._text(value, "authors", value)

    def date(self, value: Any) -> str:
        if isinstance(value, datetime.date):
            year, month, day = value.year, value.month, value.day
        else:
            match = _ISO_DATE.fullmatch(str(value))
            if match is None:
                return str(value)
            year, month, day = (int(g) for g in match.groups())
            if not 1 <= month <= 12:
                return str(value)
        months = self._lookup("months")
        if not isinstance(months, list) or len(cast(list[Any], months)) != 12:
            return f"{year:04d}-{month:02d}-{day:02d}"
        return f"{day} {cast(list[Any], months)[month - 1]} {year}"


def load_labels(config_site: dict[str, Any]) -> tuple[Labels, str, list[str]]:
    """Labels, lang and warnings from a `core.specs.site` mapping; the shipped tables
    sit under it, so an empty mapping gives English."""
    lang = str(config_site.get("lang") or _FALLBACK)
    own = config_site.get("labels")
    tables = deep_merge(_shipped(), cast(dict[str, Any], own) if isinstance(own, dict) else {})
    warnings: list[str] = []
    if lang not in tables:
        warnings.append(f"core.specs.site.lang `{lang}` has no labels; using {_FALLBACK}")
    return Labels(tables, lang), lang, warnings
