from __future__ import annotations

from pathlib import Path, PurePosixPath

from booping.sidecar import Sidecar, next_number

TARGET = PurePosixPath("plans/p/index.md")


def _open(vault: Path) -> Sidecar:
    return Sidecar.open(vault, TARGET, name="log.md", heading="# Log", prefix="D")


def test_numbering_continues_from_the_highest_entry_of_its_own_prefix() -> None:
    text = "# Log\n\n## D2 — a — t\n\n## D7 — b — t\n\n## R9 — c — t\n"
    assert next_number(text, "D") == 8
    assert next_number(text, "R") == 10
    assert next_number("# Log\n", "D") == 1


def test_a_missing_sidecar_starts_at_its_heading_and_number_one(tmp_path: Path) -> None:
    (tmp_path / "plans" / "p").mkdir(parents=True)
    log = _open(tmp_path)
    assert (log.rel, log.number) == (PurePosixPath("plans/p/log.md"), 1)
    log.append(f"{log.header('step', 'now')}\n\n{log.artifact_line(TARGET)}\n")
    text = (tmp_path / "plans/p/log.md").read_text()
    assert text == "# Log\n\n## D1 — step — now\n\n**Artifact:** [index.md](index.md)\n"
    assert _open(tmp_path).number == 2
