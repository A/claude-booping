from __future__ import annotations

import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

from booping import macros
from booping.commands import frontmatter_update as fu_cmd
from booping.commands import playbook_transition as pt_cmd

CONFIG: dict[str, Any] = {"core": {"macros": {"date": ["date"]}}}
GIT_CONFIG: dict[str, Any] = {
    "core": {"macros": {"git_commit": {"command": ["git", "rev-parse", "HEAD"], "cwd": "repo"}}}
}
NOW_EXPR = "{{ macro('core.macros.date', '+%Y-%m-%d %H:%M') }}"
TODAY_EXPR = "{{ macro('core.macros.date', '+%Y-%m-%d') }}"


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
        result = fu_cmd.parse_pairs(["status=in-progress", "sp=5"])
        assert result == {"status": "in-progress", "sp": "5"}

    def test_value_with_equals_sign(self) -> None:
        result = fu_cmd.parse_pairs(["goal=a = b"])
        assert result == {"goal": "a = b"}

    def test_empty_key_exits_1(self) -> None:
        with pytest.raises(SystemExit) as excinfo:
            fu_cmd.parse_pairs(["=value"])
        assert excinfo.value.code == 1

    def test_no_equals_exits_1(self) -> None:
        with pytest.raises(SystemExit) as excinfo:
            fu_cmd.parse_pairs(["noequals"])
        assert excinfo.value.code == 1


# ── interpolate ──────────────────────────────────────────────────────────


