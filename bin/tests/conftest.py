import sys
from pathlib import Path

# Make bin/booping_plans.py importable from tests
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
import booping_plans


class ProjectFixture:
    """Helper returned by the tmp_project fixture."""

    def __init__(self, tmp_path: Path, project_name: str, monkeypatch):
        self.project_name = project_name
        # Set HOME so Path.home() resolves to tmp_path
        monkeypatch.setenv("HOME", str(tmp_path))
        self.plans_dir = tmp_path / "Claude" / project_name / "plans"
        self.plans_dir.mkdir(parents=True, exist_ok=True)
        self.claude_root = tmp_path / "Claude" / project_name
        self._capsys = None

    def write_plan(self, filename: str, content: str) -> Path:
        p = self.plans_dir / filename
        p.write_text(content, encoding="utf-8")
        return p

    def run(self, *args) -> tuple[int, str, str]:
        """Call booping_plans.main() with given args, returning (exitcode, stdout, stderr).

        Uses pytest's capsys if provided, otherwise uses subprocess-style capture
        via a direct call.
        """
        import io
        from contextlib import redirect_stdout, redirect_stderr

        stdout_buf = io.StringIO()
        stderr_buf = io.StringIO()
        with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
            rc = booping_plans.main(list(args))
        return rc, stdout_buf.getvalue(), stderr_buf.getvalue()


@pytest.fixture
def tmp_project(tmp_path, monkeypatch):
    """Returns a ProjectFixture with an isolated ~/Claude/<project>/plans/ tree."""
    project_name = "test-proj"
    return ProjectFixture(tmp_path, project_name, monkeypatch)
