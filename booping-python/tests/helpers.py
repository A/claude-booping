from pathlib import Path

FIXTURES = Path(__file__).resolve().parent / "__fixtures__"


def get_fixture_path(name: str) -> Path:
    return FIXTURES / name