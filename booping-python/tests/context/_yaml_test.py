from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from booping.context._yaml import (
    UnclosedFrontmatterError,
    split_frontmatter,
    split_frontmatter_md,
    update_frontmatter,
    update_marker,
)

# ── split_frontmatter ───────────────────────────────────────────────────


class TestSplitFrontmatter:
    @pytest.mark.parametrize(
        ("text", "yaml_text", "body"),
        [
            pytest.param(
                "---\ntitle: Foo\n---\n\n# Body\n", "title: Foo\n", "# Body\n", id="plain"
            ),
            pytest.param(
                "---\ntitle: a --- b\nstatus: done\n---\nbody\n",
                "title: a --- b\nstatus: done\n",
                "body\n",
                id="dashes-inside-a-value",
            ),
            pytest.param(
                "---\nnotes: |\n  one\n  ---\n  two\nstatus: done\n---\nbody\n",
                "notes: |\n  one\n  ---\n  two\nstatus: done\n",
                "body\n",
                id="dashes-inside-a-block-scalar",
            ),
            pytest.param(
                "---\r\ntitle: Foo\r\n---\r\nbody\r\n",
                "title: Foo\r\n",
                "body\r\n",
                id="crlf",
            ),
            pytest.param(
                "---  \ntitle: Foo\n--- \nbody\n", "title: Foo\n", "body\n", id="trailing-spaces"
            ),
            pytest.param("---\ntitle: Foo\n---", "title: Foo\n", "", id="closing-line-at-eof"),
            pytest.param(
                "# Title\n\n---\nbody\n", None, "# Title\n\n---\nbody\n", id="no-frontmatter"
            ),
        ],
    )
    def test_splits_at_the_first_bare_delimiter_line(
        self, text: str, yaml_text: str | None, body: str
    ) -> None:
        assert split_frontmatter(text) == (yaml_text, body)

    @pytest.mark.parametrize(
        "text",
        [
            pytest.param("---\ntitle: Foo\n\nbody\n", id="never-closed"),
            pytest.param("---\ntitle: a --- b\n", id="only-dashes-inside-a-value"),
            pytest.param("---\nnotes: |\n  ---\n", id="only-an-indented-dash-line"),
        ],
    )
    def test_unclosed_block_is_a_value_error(self, text: str) -> None:
        with pytest.raises(ValueError, match="frontmatter block is not closed"):
            split_frontmatter(text)

    def test_unclosed_error_is_its_own_type(self) -> None:
        with pytest.raises(UnclosedFrontmatterError):
            split_frontmatter("---\ntitle: Foo\n")


# ── split_frontmatter_md ────────────────────────────────────────────────


class TestSplitFrontmatterMd:
    def test_splits_standard_frontmatter(self) -> None:
        text = "---\ntitle: Foo\nstatus: backlog\n---\n# Body\n"
        before, yaml_text, after = split_frontmatter_md(text)
        assert before == "---\n"
        assert yaml_text == "title: Foo\nstatus: backlog\n"
        assert after == "---\n# Body\n"

    def test_reconstructs_identical(self) -> None:
        text = "---\ntitle: Foo\n---\nbody\n"
        before, yaml_text, after = split_frontmatter_md(text)
        assert before + yaml_text + after == text

    def test_empty_frontmatter(self) -> None:
        text = "---\n---\nbody\n"
        before, yaml_text, after = split_frontmatter_md(text)
        assert before == "---\n"
        assert yaml_text == ""
        assert after == "---\nbody\n"
        assert before + yaml_text + after == text

    def test_raises_on_missing_opening_delimiter(self) -> None:
        with pytest.raises(ValueError, match="opening"):
            split_frontmatter_md("no frontmatter\n")

    def test_raises_on_missing_closing_delimiter(self) -> None:
        with pytest.raises(ValueError, match="not closed"):
            split_frontmatter_md("---\ntitle: Foo\n")

    def test_raises_on_opening_without_newline(self) -> None:
        with pytest.raises(ValueError):
            split_frontmatter_md("---title: Foo\n---\nbody\n")

    def test_dashes_inside_a_value_stay_in_the_yaml(self) -> None:
        text = "---\ntitle: a --- b\nstatus: done\n---\nbody\n"
        _, yaml_text, after = split_frontmatter_md(text)
        assert yaml_text == "title: a --- b\nstatus: done\n"
        assert after == "---\nbody\n"

    def test_crlf_reconstructs_identical(self) -> None:
        text = "---\r\ntitle: Foo\r\n---\r\nbody\r\n"
        before, yaml_text, after = split_frontmatter_md(text)
        assert (before, yaml_text) == ("---\r\n", "title: Foo\r\n")
        assert before + yaml_text + after == text


# ── update_frontmatter ───────────────────────────────────────────────────


