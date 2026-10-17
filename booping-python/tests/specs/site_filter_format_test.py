from __future__ import annotations

import json
import shutil
import subprocess
from importlib.resources import files
from typing import Any

import pytest

_RUNNER = """
const fs = require("fs");
const vm = require("vm");
const input = JSON.parse(fs.readFileSync(0, "utf8"));
const ctx = {};
vm.runInNewContext(input.source, ctx);
process.stdout.write(JSON.stringify(ctx.SpecsFilters[input.fn](...input.args)));
"""


def _call(fn: str, *args: Any) -> Any:
    node = shutil.which("node")
    if node is None:
        pytest.fail("node is not on PATH: the filter format tests run filter-format.js under node")
    source = files("booping.specs.site").joinpath("filter-format.js").read_text()
    stdin = json.dumps({"source": source, "fn": fn, "args": list(args)})
    done = subprocess.run(
        [node, "-e", _RUNNER], input=stdin, capture_output=True, text=True, check=True
    )
    return json.loads(done.stdout)


def test_row_without_pressed_chips_names_only_the_sort() -> None:
    assert _call("row", "Filters", 0, "Review order") == "Filters · Review order"


def test_row_counts_pressed_chips() -> None:
    assert _call("row", "Filters", 2, "By title") == "Filters (2) · By title"


def test_row_in_russian() -> None:
    assert _call("row", "Фильтры", 1, "Для ревью") == "Фильтры (1) · Для ревью"


def test_removable_keeps_order_and_fills_the_label() -> None:
    pressed = [
        {"key": "source", "value": "claude", "label": "Claude"},
        {"key": "flag", "value": "unreviewed", "label": "Unreviewed"},
    ]
    assert _call("removable", pressed, "Remove filter: {label}") == [
        {
            "key": "source",
            "value": "claude",
            "text": "Claude",
            "aria": "Remove filter: Claude",
        },
        {
            "key": "flag",
            "value": "unreviewed",
            "text": "Unreviewed",
            "aria": "Remove filter: Unreviewed",
        },
    ]


def test_removable_in_russian() -> None:
    pressed = [{"key": "status", "value": "draft", "label": "Черновик"}]
    assert _call("removable", pressed, "Убрать фильтр: {label}") == [
        {
            "key": "status",
            "value": "draft",
            "text": "Черновик",
            "aria": "Убрать фильтр: Черновик",
        }
    ]


def test_removable_with_nothing_pressed_is_empty() -> None:
    assert _call("removable", [], "Remove filter: {label}") == []
