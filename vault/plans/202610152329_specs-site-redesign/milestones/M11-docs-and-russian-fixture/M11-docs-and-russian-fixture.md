---
id: "11"
title: "Docs and a Russian fixture case"
sp: 3
status: done
plan: "plans/202610152329_specs-site-redesign/index.md"
---

# M11: Docs and a Russian fixture case

The user docs describe the redesigned site and its new flags and keys, and a Russian contract case proves `lang: ru`, Cyrillic content and a labelled tier-own type render as designed.

**Scope**: `documentation/specs.md` — `### booping specs site`: the page shell and what each page shows (home, root, type, record), the state badges, the theme toggle, the output files (`fonts.css` and licences, `site.js`, `llms.txt`, `index.json`, `.md` copies, `404.html` with `--site-url`), the new flags `--title` and `--site-url`, the config keys `core.specs.site.lang` and `core.specs.site.labels` with one example labelling a tier-own type in a project config; `### booping specs site-index`: same design; `## Publishing on GitLab Pages`: the template now passes `--site-url "$CI_PAGES_URL"`. Audience: a booping user publishing a specs site — behaviour and flags only, no internal module names (booping:rule/0008). `src/specs/README.md` line about the site rendering a type's records together: reword to the list-and-record-page reality. New e2e case `booping-python/e2e/cases/specs/site-renders-russian-labels-and-a-tier-own-type.txtar`: vault config `core.specs.site.lang: ru` with `labels.ru.types.mechanic: {name: Механика, plural: Механики, scenario: "Механики — как устроен мир"}`, a project root with a Russian value, an ADR with `values:`, one `[clarify]` and `created_by: claude`, a `_schemas/mechanic.yaml` tier type with one mechanic record; asserts full bytes of the ADR record page and the mechanic type page (`<html lang="ru">`, «Решения», «агент», the date, the clarify badge text «1 вопрос к тебе», «Механики»). Copy the `_schemas/mechanic.yaml` shape from `site-a-tier-schema-adds-the-mechanic-type.txtar`.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 11.1 | `documentation/specs.md` and the `src/specs/README.md` line. | `documentation/specs.md`, `src/specs/README.md` | 2 | done |
| 11.2 | The Russian e2e case. | `booping-python/e2e/cases/specs/site-renders-russian-labels-and-a-tier-own-type.txtar` | 1 | done |

## Definition of Done

### Task 11.1

- [x] Every flag in `booping specs site --help` and `site-index --help` is documented with its default.
- [x] No module, function or template name appears in the user docs.
- [x] `just docs` builds without warnings.

### Task 11.2

- [x] The case passes and its expected bytes were read, not only regenerated.

Return: the list of changed and created files, nothing else.

## References

- `documentation/specs.md` — the sections being updated.
- `booping-python/e2e/cases/specs/site-a-tier-schema-adds-the-mechanic-type.txtar` — tier-own type fixture shape.

## Verify

`cd booping-python && uv run pytest e2e -k russian -q`
