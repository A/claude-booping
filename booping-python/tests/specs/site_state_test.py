from __future__ import annotations

from pathlib import Path

from booping.specs.site.markdown import render_body
from booping.specs.site.model import SiteRecord, SiteRoot, load_site
from booping.specs.site.state import RecordState, record_state

TYPES = ["value", "adr", "conflict", "idea"]


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def _states(tmp_path: Path) -> dict[str, RecordState]:
    site = load_site([SiteRoot("s", tmp_path / "s")], TYPES)

    def state(record: SiteRecord) -> RecordState:
        rendered = render_body(
            record.body,
            first_line=record.body_first_line,
            link=lambda dest: (dest, None),
            statuses=set(),
        )
        return record_state(record, rendered.marks)

    return {record.ref: state(record) for record in site.records}


def test_reasons_follow_the_fixed_order_and_marks_anchor_per_kind(tmp_path: Path) -> None:
    # Body starts on line 5: three frontmatter lines between the delimiters.
    _write(
        tmp_path / "s" / "adr" / "0001-pick.md",
        "---\ntitle: Pick\nstatus: accepted\n---\n"
        "Intro.\n\nWho [unknown] owns it?\n\nWe [clarify] this.\n\nAnd [clarify] that.\n",
    )
    _write(
        tmp_path / "s" / "conflict" / "0001-clash.md",
        "---\ntitle: Clash\nstatus: open\n"
        "review: accepted\nreview_evidence: site review — 2026-10-01\n"
        "---\nx\n",
    )
    _write(
        tmp_path / "s" / "adr" / "0002-done.md",
        "---\ntitle: Done\nstatus: accepted\n"
        "review: accepted\nreview_evidence: site review — 2026-10-01\n"
        "---\nx\n",
    )
    states = _states(tmp_path)

    pick = states["adr/0001"]
    assert pick.reasons == ("not_accepted", "clarify", "unknown")
    assert pick.first_unknown == "L7"
    assert pick.first_clarify == "L9"
    assert pick.first_mark == "L7"
    assert states["conflict/0001"].reasons == ("conflict",)
    assert states["adr/0002"].reasons == ()


def test_proposed_adr_and_open_idea_are_reasons(tmp_path: Path) -> None:
    _write(
        tmp_path / "s" / "adr" / "0001-maybe.md",
        "---\ntitle: Maybe\nstatus: proposed\n"
        "review: accepted\nreview_evidence: site review — 2026-10-01\n"
        "---\nx\n",
    )
    _write(
        tmp_path / "s" / "idea" / "0001-spark.md",
        "---\ntitle: Spark\nstatus: open\n"
        "review: accepted\nreview_evidence: site review — 2026-10-01\n"
        "---\nx\n",
    )
    _write(
        tmp_path / "s" / "conflict" / "0001-settled.md",
        "---\ntitle: Settled\nstatus: resolved\n"
        "review: accepted\nreview_evidence: site review — 2026-10-01\n"
        "---\nx\n",
    )
    states = _states(tmp_path)

    assert states["adr/0001"].reasons == ("proposed",)
    assert states["idea/0001"].reasons == ("open",)
    assert states["conflict/0001"].reasons == ()
    assert states["conflict/0001"].first_clarify is None
