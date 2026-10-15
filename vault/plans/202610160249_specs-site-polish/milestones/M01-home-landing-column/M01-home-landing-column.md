---
id: "01"
title: "Home landing column and callout breakdown"
sp: 3
status: pending
plan: "/home/anton/Dev/@A/claude-booping-specs/vault/plans/202610160249_specs-site-polish/index.md"
---

# M01: Home landing column and callout breakdown

The home page reads as the prototype's landing: lead, callout and Recently updated sit in the 68ch column, the callout names its breakdown, and a phone Recently-updated row no longer squeezes its title.

**Scope**: `booping-python/src/booping/specs/site/pages.py` (the `index.html.j2` page call passes `unreviewed` — the count of records whose `RecordState.unreviewed` is true — beside `needs` and `questions`), `templates/index.html.j2` (lead and callout wrapped in one `<div class="measure">`, the Recently-updated `h2` and list in a second; the `ul.scen` grid stays outside, full width; callout text exactly `../../clarifications.md` C3), `src/config.yaml` (new plural label `unreviewed_n`, `en` and `ru`, strings from C3), `style.css` (inside the existing 760px phone block: `.recent li` wraps, the `time` drops to its own line under the title, left-aligned — C5). The `.measure` token (68ch) already exists in `style.css` and is reused, never redefined.

Tests (integration, `booping-python/tests/specs/site_pages_test.py`): extend `test_home_lead_callout_scenarios_and_recent` — the callout's text after the link is ` · {u} unreviewed · {q} open questions` with hand-derived counts from its fixture; a fixture with every record reviewed omits the `unreviewed` part; lead and Recently updated sit inside `class="measure"`, `ul.scen` does not; the home page holds no `class="mark"` and no `[clarify]` text. Extend `test_new_navigation_labels_resolve_from_the_russian_table` (or the Russian home test nearest it) with the `ru` callout text from C3. Rebaseline the `site-*.txtar` goldens and read the diff: home page markup only.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Callout breakdown: `unreviewed` count, `unreviewed_n` label en/ru, template line; tests. | `booping-python/src/booping/specs/site/pages.py`, `booping-python/src/booping/specs/site/templates/index.html.j2`, `src/config.yaml`, `booping-python/tests/specs/site_pages_test.py` | 2 | pending |
| 1.2 | `.measure` wrappers on home; phone Recently-updated wrap in CSS; golden rebaseline. | `booping-python/src/booping/specs/site/templates/index.html.j2`, `booping-python/src/booping/specs/site/style.css`, `booping-python/e2e/cases/specs/site-*.txtar` | 1 | pending |

## Definition of Done

### Task 1.1

- [ ] The callout reads `{needs_you} link` + ` · {unreviewed_n}` + ` · {open_questions}`, a zero part omitted, no callout at `needs` 0; en and ru strings exactly C3.
- [ ] `unreviewed_n` is in `labels.en.ui` and `labels.ru.ui` of `src/config.yaml` with the forms from C3.
- [ ] The home test asserts the hand-derived en text; a Russian test asserts the ru text.

### Task 1.2

- [ ] Lead + callout and Recently updated each sit in a `div.measure`; `ul.scen` is outside both.
- [ ] Below 760px a Recently-updated `li` shows the date under the title; at 1300px the row is unchanged.
- [ ] `site-*.txtar` goldens rebaselined with `just e2e -k site --txtar-update`; their diff touches the home page only.

Return: the list of changed and created files, nothing else.

## References

- `vault/plans/202610152329_specs-site-redesign/design/specs-site-mockup.html` — `home()` and the `.measure` / `.callout` / `.recent` CSS: the approved shape.
- `booping-python/tests/specs/site_pages_test.py` — `test_home_lead_callout_scenarios_and_recent`: the test to extend.

## Verify

`cd booping-python && uv run pytest tests/specs/site_pages_test.py e2e -k site -q`
