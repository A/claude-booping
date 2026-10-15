---
id: "08"
title: "Machine layer — llms.txt and index.json"
sp: 3
status: done
plan: "plans/202610152329_specs-site-redesign/index.md"
---

# M08: Machine layer — llms.txt and index.json

Every site output carries `llms.txt` and `index.json`, so an agent reads the whole specs set's metadata and relations without parsing HTML.

**Scope**: new module `booping-python/src/booping/specs/site/machine.py` with `llms_txt(site, states, labels, title) -> str` and `index_json(site, states, labels, title, lang) -> str`, exactly in the formats `../../clarifications.md` C9 locks (line shapes, ordering, escaping, `null`/`[]` rules, `ensure_ascii=False, indent=1`, trailing newline); record ids `{root}:{ref}`; `url` the record page path and `md` the `.md` copy path M09 writes (site-root-relative, both); `relations` from `Site.relations`, `superseded_by` from `Site.superseded_by`, `backlinks` from `Site.backlinks` (M05); type order as the site's page order; status labels in `llms.txt` through `labels.status`. `build_site` adds both files. Frontmatter dates that YAML parsed as `date` objects serialise as `YYYY-MM-DD` strings.

Tests (integration, `booping-python/tests/specs/site_machine_test.py`, expectations hand-derived): a two-root fixture (value with summary, rule with tags and status, ADR superseding another, one record with no summary and no status) → `llms.txt` equals the expected text exactly, including a title with `[brackets]` escaped and the omitted parenthetical; `index.json` parses, holds every record once in page order, the superseded ADR lists its superseder in `superseded_by`, the cross-root ref resolves to the other root's id, `reviewed` absent → `null`; two builds give identical bytes. One e2e case `booping-python/e2e/cases/specs/site-writes-llms-txt-and-index-json.txtar` asserting both files' full bytes for a three-record root.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 8.1 | `llms_txt` and its tests. | `booping-python/src/booping/specs/site/machine.py`, `booping-python/tests/specs/site_machine_test.py` | 1 | done |
| 8.2 | `index_json`, wiring into `build_site`, its tests, the e2e case. | `booping-python/src/booping/specs/site/machine.py`, `booping-python/src/booping/specs/site/pages.py`, `booping-python/tests/specs/site_machine_test.py`, `booping-python/e2e/cases/specs/site-writes-llms-txt-and-index-json.txtar` | 2 | done |

## Definition of Done

### Task 8.1

- [x] `llms.txt` follows llmstxt.org: one H1, optional blockquote, H2 file-list sections of `- [name](url): note` lines.
- [x] Output matches C9 character for character on the test fixture.

### Task 8.2

- [x] `index.json` key order is the C9 order for every record.
- [x] `uv run pytest tests/specs/site_machine_test.py -q` and the new e2e case pass.

Return: the list of changed and created files, nothing else.

## References

- `/home/anton/Dev/@A/shatterlings/crates/specs/src/site.rs` — `llms` (lines ~981–999), the port source.
- `booping-python/e2e/cases/specs/site-renders-one-root-with-links-and-marks.txtar` — e2e case shape.

## Verify

`cd booping-python && uv run pytest tests/specs/site_machine_test.py e2e -k site -q`