class TestUpdateFrontmatter:
    def test_keys_after_a_dashed_value_survive_an_update(self, tmp_path: Path) -> None:
        f = tmp_path / "plan.md"
        f.write_text("---\ntitle: a --- b\nstatus: draft\n---\nbody\n")
        update_frontmatter(f, {"status": "done"})
        assert f.read_text() == "---\ntitle: a --- b\nstatus: done\n---\nbody\n"

    def test_round_trip_no_changes(self, tmp_path: Path) -> None:
        """Round-trip with no key changes leaves the whole file byte-identical."""
        md = (
            "---\n"
            "title: Add search feature\n"
            "type: feature\n"
            "status: in-progress\n"
            "sp: 5\n"
            'planned: "20260101 09:00"\n'
            "split_from: null\n"
            "commit: 0123456789abcdef0123456789abcdef01234567\n"
            "---\n"
            "# Add search feature\n\n"
            "## Tasks\n\n"
            "- [ ] 3 SP: Integrate search index library\n"
        )
        plan = tmp_path / "plan.md"
        plan.write_text(md)

        update_frontmatter(plan, {})

        assert plan.read_text() == md

    def test_updates_key_preserves_others(self, tmp_path: Path) -> None:
        md = "---\ntitle: Foo\nstatus: backlog\nsp: 3\n---\n# Body\n"
        plan = tmp_path / "plan.md"
        plan.write_text(md)

        update_frontmatter(plan, {"status": "in-progress", "sp": 5})

        text = plan.read_text()
        assert "status: in-progress" in text
        assert "sp: 5" in text
        assert "title: Foo" in text
        assert "# Body" in text

    def test_preserves_null_values(self, tmp_path: Path) -> None:
        md = "---\nsplit_from: null\ncompleted: null\n---\nbody\n"
        plan = tmp_path / "plan.md"
        plan.write_text(md)

        update_frontmatter(plan, {"status": "in-progress"})

        text = plan.read_text()
        assert "split_from: null" in text
        assert "completed: null" in text

    def test_preserves_comments(self, tmp_path: Path) -> None:
        md = "---\ntitle: Foo  # important\n# section\nstatus: backlog\n---\nbody\n"
        plan = tmp_path / "plan.md"
        plan.write_text(md)

        update_frontmatter(plan, {"status": "in-progress"})

        text = plan.read_text()
        assert "# important" in text
        assert "# section" in text

    def test_preserves_key_order(self, tmp_path: Path) -> None:
        md = "---\nalpha: 1\nbeta: 2\ngamma: 3\n---\nbody\n"
        plan = tmp_path / "plan.md"
        plan.write_text(md)

        update_frontmatter(plan, {"beta": 99})

        text = plan.read_text()
        # alpha should still come before gamma
        assert text.index("alpha") < text.index("gamma")

    def test_body_byte_identical(self, tmp_path: Path) -> None:
        """Body after the closing --- is concatenated back byte-identical."""
        body = "# Heading\n\n- item 1\n- item 2\n"
        md = f"---\ntitle: Foo\n---\n{body}"
        plan = tmp_path / "plan.md"
        plan.write_text(md)

        update_frontmatter(plan, {"status": "in-progress"})

        # Extract body from result
        result = plan.read_text()
        assert result.endswith(body)

    def test_body_with_yaml_like_content_not_parsed(self, tmp_path: Path) -> None:
        """Whole .md is never passed to the YAML parser (only the extracted block).

        The body may contain text that would break YAML parsing; it must survive
        untouched.
        """
        body = "---\nthis: is yaml-like\nbut: should not be parsed\n"
        md = f"---\ntitle: Foo\n---\n{body}"
        plan = tmp_path / "plan.md"
        plan.write_text(md)

        update_frontmatter(plan, {"status": "in-progress"})

        result = plan.read_text()
        assert result.endswith(body)

    def test_adds_new_key(self, tmp_path: Path) -> None:
        md = "---\ntitle: Foo\nstatus: backlog\n---\nbody\n"
        plan = tmp_path / "plan.md"
        plan.write_text(md)

        update_frontmatter(plan, {"commit": "abc123"})

        text = plan.read_text()
        assert "commit: abc123" in text
        assert "title: Foo" in text

    def test_bootstraps_missing_frontmatter(self, tmp_path: Path) -> None:
        plan = tmp_path / "plan.md"
        plan.write_text("# Heading\n\nbody text\n")

        update_frontmatter(plan, {"status": "in-progress"})

        text = plan.read_text()
        assert text == "---\nstatus: in-progress\n---\n\n# Heading\n\nbody text\n"

    def test_bootstraps_frontmatter_on_empty_file(self, tmp_path: Path) -> None:
        plan = tmp_path / "plan.md"
        plan.write_text("")

        update_frontmatter(plan, {"status": "in-progress"})

        assert plan.read_text() == "---\nstatus: in-progress\n---\n"

    def test_removes_key_preserves_others_comments_order_body(self, tmp_path: Path) -> None:
        body = "# Body\n\n- item 1\n- item 2\n"
        md = (
            "---\n"
            "title: Foo  # important\n"
            "business_goal: Users can find widgets faster.\n"
            "status: backlog\n"
            "# trailing section\n"
            "sp: 5\n"
            f"---\n{body}"
        )
        plan = tmp_path / "plan.md"
        plan.write_text(md)

        update_frontmatter(plan, {}, removals=["business_goal"])

        text = plan.read_text()
        assert "business_goal" not in text
        assert "title: Foo" in text
        assert "# important" in text
        assert "# trailing section" in text
        assert "status: backlog" in text
        assert "sp: 5" in text
        assert text.index("title") < text.index("status") < text.index("sp")
        assert text.endswith(body)

    def test_removes_missing_key_is_noop(self, tmp_path: Path) -> None:
        md = "---\ntitle: Foo\nstatus: backlog\n---\nbody\n"
        plan = tmp_path / "plan.md"
        plan.write_text(md)

        update_frontmatter(plan, {}, removals=["nonexistent"])

        assert plan.read_text() == md

    def test_remove_then_add_same_key(self, tmp_path: Path) -> None:
        md = "---\ntitle: Foo\nbusiness_goal: old\nstatus: backlog\n---\nbody\n"
        plan = tmp_path / "plan.md"
        plan.write_text(md)

        update_frontmatter(plan, {"summary": ""}, removals=["business_goal"])

        text = plan.read_text()
        assert "business_goal" not in text
        assert "summary:" in text
        assert "title: Foo" in text

    @pytest.mark.parametrize(
        ("frontmatter", "appends", "expected"),
        [
            pytest.param(
                "sessions:\n- a\n",
                [("sessions", "b"), ("sessions", "c")],
                "sessions:\n- a\n- b\n- c\n",
                id="repeated-key-keeps-every-value-in-order",
            ),
            pytest.param(
                "sessions:\n",
                [("sessions", "a"), ("sessions", "b")],
                "sessions:\n- a\n- b\n",
                id="null-key-then-repeat",
            ),
            pytest.param(
                "title: Foo\n",
                [("sessions", "a"), ("sessions", "a")],
                "title: Foo\nsessions:\n- a\n",
                id="absent-key-duplicate-value-added-once",
            ),
        ],
    )
    def test_appends_apply_each_pair(
        self, tmp_path: Path, frontmatter: str, appends: list[tuple[str, object]], expected: str
    ) -> None:
        plan = tmp_path / "plan.md"
        plan.write_text(f"---\n{frontmatter}---\nbody\n")

        update_frontmatter(plan, {}, appends=appends)

        assert plan.read_text() == f"---\n{expected}---\nbody\n"

    def test_append_onto_scalar_raises(self, tmp_path: Path) -> None:
        plan = tmp_path / "plan.md"
        plan.write_text("---\nsessions: a\n---\nbody\n")

        with pytest.raises(ValueError, match="scalar"):
            update_frontmatter(plan, {}, appends=[("sessions", "b")])


