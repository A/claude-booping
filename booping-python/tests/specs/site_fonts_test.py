from __future__ import annotations

import base64
import re
from pathlib import Path

from booping.specs.site import fonts
from booping.specs.site.fonts import font_files
from booping.specs.site.index import build_index
from booping.specs.site.model import SiteRoot, load_site
from booping.specs.site.pages import build_site
from booping.specs.site.write import write_site

FONT_DIR = Path(fonts.__file__).parent / "fonts"
SHIPPED = {"fonts.css", "fonts/OFL-golos-text.txt", "fonts/OFL-jetbrains-mono.txt"}


def test_fonts_css_embeds_the_four_vendored_faces_in_order() -> None:
    css = font_files()["fonts.css"]
    assert isinstance(css, str)
    assert css.count("@font-face") == 4
    payloads = re.findall(r"data:font/woff2;base64,([A-Za-z0-9+/=]+)", css)
    assert [base64.b64decode(p) for p in payloads] == [
        (FONT_DIR / name).read_bytes()
        for name in (
            "golos-text-cyrillic-wght-normal.woff2",
            "golos-text-latin-wght-normal.woff2",
            "jetbrains-mono-cyrillic-wght-normal.woff2",
            "jetbrains-mono-latin-wght-normal.woff2",
        )
    ]
    assert re.findall(r'font-family: "([^"]+)"', css) == [
        "Golos Text",
        "Golos Text",
        "JetBrains Mono",
        "JetBrains Mono",
    ]


def test_licences_ship_as_bytes() -> None:
    files = font_files()
    assert files["fonts/OFL-golos-text.txt"] == (FONT_DIR / "OFL-golos-text.txt").read_bytes()
    assert (
        files["fonts/OFL-jetbrains-mono.txt"] == (FONT_DIR / "OFL-jetbrains-mono.txt").read_bytes()
    )


def test_font_files_are_repeatable() -> None:
    assert font_files() == font_files()


def test_site_and_index_carry_the_fonts(tmp_path: Path) -> None:
    record = tmp_path / "core" / "value" / "0001-clarity.md"
    record.parent.mkdir(parents=True)
    record.write_text("---\ntitle: Clarity\n---\nBody.\n")
    site_files, _ = build_site(
        load_site([SiteRoot("core", tmp_path / "core")], ["value"]), ["value"]
    )
    assert SHIPPED <= set(site_files)
    assert SHIPPED <= set(build_index([], "Specs"))


def test_write_site_writes_bytes_verbatim(tmp_path: Path) -> None:
    out = tmp_path / "out"
    payload = (FONT_DIR / "golos-text-latin-wght-normal.woff2").read_bytes()
    write_site({"blob.bin": payload, "page.html": "ok\n"}, out, [])
    assert (out / "blob.bin").read_bytes() == payload
    assert (out / "page.html").read_text() == "ok\n"
