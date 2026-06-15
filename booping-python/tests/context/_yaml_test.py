from __future__ import annotations

from pathlib import Path

import pytest

from booping.context._yaml import split_frontmatter_md, update_frontmatter

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
        with pytest.raises(ValueError, match="closing"):
            split_frontmatter_md("---\ntitle: Foo\n")

    def test_raises_on_opening_without_newline(self) -> None:
        with pytest.raises(ValueError, match="newline"):
            split_frontmatter_md("---title: Foo\n---\nbody\n")


# ── update_frontmatter ───────────────────────────────────────────────────


class TestUpdateFrontmatter:
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
        md = (
            "---\n"
            "title: Foo\n"
            "status: backlog\n"
            "sp: 3\n"
            "---\n"
            "# Body\n"
        )
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

    def test_raises_on_missing_frontmatter(self, tmp_path: Path) -> None:
        plan = tmp_path / "plan.md"
        plan.write_text("no frontmatter here\n")

        with pytest.raises(ValueError, match="opening"):
            update_frontmatter(plan, {"status": "in-progress"})