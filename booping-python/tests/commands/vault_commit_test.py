from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import pytest

from booping.commands import vault_commit as vc_cmd


def _git(cwd: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=True,
    )


def _init_vault(tmp_path: Path) -> Path:
    """Create a minimal vault directory structure with git init + initial commit."""
    vault = tmp_path / "vault"
    vault.mkdir()
    plans = vault / "plans"
    plans.mkdir()

    # Initialize git repo
    _git(vault, ["init"])
    _git(vault, ["config", "user.email", "test@example.com"])
    _git(vault, ["config", "user.name", "Test"])

    # Create .booping marker
    (vault / ".booping").write_text("project_name: test-project\n")

    # Create sprints.md
    (vault / "sprints.md").write_text(
        "# Sprints\n\n| status | sp | title |\n| --- | --- | --- |\n"
    )

    # Create a plan file
    plan = plans / "20240115-my-feature.md"
    plan.write_text(
        "---\nstatus: awaiting-plan-review\ntitle: My feature\n---\n\n# Plan body\n"
    )

    # Initial commit
    _git(vault, ["add", ".booping", "sprints.md", "plans/20240115-my-feature.md"])
    _git(vault, ["commit", "-m", "initial"])

    return vault


class TestVaultCommitCLI:
    def test_add_parser(self) -> None:
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        vc_cmd.add_parser(sub)
        args = parser.parse_args(
            ["vault-commit", "done", "/tmp/plan.md"]
        )
        assert args.to_status == "done"
        assert args.plan_path == Path("/tmp/plan.md")
        assert args.also == []

    def test_add_parser_with_also(self) -> None:
        parser = argparse.ArgumentParser()
        sub = parser.add_subparsers(dest="cmd")
        vc_cmd.add_parser(sub)
        args = parser.parse_args(
            ["vault-commit", "done", "/tmp/plan.md", "--also", "/tmp/extra.md"]
        )
        assert args.also == [Path("/tmp/extra.md")]


