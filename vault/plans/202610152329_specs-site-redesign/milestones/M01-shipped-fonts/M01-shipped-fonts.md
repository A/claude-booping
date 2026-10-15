---
id: "01"
title: "Shipped fonts — vendored woff2 embedded in fonts.css"
sp: 3
status: pending
plan: "plans/202610152329_specs-site-redesign/index.md"
---

# M01: Shipped fonts — vendored woff2 embedded in fonts.css

Every site and site-index output carries `fonts.css` with Golos Text and JetBrains Mono embedded, so text renders in the shipped faces from `file://` and from Pages, with nothing fetched at render or view time.

**Scope**: vendor the font files once, exactly as `../../clarifications.md` C3 names them, into `booping-python/src/booping/specs/site/fonts/`: `golos-text-cyrillic-wght-normal.woff2`, `golos-text-latin-wght-normal.woff2` from `https://cdn.jsdelivr.net/npm/@fontsource-variable/golos-text@5.3.0/files/`, `jetbrains-mono-cyrillic-wght-normal.woff2`, `jetbrains-mono-latin-wght-normal.woff2` from `https://cdn.jsdelivr.net/npm/@fontsource-variable/jetbrains-mono@5.3.0/files/`, and each package's `LICENSE` saved as `OFL-golos-text.txt` / `OFL-jetbrains-mono.txt`. Take each subset's `unicode-range` from the same package's `index.css` (`https://cdn.jsdelivr.net/npm/{package}@5.3.0/index.css`) and hold them as constants in a new module `booping-python/src/booping/specs/site/fonts.py`, with `font_files() -> dict[str, str | bytes]` returning `fonts.css` (four `@font-face` rules — families `"Golos Text"` weight `400 700`, `"JetBrains Mono"` weight `400 500`, `font-style: normal`, `font-display: swap`, `src: url(data:font/woff2;base64,…) format("woff2")`, the subset's `unicode-range` — in the fixed order golos cyrillic, golos latin, mono cyrillic, mono latin) plus `fonts/OFL-golos-text.txt` and `fonts/OFL-jetbrains-mono.txt` as bytes. `build_site` (`pages.py`) and `build_index` (`index.py`) merge `font_files()` into their result; `write.write_site` writes `bytes` values in binary mode and `str` values as today. Add `*.woff2 binary` to the repo-root `.gitattributes`. Pages do not link `fonts.css` yet — M04's shell does.

Tests (integration, `booping-python/tests/specs/site_fonts_test.py`): `fonts.css` holds exactly four `@font-face` blocks; each base64 payload decodes to the vendored file's bytes; two calls return identical output; `build_index([], "Specs")` and a one-record `build_site` both contain `fonts.css` and both licence files. Existing `site-*.txtar` goldens list output files only where they already do — none asserts `fonts.css` bytes.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Download the four woff2 files and two licences at the pinned versions; `.gitattributes` binary rule. | `booping-python/src/booping/specs/site/fonts/*`, `.gitattributes` | 1 | pending |
| 1.2 | `fonts.py` with `font_files()`; merge into `build_site`/`build_index`; binary-safe `write_site`; the tests above. | `booping-python/src/booping/specs/site/fonts.py`, `booping-python/src/booping/specs/site/pages.py`, `booping-python/src/booping/specs/site/index.py`, `booping-python/src/booping/specs/site/write.py`, `booping-python/tests/specs/site_fonts_test.py` | 2 | pending |

## Definition of Done

### Task 1.1

- [ ] The six files exist under `booping-python/src/booping/specs/site/fonts/`; each woff2 starts with the bytes `wOF2`.
- [ ] `git check-attr binary booping-python/src/booping/specs/site/fonts/golos-text-latin-wght-normal.woff2` reports `binary: set`.

### Task 1.2

- [ ] `font_files()` reads no network and no clock; output identical across calls.
- [ ] `booping specs site` output gains `fonts.css`, `fonts/OFL-golos-text.txt`, `fonts/OFL-jetbrains-mono.txt`; `site-index` output gains the same three.
- [ ] `write_site` writes a `bytes` value byte for byte.
- [ ] `uv run pytest tests/specs/site_fonts_test.py tests/specs/site_pages_test.py -q` passes.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/src/booping/specs/site/pages.py` — `build_site` reading `style.css` beside the module, the pattern for locating `fonts/`.
- `booping-python/tests/specs/site_pages_test.py` — test shape over `build_site` output.

## Verify

`cd booping-python && uv run pytest tests/specs e2e -k site -q`
