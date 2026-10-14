from __future__ import annotations

import pytest

from booping.specs.links import relative_links


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        pytest.param("See [a](../value/0001-a.md).", [(1, "../value/0001-a.md")], id="plain"),
        pytest.param("[a](notes.md#why)", [(1, "notes.md")], id="anchor-stripped"),
        pytest.param("[a](<my notes.md>)", [(1, "my notes.md")], id="angle-wrapper"),
        pytest.param('[a](notes.md "Title")', [(1, "notes.md")], id="title"),
        pytest.param("[a](https://example.com/x.md)", [], id="url"),
        pytest.param("[mail](mailto:me@example.com)", [], id="mailto"),
        pytest.param("[a](/etc/hosts)", [], id="absolute"),
        pytest.param("[a](#section)", [], id="anchor-only"),
        pytest.param("```\n[a](inside.md)\n```\n[b](after.md)", [(4, "after.md")], id="fenced"),
        pytest.param("~~~md\n[a](inside.md)\n```\n~~~\n", [], id="fence-closes-on-its-own-marker"),
        pytest.param("Use `[a](code.md)` then [b](real.md)", [(1, "real.md")], id="inline-code"),
        pytest.param(
            "[a](one.md) and [b](two.md)", [(1, "one.md"), (1, "two.md")], id="two-on-a-line"
        ),
        pytest.param("intro\n\n[a](third.md)", [(3, "third.md")], id="line-number"),
    ],
)
def test_relative_links_keep_only_local_targets(text: str, expected: list[tuple[int, str]]) -> None:
    assert [(link.line, link.path) for link in relative_links(text)] == expected


def test_relative_links_number_from_the_body_offset() -> None:
    assert [link.line for link in relative_links("x\n[a](a.md)", first_line=10)] == [11]


def test_relative_links_keep_the_written_destination() -> None:
    assert [link.dest for link in relative_links("[a](notes.md#why)")] == ["notes.md#why"]