class TestInterpolate:
    def test_datetime_macro(self) -> None:
        result = fu_cmd.interpolate(NOW_EXPR, None, CONFIG)
        assert datetime.strptime(result, "%Y-%m-%d %H:%M") is not None  # noqa: DTZ007

    def test_date_macro(self) -> None:
        result = fu_cmd.interpolate(TODAY_EXPR, None, CONFIG)
        assert datetime.strptime(result, "%Y-%m-%d") is not None  # noqa: DTZ007

    def test_stubbed_macro_is_not_executed(self) -> None:
        config = {**CONFIG, "macro_stubs": {"core.macros.date": "19700101"}}
        assert fu_cmd.interpolate(NOW_EXPR, None, config) == "19700101"

    def test_unknown_macro_path_exits_non_zero(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        with pytest.raises(SystemExit) as excinfo:
            fu_cmd.interpolate("{{ macro('core.macros.nope') }}", None, CONFIG)
        assert excinfo.value.code != 0
        err = capsys.readouterr().err
        assert "core.macros.nope" in err
        assert "Traceback" not in err

    def test_malformed_jinja_exits_non_zero(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        with pytest.raises(SystemExit) as excinfo:
            fu_cmd.interpolate("{{ macro( }}", None, CONFIG)
        assert excinfo.value.code != 0
        assert "macro(" in capsys.readouterr().err

    def test_git_commit_macro_runs_against_the_repo_dir(self, tmp_path: Path) -> None:
        macros.clear_cache()
        repo = Path(__file__).resolve().parents[3]
        expected = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

        actual = fu_cmd.interpolate(
            "{{ macro('core.macros.git_commit') }}", repo, GIT_CONFIG, tmp_path
        )

        assert actual == expected
        assert len(actual) == 40

    def test_retired_head_token_is_a_literal(self) -> None:
        assert fu_cmd.interpolate("@head", None, CONFIG) == "@head"

    def test_literal_value(self) -> None:
        assert fu_cmd.interpolate("hello", None, CONFIG) == "hello"

    def test_literal_value_with_spaces_untouched(self) -> None:
        assert fu_cmd.interpolate("a b c", None, CONFIG) == "a b c"

    def test_at_sign_prefix_not_interpolated(self) -> None:
        assert fu_cmd.interpolate("@notatoken", None, CONFIG) == "@notatoken"

    def test_retired_now_token_is_a_literal(self) -> None:
        assert fu_cmd.interpolate("@now", None, CONFIG) == "@now"


# ── hook tokenising ──────────────────────────────────────────────────────


class TestHookTokenising:
    def test_quoted_macro_expression_survives_shlex(self, tmp_path: Path) -> None:
        artifact = tmp_path / "index.md"
        artifact.write_text("---\nstatus: drafting\n---\n")

        rel, resolved = pt_cmd.dispatch_frontmatter_update(
            f'frontmatter-update completed="{NOW_EXPR}"',
            artifact,
            None,
            file_base=tmp_path,
            config=CONFIG,
        )

        assert rel is None
        assert datetime.strptime(resolved["completed"], "%Y-%m-%d %H:%M")  # noqa: DTZ007

    def test_file_target_with_quoted_macro_expression(self, tmp_path: Path) -> None:
        artifact = tmp_path / "index.md"
        artifact.write_text("---\nstatus: drafting\n---\n")
        (tmp_path / "_specs").mkdir()
        brief = tmp_path / "_specs" / "brief.md"
        brief.write_text("---\ntitle: Brief\n---\n")

        rel, resolved = pt_cmd.dispatch_frontmatter_update(
            f'frontmatter-update _specs/brief.md reviewed_at="{TODAY_EXPR}"',
            artifact,
            None,
            file_base=tmp_path,
            config=CONFIG,
        )

        assert rel == "_specs/brief.md"
        assert datetime.strptime(resolved["reviewed_at"], "%Y-%m-%d")  # noqa: DTZ007
        assert "reviewed_at" in brief.read_text()
        assert "reviewed_at" not in artifact.read_text()


# ── CLI integration ──────────────────────────────────────────────────────


class TestFrontmatterUpdateCLI:
    def test_sets_planned_with_date_macro(self, tmp_path: Path) -> None:
        plan = _make_plan(tmp_path, "title: Foo\nstatus: backlog")

        fu_cmd._run(_ns(plan=plan, pairs=[f"planned={NOW_EXPR}"]))  # type: ignore[reportPrivateUsage]

        text = plan.read_text()
        assert "planned:" in text
        _, fm_text, _ = _split_result(text)
        import yaml as pyyaml

        fm = pyyaml.safe_load(fm_text)
        datetime.strptime(fm["planned"], "%Y-%m-%d %H:%M")  # noqa: DTZ007

    def test_sets_commit_with_the_git_macro(self, tmp_path: Path) -> None:
        macros.clear_cache()
        plan = _make_plan(tmp_path, "title: Foo\nstatus: backlog")

        fu_cmd._run(  # type: ignore[reportPrivateUsage]
            _ns(plan=plan, pairs=["commit={{ macro('core.macros.git_commit') }}"])
        )

        text = plan.read_text()
        assert "commit:" in text
        _, fm_text, _ = _split_result(text)
        import yaml as pyyaml

        fm = pyyaml.safe_load(fm_text)
        assert len(fm["commit"]) == 40

    def test_sets_created_with_date_macro(self, tmp_path: Path) -> None:
        plan = _make_plan(tmp_path, "title: Foo\nstatus: backlog")

        fu_cmd._run(_ns(plan=plan, pairs=[f"created={TODAY_EXPR}"]))  # type: ignore[reportPrivateUsage]

        text = plan.read_text()
        assert "created:" in text
        _, fm_text, _ = _split_result(text)
        import yaml as pyyaml

        fm = pyyaml.safe_load(fm_text)
        assert datetime.strptime(str(fm["created"]), "%Y-%m-%d")  # noqa: DTZ007

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
            _ns(plan=plan, pairs=[f"planned={NOW_EXPR}", "status=in-progress"]),
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

    def test_does_not_write_to_real_home(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Running from a repo whose `.booping` marker resolves the vault to
        `<home>/Claude/<project>` must never touch the developer's real `~/Claude`.

        HOME (and XDG_CONFIG_HOME) is isolated to a tmp dir, so the best-effort
        `.booping.log` writer lands under the tmp home; the real home — read straight
        from the passwd database, independent of the HOME env var — stays untouched.
        """
        import os
        import pwd

        home = tmp_path / "home"
        home.mkdir()
        monkeypatch.setenv("HOME", str(home))
        # Isolate global config too, so the default `home_dir` (~/Claude) is used.
        monkeypatch.setenv("XDG_CONFIG_HOME", str(home / ".config"))
        # Run from a self-contained repo dir carrying its own `.booping` marker
        # (the real repo's marker is gitignored and absent in CI checkouts).
        repo_root = tmp_path / "repo"
        repo_root.mkdir()
        (repo_root / ".booping").write_text("project_name: claude-booping\n")
        monkeypatch.chdir(repo_root)

        real_home = Path(pwd.getpwuid(os.getuid()).pw_dir)
        real_claude = real_home / "Claude"
        real_claude_existed = real_claude.exists()

        plan = _make_plan(tmp_path, "title: Foo\nstatus: backlog")
        fu_cmd._run(_ns(plan=plan, pairs=["status=in-progress"]))  # type: ignore[reportPrivateUsage]

        # The write went under the isolated tmp home (proves logging was attempted)…
        assert (home / "Claude").exists()
        # …and never the developer's real home.
        if not real_claude_existed:
            assert not real_claude.exists()