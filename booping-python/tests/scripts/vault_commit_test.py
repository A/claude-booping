"""Vault-commit hooks against a vault inside a git work tree.

Each plugin-shipped vault-commit hook runs as a subprocess the way `booping
playbook-transition` runs it, over real `git` in two layouts: **nested** — the vault is
`repo/vault` inside a larger repository that also holds an unrelated staged change — and
**own repo** — the vault is the repository.
"""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import NamedTuple

import pytest

PLAYBOOKS = Path(__file__).resolve().parents[3] / "playbooks"

PLAN_SLUG = "20261014_plan"
PLAN_REL = f"plans/{PLAN_SLUG}/index.md"
REVIEW_REL = f"codereviews/{PLAN_SLUG}/202610142200.md"
RETRO_REL = "retrospectives/20261014_retro.md"


class Hook(NamedTuple):
    script: Path
    argv: list[str]
    workdir: str
    artifact: str
    committed: set[str]
    seed: Callable[[Path], None]


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def _seed_plan(vault: Path) -> None:
    _write(vault / PLAN_REL, "---\ntitle: Plan\nstatus: done\nretro: null\n---\n\n# Plan\n")
    _write(vault / "notes/unrelated.md", "not named by any hook\n")


def _seed_review(vault: Path, plan: str = PLAN_REL) -> None:
    _seed_plan(vault)
    _write(vault / REVIEW_REL, f"---\nplan: {plan}\nstatus: done\n---\n\n# Review\n")


def _seed_retro(vault: Path) -> None:
    _seed_plan(vault)
    _write(
        vault / RETRO_REL,
        f"---\nstatus: awaiting-learning\nplans:\n  - {PLAN_REL}\n---\n\n# Retro\n",
    )


HOOKS = {
    "commit-plan": Hook(
        PLAYBOOKS / "groom" / "_scripts" / "commit-plan",
        [],
        f"plans/{PLAN_SLUG}",
        PLAN_REL,
        {PLAN_REL},
        _seed_plan,
    ),
    "close-code-review": Hook(
        PLAYBOOKS / "code-review" / "_scripts" / "close-code-review",
        [],
        ".",
        REVIEW_REL,
        {REVIEW_REL, PLAN_REL},
        _seed_review,
    ),
    "close-working-set": Hook(
        PLAYBOOKS / "_scripts" / "close-working-set",
        ["--prefix", "retro"],
        ".",
        RETRO_REL,
        {RETRO_REL, PLAN_REL},
        _seed_retro,
    ),
    "drop-plan": Hook(
        PLAYBOOKS / "retro" / "_scripts" / "drop-plan",
        [PLAN_SLUG],
        ".",
        PLAN_REL,
        {PLAN_REL},
        _seed_plan,
    ),
}


class Layout(NamedTuple):
    repo: Path
    vault: Path
    prefix: str


def _env(tmp_path: Path) -> dict[str, str]:
    return {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(tmp_path),
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
    }


def _git(repo: Path, env: dict[str, str], *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], env=env, capture_output=True, text=True, check=True
    ).stdout


def _init_repo(repo: Path, env: dict[str, str]) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    _git(repo, env, "init", "-q")
    _git(repo, env, "config", "user.name", "Test")
    _git(repo, env, "config", "user.email", "test@example.com")
    _write(repo / "README.md", "seed\n")
    _git(repo, env, "add", "README.md")
    _git(repo, env, "commit", "-q", "-m", "seed")


def _nested(tmp_path: Path, env: dict[str, str]) -> Layout:
    repo = tmp_path / "repo"
    _init_repo(repo, env)
    _write(repo / "src/x.txt", "unrelated work\n")
    _git(repo, env, "add", "src/x.txt")
    return Layout(repo, repo / "vault", "vault/")


def _own_repo(tmp_path: Path, env: dict[str, str]) -> Layout:
    vault = tmp_path / "vault"
    _init_repo(vault, env)
    return Layout(vault, vault, "")


