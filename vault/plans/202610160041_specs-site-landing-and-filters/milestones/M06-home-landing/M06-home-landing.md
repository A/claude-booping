---
id: "06"
title: "Home landing — lead, needs-you callout, scenarios, recently updated"
sp: 3
status: pending
plan: "plans/202610160041_specs-site-landing-and-filters/index.md"
---

# M06: Home landing — lead, needs-you callout, scenarios, recently updated

The home page becomes the documentation landing: what the project is, one link to what needs the owner, the types as reading scenarios, and what changed recently.

**Scope**: `booping-python/src/booping/specs/site/templates/index.html.j2`, `pages.py`, `machine.py` (only to share the lead-summary helper with `llms_txt`), `style.css` (`.callout`, `.scen`, `.recent`), `src/config.yaml` labels. Exactly `../../clarifications.md` C5: H1 site title; `<p class="lead">` from one helper used by both the home page and `llms_txt` (first value record of the first root with one); the `.callout` with the clarify icon, the plural link `{N} need you →` to `review.html` and the ` · {M} open questions` clause; the `.scen` grid of type cards linking `records.html#type={type}` (name, count, scenario); H2 "Recently updated" + `<ul class="recent">` of up to 10 rows (ref, title link, `<time datetime>` with `labels.date`). The per-root type lists leave the page.

Tests (integration, `site_pages_test.py`): a fixture with a value record, three records needing review, two clarify marks and twelve records with distinct `updated_at` — the lead equals the value's summary; the callout link text is the plural form for 3 and points at `review.html`; the questions clause says 2; the grid holds one card per non-empty type in type order with hand-counted counts; "Recently updated" lists exactly the 10 newest in order. No value record → no lead; nothing to review → no callout. Under `lang: ru` the callout uses the three-form plural (`3 записи ждут тебя`-style form from the `ru` table). Rebaseline `site-*.txtar` goldens and read the diff: `index.html` only.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | Landing template, shared lead helper, recent list, callout; CSS; labels. | `booping-python/src/booping/specs/site/templates/index.html.j2`, `booping-python/src/booping/specs/site/pages.py`, `booping-python/src/booping/specs/site/machine.py`, `booping-python/src/booping/specs/site/style.css`, `src/config.yaml` | 2 | pending |
| 6.2 | Tests; golden rebaseline. | `booping-python/tests/specs/site_pages_test.py`, `booping-python/e2e/cases/specs/site-*.txtar` | 1 | pending |

## Definition of Done

### Task 6.1

- [ ] Home matches C5; no count table and no per-root type list remain on it.
- [ ] `llms.txt` output is byte-identical to before (shared helper, same result).
- [ ] New colours, if any, pass `site_contrast_test.py`.

### Task 6.2

- [ ] Tests above pass; goldens differ only in `index.html`.

Return: the list of changed and created files, nothing else.

## References

- `../../../202610152329_specs-site-redesign/design/specs-site-mockup.html` — `home()`: `.lead`, `.callout`, `.scen`, `.recent`.
- `booping-python/src/booping/specs/site/machine.py` — the existing lead-summary lookup in `llms_txt`.

## Verify

`cd booping-python && uv run pytest tests/specs/site_pages_test.py tests/specs/site_machine_test.py tests/specs/site_contrast_test.py e2e -k site -q`