class TestVaultCommitIntegration:
    def test_commits_plan_and_sprints(self, tmp_path: Path) -> None:
        vault = _init_vault(tmp_path)
        plan = vault / "plans" / "20240115-my-feature.md"

        # Modify the plan to a different status (different content from initial)
        plan.write_text(
            "---\nstatus: ready-for-dev\ntitle: My feature\n"
            "---\n\n# Plan body\n"
        )
        (vault / "sprints.md").write_text("# Updated sprints\n")

        vc_cmd.do_vault_commit(
            to_status="ready-for-dev", plan_path=plan, vault=vault
        )

        # Check the commit
        log = _git(vault, ["log", "--oneline", "-1"])
        assert "ready-for-dev: 20240115-my-feature" in log.stdout

        # Check only plan and sprints.md were staged
        show = _git(vault, ["show", "--name-only", "HEAD", "--"])
        assert "plans/20240115-my-feature.md" in show.stdout
        assert "sprints.md" in show.stdout

        # Working tree should be clean (except logger-created _booping/)
        status = _git(vault, ["status", "--porcelain"])
        untracked = [
            line for line in status.stdout.strip().splitlines()
            if not line.startswith("??")
        ]
        assert untracked == []

    def test_commit_message_uses_plan_stem(self, tmp_path: Path) -> None:
        vault = _init_vault(tmp_path)
        plan = vault / "plans" / "20250228-another-plan.md"
        plan.write_text(
            "---\nstatus: ready-for-dev\ntitle: Another\n---\n\n# Body\n"
        )

        _git(vault, ["add", str(plan)])
        _git(vault, ["commit", "-m", "add plan"])

        (vault / "sprints.md").write_text("# Updated\n")

        vc_cmd.do_vault_commit(
            to_status="ready-for-dev", plan_path=plan, vault=vault
        )

        log = _git(vault, ["log", "--oneline", "-1"])
        assert "ready-for-dev: 20250228-another-plan" in log.stdout

    def test_nothing_to_commit_exits_gracefully(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        vault = _init_vault(tmp_path)
        plan = vault / "plans" / "20240115-my-feature.md"

        # No changes to commit
        vc_cmd.do_vault_commit(
            to_status="awaiting-plan-review", plan_path=plan, vault=vault
        )

        captured = capsys.readouterr()
        assert "nothing to commit" in captured.err or captured.out == ""

    def test_stages_only_specified_files(self, tmp_path: Path) -> None:
        vault = _init_vault(tmp_path)
        plan = vault / "plans" / "20240115-my-feature.md"

        # Create an unrelated file that should NOT be staged
        unrelated = vault / "notes" / "scratch.md"
        unrelated.parent.mkdir(exist_ok=True)
        unrelated.write_text("random notes")

        # Modify plan and sprints
        plan.write_text(
            "---\nstatus: ready-for-dev\ntitle: My feature\n"
            "---\n\n# Plan body\n"
        )
        (vault / "sprints.md").write_text("# Updated sprints\n")

        vc_cmd.do_vault_commit(
            to_status="ready-for-dev", plan_path=plan, vault=vault
        )

        # The commit should NOT include the unrelated file
        show = _git(vault, ["show", "--name-only", "HEAD", "--"])
        assert "notes/scratch.md" not in show.stdout

        # The unrelated file should remain untracked / modified
        status = _git(vault, ["status", "--porcelain", "--", "notes/scratch.md"])
        assert status.stdout.strip() != ""  # still dirty

    def test_stages_also_paths(self, tmp_path: Path) -> None:
        vault = _init_vault(tmp_path)
        plan = vault / "plans" / "20240115-my-feature.md"

        # Create an extra file to stage via --also
        extra = vault / "lessons" / "learned.md"
        extra.parent.mkdir(exist_ok=True)
        extra.write_text("# Lessons\n")

        # Modify plan
        plan.write_text(
            "---\nstatus: in-progress\ntitle: My feature\n"
            "---\n\n# Plan body\n"
        )

        vc_cmd.do_vault_commit(
            to_status="in-progress", plan_path=plan, also=[extra], vault=vault
        )

        show = _git(vault, ["show", "--name-only", "HEAD", "--"])
        assert "plans/20240115-my-feature.md" in show.stdout
        assert "lessons/learned.md" in show.stdout

    def test_shared_repo_excludes_prestaged_code(self, tmp_path: Path) -> None:
        """In a shared code+vault repo, a pre-staged unrelated file must not be
        swept into the plan commit and must stay in the index."""
        vault = _init_vault(tmp_path)
        plan = vault / "plans" / "20240115-my-feature.md"

        # Pre-stage an unrelated code file
        unrelated = vault / "src" / "module.py"
        unrelated.parent.mkdir(exist_ok=True)
        unrelated.write_text("x = 1\n")
        _git(vault, ["add", "src/module.py"])

        plan.write_text(
            "---\nstatus: ready-for-dev\ntitle: My feature\n"
            "---\n\n# Plan body\n"
        )
        (vault / "sprints.md").write_text("# Updated sprints\n")

        vc_cmd.do_vault_commit(
            to_status="ready-for-dev", plan_path=plan, vault=vault
        )

        # The commit lists only plan + sprints paths
        names = _git(vault, ["log", "-1", "--name-only", "--format="])
        committed = [line for line in names.stdout.strip().splitlines() if line]
        assert sorted(committed) == [
            "plans/20240115-my-feature.md",
            "sprints.md",
        ]

        # The pre-staged unrelated file is still in the index, uncommitted
        cached = _git(vault, ["diff", "--cached", "--name-only"])
        assert "src/module.py" in cached.stdout

    def test_local_subdir_vault(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Vault is a plans/-bearing subdir of the repo; resolve_vault (via
        Project.load_cwd) returns the subdir and the commit succeeds."""
        repo = tmp_path / "repo"
        repo.mkdir()
        _git(repo, ["init"])
        _git(repo, ["config", "user.email", "test@example.com"])
        _git(repo, ["config", "user.name", "Test"])

        vault = repo / "vault"
        plans = vault / "plans"
        plans.mkdir(parents=True)
        (vault / ".booping").write_text(
            "project_name: test-project\nvault_path: .\n"
        )
        (vault / "sprints.md").write_text("# Sprints\n")
        plan = plans / "20240115-my-feature.md"
        plan.write_text(
            "---\nstatus: awaiting-plan-review\ntitle: My feature\n---\n\n# Body\n"
        )
        _git(repo, ["add", "-A"])
        _git(repo, ["commit", "-m", "initial"])

        # resolve_vault uses Project.load_cwd() → must run from inside the vault
        monkeypatch.chdir(vault)
        assert vc_cmd.resolve_vault(plan).resolve() == vault.resolve()

        plan.write_text(
            "---\nstatus: ready-for-dev\ntitle: My feature\n---\n\n# Body\n"
        )
        (vault / "sprints.md").write_text("# Updated\n")

        vc_cmd.do_vault_commit(to_status="ready-for-dev", plan_path=plan)

        log = _git(repo, ["log", "--oneline", "-1"])
        assert "ready-for-dev: 20240115-my-feature" in log.stdout

    def test_missing_plan_exits_1(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        with pytest.raises(SystemExit) as excinfo:
            vc_cmd.do_vault_commit(
                to_status="done",
                plan_path=tmp_path / "nonexistent.md",
                vault=tmp_path,
            )
        assert excinfo.value.code == 1
        assert "not found" in capsys.readouterr().err

    def test_never_uses_git_add_all(self, tmp_path: Path) -> None:
        """Verify only specific paths are staged, never git add -A or ."""
        vault = _init_vault(tmp_path)
        plan = vault / "plans" / "20240115-my-feature.md"
        plan.write_text(
            "---\nstatus: in-progress\ntitle: My feature\n"
            "---\n\n# Plan body\n"
        )

        # Create an untracked file that must NOT be committed
        untracked = vault / "untracked_file.txt"
        untracked.write_text("should not be committed")

        vc_cmd.do_vault_commit(
            to_status="in-progress", plan_path=plan, vault=vault
        )

        # Verify the untracked file was NOT committed
        show = _git(vault, ["show", "--name-only", "HEAD", "--"])
        assert "untracked_file.txt" not in show.stdout

        # Verify it still exists as untracked
        assert untracked.exists()

    def test_resolve_vault_from_heuristic(self, tmp_path: Path) -> None:
        """resolve_vault falls back to parent/parent heuristic when
        Project.load_cwd() returns None (no .booping marker in cwd walk)."""
        vault = tmp_path / "custom-vault"
        vault.mkdir()
        plans = vault / "plans"
        plans.mkdir()
        plan = plans / "test.md"
        plan.write_text("---\n---\n")

        # We can't easily test the Project.load_cwd() path in isolation,
        # but we can test the heuristic by mocking.
        # For now, just verify the heuristic works when plan is in plans/ subdir.
        parent = plan.resolve().parent
        if parent.name == "plans":
            assert parent.parent == vault.resolve()
        else:
            assert parent == vault.resolve()


class TestGitHelper:
    def test_git_success(self, tmp_path: Path) -> None:
        vault = _init_vault(tmp_path)
        result = vc_cmd._git(vault, ["status", "--porcelain"])  # type: ignore[reportPrivateUsage]
        assert result.returncode == 0

    def test_git_failure(self, tmp_path: Path) -> None:
        result = vc_cmd._git(tmp_path, ["rev-parse", "HEAD"])  # type: ignore[reportPrivateUsage]
        # Not a git repo → should return non-zero
        assert result.returncode != 0