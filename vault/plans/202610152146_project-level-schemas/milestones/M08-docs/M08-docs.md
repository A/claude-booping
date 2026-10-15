---
id: "08"
title: "Documentation \u2014 format guide, specs docs, config reference and CLAUDE.md for tier schemas"
sp: 3
status: pending
plan: "plans/202610152146_project-level-schemas/index.md"
---

# M08: Documentation — format guide, specs docs, config reference and CLAUDE.md for tier schemas

The format guide, the public docs, the config reference and `CLAUDE.md` describe tier schemas, the tags dictionary, the alternatives check and the Russian set.

**Scope**: `src/specs/README.md` — `## Tiers` or a new `## Tier schemas` section: `{tier root}/_schemas/{type}.yaml` overrides the shipped schema for that tier and adds types, no cascade between tiers (C3), why the underscore (C1/C12); `{tier root}/tags.yaml` and the `tags:` field (C4); language-neutral frontmatter keys and values a set may never translate (`type`, `status`, `kind`, `targets`, `brief`, `values`, `rules`, `supersedes`, `sources`, `reviewed`, `created_by`, the alternatives status cell); `## Check` lists `tags` and `alternatives`; the shipped sets (`schemas-ru`) and `init --schemas`. `documentation/specs.md` — the type list stops being a fixed eight (types = the tier's effective schema stems), `specs check` kinds, `specs init --schemas`, a short tier-schemas and tags section. `documentation/project_config.md` `core.specs.format` — types are per tier: the shipped stems plus the tier's `_schemas/`. `CLAUDE.md` — the `core.specs` line (`types = schema stems` → per tier) and the `src/specs/` layout line (`schemas-{lang}/`). Audience filter (booping:rule/0008): user docs say what a project author touches — files, flags, errors — no internal module names.

Tests: none — prose; `just mdcheck` and `just docs` hold the structure.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 8.1 | Format guide. | `src/specs/README.md` | 1 | pending |
| 8.2 | Public docs and config reference. | `documentation/specs.md`, `documentation/project_config.md` | 1 | pending |
| 8.3 | `CLAUDE.md` lines. | `CLAUDE.md` | 1 | pending |

## Definition of Done

### Task 8.1

- [ ] README states the location, the overlay, the no-cascade rule, the tags dictionary, the neutral keys, both new check kinds and `--schemas`.

### Task 8.2

- [ ] `grep -n "value/, rule/, adr/, conflict/, story/, idea/, reference/, runbook/" documentation/specs.md` no longer presents the eight as the closed set.
- [ ] No internal module path appears in `documentation/`.

### Task 8.3

- [ ] `CLAUDE.md`'s `core.specs` and `src/specs/` lines name per-tier types and `schemas-{lang}/`.

Return: the list of changed and created files, nothing else.

## References

- `src/specs/README.md` — the format guide's own voice.
- `documentation/specs.md` — current public page.

## Verify

`just docs`