# ── update_marker ───────────────────────────────────────────────────────


LONG_VAULT = "vault_path: ../some/quite/deliberately/long/path/that/must/not/be/rewrapped/by/ruamel"

MARKER = (
    "# booping project marker\n"
    'project_name: "claude-booping"  # quoted on purpose\n'
    f"{LONG_VAULT}\n"
    "latest_migration: 2\n"
)


class TestUpdateMarker:
    def test_changes_only_the_target_line(self, tmp_path: Path) -> None:
        marker = tmp_path / ".booping"
        marker.write_text(MARKER)

        update_marker(marker, {"latest_migration": 3})

        before = MARKER.splitlines()
        after = marker.read_text().splitlines()
        assert len(before) == len(after)
        changed = [(b, a) for b, a in zip(before, after, strict=True) if b != a]
        assert changed == [("latest_migration: 2", "latest_migration: 3")]

    def test_preserves_comments_quoting_and_order(self, tmp_path: Path) -> None:
        marker = tmp_path / ".booping"
        marker.write_text(MARKER)

        update_marker(marker, {"latest_migration": 7})

        text = marker.read_text()
        assert "# booping project marker" in text
        assert '"claude-booping"' in text
        assert "# quoted on purpose" in text
        assert text.index("project_name") < text.index("vault_path")
        assert text.index("vault_path") < text.index("latest_migration")

    def test_long_line_is_not_rewrapped(self, tmp_path: Path) -> None:
        marker = tmp_path / ".booping"
        marker.write_text(MARKER)

        update_marker(marker, {"latest_migration": 3})

        assert LONG_VAULT in marker.read_text()

    def test_adds_missing_key(self, tmp_path: Path) -> None:
        marker = tmp_path / ".booping"
        marker.write_text("project_name: demo\n")

        update_marker(marker, {"latest_migration": 0})

        assert marker.read_text() == "project_name: demo\nlatest_migration: 0\n"

    def test_stays_a_single_yaml_document(self, tmp_path: Path) -> None:
        marker = tmp_path / ".booping"
        marker.write_text(MARKER)

        update_marker(marker, {"latest_migration": 3})

        text = marker.read_text()
        assert "---" not in text
        assert len(list(yaml.safe_load_all(text))) == 1
        assert yaml.safe_load(text)["latest_migration"] == 3

    def test_rejects_non_mapping(self, tmp_path: Path) -> None:
        marker = tmp_path / ".booping"
        marker.write_text("- one\n- two\n")

        with pytest.raises(ValueError, match="not a YAML mapping"):
            update_marker(marker, {"latest_migration": 1})
