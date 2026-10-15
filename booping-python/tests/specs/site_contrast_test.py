from __future__ import annotations

import re
from pathlib import Path

import pytest

from booping.specs.site import pages

CSS = (Path(pages.__file__).parent / "style.css").read_text()
TOKENS = (
    "bg surface sunk text muted faint line link link-bg ok ok-bg warn warn-bg bad bad-bg"
    " info info-bg idle idle-bg sans mono"
).split()


def _block(selector: str) -> str:
    start = CSS.index(selector + " {") + len(selector) + 2
    return CSS[start : CSS.index("}", start)]


def _tokens(block: str) -> dict[str, str]:
    return dict(re.findall(r"--([a-z-]+):\s*([^;]+);", block))


LIGHT = _tokens(_block(":root"))
DARK = _tokens(_block(':root[data-theme="dark"]'))
DARK_AUTO = _tokens(_block(':root:not([data-theme="light"])'))


def _luminance(hex_colour: str) -> float:
    channels = [int(hex_colour[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    r, g, b = (c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _contrast(a: str, b: str) -> float:
    hi, lo = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def _badge_pairs() -> list[tuple[str, str, str]]:
    """(badge class, foreground token, background token) as the stylesheet styles
    them; a badge without a background sits on the page background."""
    pairs: list[tuple[str, str, str]] = []
    for name, body in re.findall(r"^\.b(\.[a-z]+)? \{([^}]*)\}", CSS, re.MULTILINE):
        fg = re.search(r"(?<![-\w])color: var\(--([a-z-]+)\)", body)
        bg = re.search(r"background: (?:var\(--([a-z-]+)\)|none)", body)
        assert fg is not None and bg is not None, name
        pairs.append((name or ".b", fg.group(1), bg.group(1) or "bg"))
    return pairs


def test_every_token_in_both_themes() -> None:
    assert set(TOKENS) <= set(LIGHT)
    assert set(TOKENS) - {"sans", "mono"} <= set(DARK)
    assert DARK == DARK_AUTO
    assert "color-scheme: light" in _block(":root")
    assert "color-scheme: dark" in _block(':root[data-theme="dark"]')


def test_badge_classes_are_all_checked() -> None:
    assert {name for name, _, _ in _badge_pairs()} == {
        ".b",
        ".ok",
        ".warn",
        ".bad",
        ".info",
        ".idle",
        ".plain",
    }


@pytest.mark.parametrize("theme", [LIGHT, DARK], ids=["light", "dark"])
@pytest.mark.parametrize(
    ("fg", "bg"),
    [("text", "bg"), ("muted", "bg"), ("link", "bg")],
)
def test_text_contrast(theme: dict[str, str], fg: str, bg: str) -> None:
    assert _contrast(theme[fg], theme[bg]) >= 4.5


@pytest.mark.parametrize("theme", [LIGHT, DARK], ids=["light", "dark"])
@pytest.mark.parametrize(("name", "fg", "bg"), _badge_pairs())
def test_badge_contrast(theme: dict[str, str], name: str, fg: str, bg: str) -> None:
    assert _contrast(theme[fg], theme[bg]) >= 4.5, name


def test_dark_body_text_reaches_aaa() -> None:
    assert _contrast(DARK["text"], DARK["bg"]) >= 7


def test_no_system_ui_font() -> None:
    assert "system-ui" not in CSS
