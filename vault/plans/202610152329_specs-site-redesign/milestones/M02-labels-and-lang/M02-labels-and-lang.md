---
id: "02"
title: "Labels and lang — config label table, html lang, site title"
sp: 3
status: pending
plan: "plans/202610152329_specs-site-redesign/index.md"
---

# M02: Labels and lang — config label table, html lang, site title

Every page renders its UI strings, type names, status names, fact labels and dates from a configurable label table in the configured language, with `<html lang>` set to it and a site title from `--title`.

**Scope**: config keys in `src/config.yaml` under `core.specs.site` (beside `roots`), commented like their neighbours: `lang: en` and `labels: {en: …, ru: …}` with the shape `../../clarifications.md` C4 fixes — `ui` (ids: `skip`, `overview`, `menu`, `close`, `theme_auto`, `theme_light`, `theme_dark`, `on_this_page`, `referenced_by`, `records`, `types`, `marks`, `not_found`, `not_found_home`, `generator`, `not_reviewed`, `unreviewed`, `clarify`, `unknown`, `superseded_by`, `chosen`), `types.{value,rule,adr,conflict,story,idea,reference,runbook}` each `{name, plural, scenario}` (en scenarios: value «why the project exists», rule «what constrains decisions», adr «why it was decided so», conflict «where values pull apart», story «who wants what and why», idea «what is still a guess», reference «facts the code does not show», runbook «how to operate it»; ru: «Ценности — зачем этот проект и какой он», «Правила — что ограничивает решения», «Решения — почему решили так», «Конфликты — где ценности тянут в разные стороны», «Истории — кто чего хочет и зачем», «Идеи — что пока догадка», «Справки — факты, которых не видно в коде», «Ранбуки — как этим управлять»; names ru: Ценность/Ценности, Правило/Правила, Решение/Решения, Конфликт/Конфликты, История/Истории, Идея/Идеи, Справка/Справки, Ранбук/Ранбуки), `statuses` (every status of `src/specs/README.md`'s Frontmatter section; ru: принято, отклонено, предложено, заменено, выведено, открыто, решено, сделано, запланировано, отложено, проверяется, действует), `facts.{created_by,created_at,updated_at,reviewed,tags,sources,values,rules,supersedes}` (ru: Автор, Создано, Изменено, Ревью, Теги, Источники, Служит ценностям, Правила, Заменяет), `authors.{owner,claude}` (ru: владелец, агент), `months` (en `January`…; ru genitive `января`…`декабря`). `clarify` is a list of plural forms, each with `{n}` (en `["{n} question for you", "{n} questions for you"]`; ru `["{n} вопрос к тебе", "{n} вопроса к тебе", "{n} вопросов к тебе"]`); `Labels.plural(id, n)` picks the form — a three-form list by the Slavic rule (`n%10==1 and n%100!=11` → 0; `n%10 in 2..4 and n%100 not in 12..14` → 1; else 2), a two-form list by `n==1` → 0 else 1. New module `booping-python/src/booping/specs/site/labels.py`: `Labels` with `ui(id, **fmt)`, `type_name(type)`, `type_plural(type)`, `scenario(type)`, `status(s)`, `fact(key)`, `author(v)`, `date(value)` (C11), built by `load_labels(config_site: dict) -> tuple[Labels, str, list[str]]` returning the labels, the lang and warnings; fallback per C4 (lang → en → raw id; unknown type → its id as name and plural, empty scenario). `booping specs site` gains `--title TEXT` (C5) in `booping-python/src/booping/commands/specs.py`; `_run_site` reads `core.specs.site` from the merged config, prints each label warning as `warning: {text}` on stderr, and passes labels, lang and title to `build_site`. `environment()` exposes them as template globals `labels`, `lang`, `site_title`; `base.html.j2` emits `<html lang="{{ lang }}">` and `<title>{page title} — {site_title}</title>`. `build_index` (`index.py`) renders with `load_labels({})` (English, `lang` `en`) until M10 wires `site-index` to config, so its page keeps rendering through the shared base template. Existing templates switch their hardcoded English strings and raw status/fact keys to `labels` calls.

Tests (integration): `booping-python/tests/specs/site_labels_test.py` — `ru` returns the Russian type plural; a key missing in `ru` falls back to `en`; unknown lang `de` → `en` labels, lang stays `de`, one warning; unknown type `mechanic` → `mechanic`; a project-tier override `labels.ru.types.mechanic` wins; `date("2026-10-15")` in ru is `15 октября 2026`, `date("someday")` is `someday`; `plural("clarify", n)` in ru for n = 1, 3, 5, 11, 21, 22 gives вопрос, вопроса, вопросов, вопросов, вопрос, вопроса. e2e: rebaseline the `site-*.txtar` goldens (`--txtar-update`) and read the diff — only `lang`, `<title>` and label text change.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | `core.specs.site.lang` and `core.specs.site.labels.{en,ru}` in config. | `src/config.yaml` | 1 | pending |
| 2.2 | `labels.py`, `--title`, wiring into `_run_site`/`environment()`/templates, the tests, golden rebaseline. | `booping-python/src/booping/specs/site/labels.py`, `booping-python/src/booping/specs/site/pages.py`, `booping-python/src/booping/specs/site/templates/*.j2`, `booping-python/src/booping/commands/specs.py`, `booping-python/tests/specs/site_labels_test.py`, `booping-python/e2e/cases/specs/site-*.txtar` | 2 | pending |

## Definition of Done

### Task 2.1

- [ ] `bin/booping config-get core.specs.site.labels.ru.types.adr` prints the ru `name`/`plural`/`scenario`.
- [ ] Every status listed in `src/specs/README.md` has an `en` and a `ru` label.

### Task 2.2

- [ ] `booping specs site --help` lists `--title` with its default.
- [ ] With `core.specs.site.lang: ru` in a vault config, `<html lang="ru">` and Russian labels appear on every page.
- [ ] No template carries a hardcoded English UI string (the `Specs` crumb included).
- [ ] `site-index-*.txtar` cases still pass after their rebaseline.
- [ ] `uv run pytest tests/specs/site_labels_test.py -q` passes; the rebaselined goldens differ only in `lang`, `<title>` and label text.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/src/booping/commands/specs.py` — `_default_roots` reading `core.specs.site.roots` from the merged config; `site-index --title` for the flag shape.
- `src/config.yaml` — the `core.specs` block's comment style.

## Verify

`cd booping-python && uv run pytest tests/specs e2e -k site -q`
