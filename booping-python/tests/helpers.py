from pathlib import Path


def get_fixture_path(name: str) -> Path:
    """Return absolute path to a fixture directory."""
    return Path(__file__).parent / "__fixtures__" / name