---
id: "02"
title: "Request and backlog items with verbatim text"
sp: 4
status: done
plan: "plans/202610151825_user-request-items/index.md"
---

# M02: Request and backlog items with verbatim text

`booping items add --text -` files a user's words, read from stdin, as an item with `source: request`, `direction: null` and the words byte-for-byte as its body; spec-gap items file exactly as before.

**Scope**: `booping-python/src/booping/specs/open_items.py` and the `add` runner in `booping-python/src/booping/commands/items.py` (moved there by M01), plus the scaffold comment in `src/config.yaml`.

- `SOURCES` gains `request` and `backlog`; a module constant names the two non-spec-gap sources (`REQUEST_SOURCES = ("request", "backlog")`) and every rule below reads it.
- `--body` is replaced by `--text TEXT`; `--text -` reads all of stdin. Help: `The item body, verbatim; - reads stdin`.
- Source defaulting, in order: `--record adr/NNNN` → `adr`; explicit `--source`; `--direction` given → `manual`; otherwise `request`. `--source` help becomes `One of: {SOURCES} (default: adr with --record adr/NNNN, manual with --direction, otherwise request)`.
- For a `REQUEST_SOURCES` source: `--text` is required and non-empty after stripping whitespace; `--direction` is rejected; `direction` is written as `null`; `--title` is optional and, absent, is `truncate(first_sentence(text))` taken from the text's first non-blank line. `--record` stays allowed.
- For every other source the existing rules hold unchanged (`--title` and `--direction` required unless `--record` names an ADR).
- The scaffold renders `direction: null` when `direction` is null (same pattern as `record`).
- Verbatim body: the item file is the frontmatter, a blank line, `# {title}`, a blank line, then the text exactly as given — `{{ }}`, `{% %}`, `---` lines, inner blank lines and trailing spaces untouched, never evaluated as Jinja — with one `\n` appended only when the text does not already end in one. The text stays the scaffold's `body` variable (Jinja does not re-parse a variable's value); fix the scaffold's whitespace control so the bytes on disk match this contract.
- `correction.py` calls `write_item` with the renamed parameter if the signature changes.

Errors (stderr `error: …`, exit 1, nothing on stdout, no file written):
- `--text is required for source request` (or `backlog`)
- `--text is empty`
- `--direction does not apply to source request` (or `backlog`)

Tests: integration tier, new e2e cases under `booping-python/e2e/cases/items/`, expected files hand-written:
- `add-request-from-stdin-keeps-the-text-verbatim.txtar` — `sh -c 'booping items add --text - < msg.txt'` with a `fixtures/cwd/msg.txt` holding two paragraphs, a `{{ x }}` and a `{% if %}`, a `---` line and a line with trailing spaces → `source: request`, `direction: null`, derived title, body identical to the fixture.
- `add-request-with-a-title-and-argv-text.txtar` — `--title … --text "…"` → title as given, text as body.
- `add-backlog-item.txtar` — `--source backlog --text …`.
- `add-request-with-a-direction-is-rejected.txtar`, `add-request-without-text-is-rejected.txtar`, `add-request-with-blank-text-is-rejected.txtar`.
- The moved `add-by-hand-files-the-first-item.txtar` switches `--body` to `--text` and stays `source: manual`.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Sources, defaulting, request validation, `--text`/stdin, title derivation, verbatim body, null direction in the scaffold. | `booping-python/src/booping/specs/open_items.py`, `booping-python/src/booping/commands/items.py`, `booping-python/src/booping/correction.py`, `src/config.yaml` | 2 | done |
| 2.2 | The six new cases and the `--body` → `--text` switch in existing cases. | `booping-python/e2e/cases/items/*.txtar` | 2 | done |

## Definition of Done

### Task 2.1

- [x] `bin/booping items add --help` shows `--text` and the new `--source` default text; no `--body`.
- [x] Each error in Scope exits 1 with exactly that message and writes no file.
- [x] A spec-gap `add` (`--title --direction`) produces the same file as before this milestone.

### Task 2.2

- [x] The six cases in Tests exist and pass; `grep -rn -- "--body" booping-python/e2e/cases/items` prints nothing.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/e2e/cases/items/add-by-hand-files-the-first-item.txtar` (after M01) — case shape to copy.
- `booping-python/e2e/conftest.py` — `bin/` leads PATH, so `booping` resolves inside `sh -c`.
- `src/config.yaml` `core.specs.open_items.scaffold` — the item file format.

## Verify

`cd booping-python && uv run pytest e2e/cases/items e2e/cases/correction -q`
