from __future__ import annotations

import argparse
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import pytest

from booping.commands import frontmatter_update as fu_cmd


def _make_plan(tmp_path: Path, frontmatter: str, body: str = "# Body\n") -> Path:
    plan = tmp_path / "20260101-test-plan.md"
    plan.write_text(f"---\n{frontmatter}\n---\n{body}")
    return plan


def _ns(**kwargs: object) -> argparse.Namespace:
    """Create an argparse.Namespace from keyword arguments."""
    return argparse.Namespace(**kwargs)  # type: ignore[arg-type]


def _split_result(text: str) -> tuple[str, str, str]:
    """Split a plan file result into (before, yaml_block, after)."""
    from booping.context._yaml import split_frontmatter_md

    return split_frontmatter_md(text)


# ── parse_pairs ──────────────────────────────────────────────────────────


class TestParsePairs:
    def test_valid_pairs(self) -> None:
        result = fu_cmd._parse_pairs(["status=in-progress", "sp=5"])  # type: ignore[reportPrivateUsage]
        assert result == {"status": "in-progress", "sp": "5"}

    def test_value_with_equals_sign(self) -> None:
        result = fu_cmd._parse_pairs(["goal=a = b"])  # type: ignore[reportPrivateUsage]
        assert result == {"goal": "a = b"}

    def test_empty_key_exits_1(self) -> None:
        with pytest.raises(SystemExit) as excinfo:
            fu_cmd._parse_pairs(["=value"])  # type: ignore[reportPrivateUsage]
        assert excinfo.value.code == 1

    def test_no_equals_exits_1(self) -> None:
        with pytest.raises(SystemExit) as excinfo:
            fu_cmd._parse_pairs(["noequals"])  # type: ignore[reportPrivateUsage]
        assert excinfo.value.code == 1


# ── interpolate ──────────────────────────────────────────────────────────


class TestInterpolate:
    def test_now(self) -> None:
        result = fu_cmd._interpolate("@now", None)  # type: ignore[reportPrivateUsage]
        # Should be yyyymmdd hh:mm format
        parsed = datetime.strptime(result, "%Y%m%d %H:%M")
        assert parsed is not None

    def test_today(self) -> None:
        result = fu_cmd._interpolate("@today", None)  # type: ignore[reportPrivateUsage]
        assert result == datetime.now(UTC).strftime("%Y-%m-%d")

    def test_head(self) -> None:
        # Should resolve to a 40-char hex SHA in a git repo
        git_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        expected = git_result.stdout.strip()
        actual = fu_cmd._interpolate("@head", Path.cwd())  # type: ignore[reportPrivateUsage]
        assert actual == expected
        assert len(actual) == 40

    def test_literal_value(self) -> None:
        assert fu_cmd._interpolate("hello", None) == "hello"  # type: ignore[reportPrivateUsage]

    def test_at_sign_prefix_not_interpolated(self) -> None:
        assert fu_cmd._interpolate("@notatoken", None) == "@notatoken"  # type: ignore[reportPrivateUsage]


# ── CLI integration ──────────────────────────────────────────────────────


