from __future__ import annotations

from pathlib import Path


def get_fixture_path(name: str) -> Path:
    path = Path(__file__).parent / "__fixtures__" / name
    assert path.is_dir(), f"Fixture directory not found: {path}"
    return path
