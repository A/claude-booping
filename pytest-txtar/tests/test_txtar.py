from __future__ import annotations

import pytest

from pytest_txtar import txtar

ARCHIVE = """intro line
second intro line
-- cmd --
tool run
-- fixtures/cwd/note.md --
body
-- stdout --
done
"""


def test_parses_leading_text_as_the_comment():
    archive = txtar.parse(ARCHIVE)

    assert archive.comment == "intro line\nsecond intro line\n"


def test_parses_sections_in_file_order():
    archive = txtar.parse(ARCHIVE)

    assert archive.files == [
        ("cmd", "tool run\n"),
        ("fixtures/cwd/note.md", "body\n"),
        ("stdout", "done\n"),
    ]


def test_serializes_back_to_the_original_text():
    assert txtar.serialize(txtar.parse(ARCHIVE)) == ARCHIVE


def test_empty_text_parses_to_an_empty_archive():
    archive = txtar.parse("")

    assert archive.comment == ""
    assert archive.files == []
    assert txtar.serialize(archive) == ""


def test_archive_without_a_comment_serializes_without_a_leading_blank_line():
    text = "-- cmd --\ntool run\n"

    assert txtar.serialize(txtar.parse(text)) == text


def test_section_missing_its_trailing_newline_gains_one():
    archive = txtar.parse("-- stdout --\nno newline here")

    assert archive.files == [("stdout", "no newline here\n")]
    assert txtar.serialize(archive) == "-- stdout --\nno newline here\n"


def test_comment_missing_its_trailing_newline_gains_one():
    archive = txtar.parse("dangling comment")

    assert archive.comment == "dangling comment\n"


def test_marker_name_is_stripped_of_surrounding_whitespace():
    archive = txtar.parse("--   cmd   --\ntool run\n")

    assert archive.files == [("cmd", "tool run\n")]


def test_empty_marker_name_is_content_not_a_section():
    archive = txtar.parse("--  --\n")

    assert archive.comment == "--  --\n"
    assert archive.files == []


@pytest.mark.parametrize("separator", ["\f", "\x1c", " "])
def test_non_newline_line_separators_stay_inside_a_section(separator: str):
    text = f"-- stdout --\nbefore{separator}after\n"

    assert txtar.parse(text).files == [("stdout", f"before{separator}after\n")]


def test_a_repeated_section_name_is_rejected():
    with pytest.raises(ValueError, match="duplicate section: cmd"):
        txtar.parse("-- cmd --\none\n-- cmd --\ntwo\n")