def _run(hook: Hook, vault: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    workdir = (vault / hook.workdir).resolve()
    return subprocess.run(
        [sys.executable, str(hook.script), *hook.argv],
        cwd=workdir,
        env={
            **env,
            "BOOPING_WORKDIR": str(workdir),
            "BOOPING_ARTIFACT": str(vault / hook.artifact),
        },
        capture_output=True,
        text=True,
    )


def _head(repo: Path, env: dict[str, str]) -> str:
    return _git(repo, env, "rev-parse", "HEAD").strip()


def _head_paths(repo: Path, env: dict[str, str]) -> set[str]:
    return set(_git(repo, env, "show", "--name-only", "--format=", "HEAD").split())


@pytest.mark.parametrize("hook", HOOKS.values(), ids=list(HOOKS))
def test_nested_vault_commit_carries_only_vault_paths(tmp_path: Path, hook: Hook) -> None:
    env = _env(tmp_path)
    layout = _nested(tmp_path, env)
    hook.seed(layout.vault)
    before = _head(layout.repo, env)

    result = _run(hook, layout.vault, env)

    assert result.returncode == 0, result.stderr
    assert _head(layout.repo, env) != before
    assert _head_paths(layout.repo, env) == {f"vault/{rel}" for rel in hook.committed}
    assert _git(layout.repo, env, "diff", "--cached", "--name-only").split() == ["src/x.txt"]


@pytest.mark.parametrize("hook", HOOKS.values(), ids=list(HOOKS))
def test_own_repo_vault_commit_carries_the_hook_paths(tmp_path: Path, hook: Hook) -> None:
    env = _env(tmp_path)
    layout = _own_repo(tmp_path, env)
    hook.seed(layout.vault)
    before = _head(layout.repo, env)

    result = _run(hook, layout.vault, env)

    assert result.returncode == 0, result.stderr
    assert _head(layout.repo, env) != before
    assert _head_paths(layout.repo, env) == hook.committed


@pytest.mark.parametrize("make_layout", [_nested, _own_repo], ids=["nested", "own-repo"])
def test_a_rerun_with_no_changes_commits_nothing(
    tmp_path: Path, make_layout: Callable[[Path, dict[str, str]], Layout]
) -> None:
    env = _env(tmp_path)
    layout = make_layout(tmp_path, env)
    hook = HOOKS["close-code-review"]
    _seed_review(layout.vault, plan="null")
    assert _run(hook, layout.vault, env).returncode == 0
    first = _head(layout.repo, env)
    assert _head_paths(layout.repo, env) == {f"{layout.prefix}{REVIEW_REL}"}

    result = _run(hook, layout.vault, env)

    assert result.returncode == 0, result.stderr
    assert _head(layout.repo, env) == first
    assert "vault-commit: nothing to commit" in result.stdout


def _empty_dir(vault: Path) -> None:
    (vault / "extra").mkdir(parents=True)


def _ignored_only_dir(vault: Path) -> None:
    _write(vault / ".gitignore", "extra/*.tmp\n")
    _write(vault / "extra/scratch.tmp", "ignored\n")


@pytest.mark.parametrize("make_layout", [_nested, _own_repo], ids=["nested", "own-repo"])
@pytest.mark.parametrize(
    "make_extra", [_empty_dir, _ignored_only_dir], ids=["empty", "ignored-only"]
)
def test_a_stage_dir_with_nothing_to_add_still_commits_the_artifact(
    tmp_path: Path,
    make_layout: Callable[[Path, dict[str, str]], Layout],
    make_extra: Callable[[Path], None],
) -> None:
    env = _env(tmp_path)
    layout = make_layout(tmp_path, env)
    base = HOOKS["close-working-set"]
    hook = base._replace(argv=[*base.argv, "--stage", "extra"])
    hook.seed(layout.vault)
    make_extra(layout.vault)
    before = _head(layout.repo, env)

    result = _run(hook, layout.vault, env)

    assert result.returncode == 0, result.stderr
    assert _head(layout.repo, env) != before
    assert _head_paths(layout.repo, env) == {f"{layout.prefix}{rel}" for rel in hook.committed}
    assert "vault-commit: ok" in result.stdout


def test_a_failing_commit_aborts_with_gits_error(tmp_path: Path) -> None:
    env = _env(tmp_path)
    layout = _own_repo(tmp_path, env)
    hook_file = layout.repo / ".git/hooks/pre-commit"
    _write(hook_file, "#!/bin/sh\necho 'rejected by pre-commit' >&2\nexit 1\n")
    hook_file.chmod(0o755)
    hook = HOOKS["commit-plan"]
    hook.seed(layout.vault)
    before = _head(layout.repo, env)

    result = _run(hook, layout.vault, env)

    assert result.returncode != 0
    assert "rejected by pre-commit" in result.stderr
    assert _head(layout.repo, env) == before
