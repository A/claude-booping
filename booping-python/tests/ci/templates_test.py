"""The shipped GitLab CI templates under `src/ci/gitlab/`."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, cast

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
TEMPLATES = REPO / "src" / "ci" / "gitlab"
NAMES = ["specs-site.gitlab-ci.yml", "specs-index.gitlab-ci.yml"]


def _load(name: str) -> dict[str, Any]:
    return cast(dict[str, Any], yaml.safe_load((TEMPLATES / name).read_text()))


@pytest.mark.parametrize("name", NAMES)
def test_one_pages_job_publishing_public(name: str) -> None:
    template = _load(name)

    assert list(template) == ["pages"]
    assert template["pages"]["artifacts"]["paths"] == ["public"]


@pytest.mark.parametrize("name", NAMES)
def test_every_cloned_path_a_script_runs_exists_in_the_repo(name: str) -> None:
    script = cast(list[str], _load(name)["pages"]["script"])

    paths = [p for line in script for p in re.findall(r"/tmp/booping/(\S+)", line)]

    assert paths
    for path in paths:
        assert (REPO / path).is_file(), path


def test_index_template_names_the_token_only_in_its_header() -> None:
    lines = (TEMPLATES / "specs-index.gitlab-ci.yml").read_text().splitlines()
    header = next(i for i, line in enumerate(lines) if not line.startswith("#"))
    body = lines[header:]

    assert all("SPECS_INDEX_TOKEN" not in line for line in body)
