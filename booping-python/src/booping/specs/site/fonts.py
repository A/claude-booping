from __future__ import annotations

import base64
from pathlib import Path

_DIR = Path(__file__).parent / "fonts"

# unicode-range values from each @fontsource-variable package's index.css at 5.3.0.
_CYRILLIC = "U+0301,U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116"
_LATIN = (
    "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,"
    "U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD"
)

_FACES = (
    ("Golos Text", "400 700", "golos-text-cyrillic-wght-normal.woff2", _CYRILLIC),
    ("Golos Text", "400 700", "golos-text-latin-wght-normal.woff2", _LATIN),
    ("JetBrains Mono", "400 500", "jetbrains-mono-cyrillic-wght-normal.woff2", _CYRILLIC),
    ("JetBrains Mono", "400 500", "jetbrains-mono-latin-wght-normal.woff2", _LATIN),
)

_LICENCES = ("OFL-golos-text.txt", "OFL-jetbrains-mono.txt")


def _face(family: str, weight: str, file: str, unicode_range: str) -> str:
    data = base64.b64encode((_DIR / file).read_bytes()).decode("ascii")
    return (
        "@font-face {\n"
        f'  font-family: "{family}";\n'
        "  font-style: normal;\n"
        f"  font-weight: {weight};\n"
        "  font-display: swap;\n"
        f'  src: url(data:font/woff2;base64,{data}) format("woff2");\n'
        f"  unicode-range: {unicode_range};\n"
        "}\n"
    )


def font_files() -> dict[str, str | bytes]:
    """Out-root-relative path → content: `fonts.css` with the vendored woff2 faces
    embedded as data URIs (Firefox blocks `file://` fonts from parent directories),
    plus the OFL licence texts."""
    files: dict[str, str | bytes] = {"fonts.css": "\n".join(_face(*face) for face in _FACES)}
    for name in _LICENCES:
        files[f"fonts/{name}"] = (_DIR / name).read_bytes()
    return files