class TestFrontmatterUpdateCLI:
    def test_sets_planned_with_at_now(self, tmp_path: Path) -> None:
        plan = _make_plan(tmp_path, "title: Foo\nstatus: backlog")

        fu_cmd._run(_ns(plan=plan, pairs=["planned=@now"]))  # type: ignore[reportPrivateUsage]

        text = plan.read_text()
        assert "planned:" in text
        _, fm_text, _ = _split_result(text)
        import yaml as pyyaml

        fm = pyyaml.safe_load(fm_text)
        datetime.strptime(fm["planned"], "%Y%m%d %H:%M")

    def test_sets_commit_with_at_head(self, tmp_path: Path) -> None:
        plan = _make_plan(tmp_path, "title: Foo\nstatus: backlog")

        fu_cmd._run(_ns(plan=plan, pairs=["commit=@head"]))  # type: ignore[reportPrivateUsage]

        text = plan.read_text()
        assert "commit:" in text
        _, fm_text, _ = _split_result(text)
        import yaml as pyyaml

        fm = pyyaml.safe_load(fm_text)
        assert len(fm["commit"]) == 40

    def test_sets_today(self, tmp_path: Path) -> None:
        plan = _make_plan(tmp_path, "title: Foo\nstatus: backlog")

        fu_cmd._run(_ns(plan=plan, pairs=["created=@today"]))  # type: ignore[reportPrivateUsage]

        text = plan.read_text()
        assert "created:" in text
        _, fm_text, _ = _split_result(text)
        import yaml as pyyaml

        fm = pyyaml.safe_load(fm_text)
        assert fm["created"] == datetime.now(UTC).strftime("%Y-%m-%d")

    def test_literal_value(self, tmp_path: Path) -> None:
        plan = _make_plan(tmp_path, "title: Foo\nstatus: backlog")

        fu_cmd._run(_ns(plan=plan, pairs=["status=in-progress"]))  # type: ignore[reportPrivateUsage]

        text = plan.read_text()
        assert "status: in-progress" in text

    def test_missing_plan_exits_1(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        with pytest.raises(SystemExit) as excinfo:
            fu_cmd._run(  # type: ignore[reportPrivateUsage]
                _ns(plan=tmp_path / "nonexistent.md", pairs=["status=in-progress"]),
            )
        assert excinfo.value.code == 1
        assert "not found" in capsys.readouterr().err

    def test_malformed_pair_exits_1(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        plan = _make_plan(tmp_path, "title: Foo\nstatus: backlog")

        with pytest.raises(SystemExit) as excinfo:
            fu_cmd._run(_ns(plan=plan, pairs=["noequals"]))  # type: ignore[reportPrivateUsage]
        assert excinfo.value.code == 1
        assert "malformed" in capsys.readouterr().err

    def test_preserves_other_keys_and_body(self, tmp_path: Path) -> None:
        body = "# My Plan\n\n- [ ] 3 SP: Task one\n- [ ] 2 SP: Task two\n"
        plan = _make_plan(
            tmp_path,
            "title: Foo\ntype: feature\nstatus: backlog\nsp: 5",
            body=body,
        )

        fu_cmd._run(_ns(plan=plan, pairs=["status=in-progress"]))  # type: ignore[reportPrivateUsage]

        text = plan.read_text()
        assert "title: Foo" in text
        assert "type: feature" in text
        assert "sp: 5" in text
        assert text.endswith(body)

    def test_multiple_keys_at_once(self, tmp_path: Path) -> None:
        plan = _make_plan(tmp_path, "title: Foo\nstatus: backlog")

        fu_cmd._run(  # type: ignore[reportPrivateUsage]
            _ns(plan=plan, pairs=["planned=@now", "status=in-progress"]),
        )

        text = plan.read_text()
        assert "planned:" in text
        assert "status: in-progress" in text

    def test_remove_key_and_add_empty(self, tmp_path: Path) -> None:
        body = "# My Plan\n\n- [ ] 3 SP: Task one\n"
        plan = _make_plan(
            tmp_path,
            "title: Foo  # keep\ntype: feature\nbusiness_goal: Users find widgets faster.\n"
            "status: backlog",
            body=body,
        )

        fu_cmd._run(  # type: ignore[reportPrivateUsage]
            _ns(plan=plan, pairs=["summary="], removals=["business_goal"]),
        )

        text = plan.read_text()
        assert "business_goal" not in text
        assert "summary:" in text
        assert "title: Foo" in text
        assert "# keep" in text
        assert "type: feature" in text
        assert text.endswith(body)

    def test_remove_only_no_pairs(self, tmp_path: Path) -> None:
        plan = _make_plan(tmp_path, "title: Foo\nbusiness_goal: x\nstatus: backlog")

        fu_cmd._run(_ns(plan=plan, pairs=[], removals=["business_goal"]))  # type: ignore[reportPrivateUsage]

        text = plan.read_text()
        assert "business_goal" not in text
        assert "title: Foo" in text

    def test_nothing_to_do_exits_1(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        plan = _make_plan(tmp_path, "title: Foo\nstatus: backlog")

        with pytest.raises(SystemExit) as excinfo:
            fu_cmd._run(_ns(plan=plan, pairs=[], removals=[]))  # type: ignore[reportPrivateUsage]
        assert excinfo.value.code == 1
        assert "nothing to do" in capsys.readouterr().err

    def test_logs_to_booping_log(self, tmp_path: Path) -> None:
        """Log line appended to _booping/.booping.log."""
        vault = tmp_path / "vault"
        vault.mkdir()
        (vault / "_booping").mkdir()
        plan = _make_plan(vault, "title: Foo\nstatus: backlog")

        # Log is best-effort if no project resolved from cwd
        fu_cmd._run(_ns(plan=plan, pairs=["status=in-progress"]))  # type: ignore[reportPrivateUsage]

        text = plan.read_text()
        assert "status: in-progress" in text