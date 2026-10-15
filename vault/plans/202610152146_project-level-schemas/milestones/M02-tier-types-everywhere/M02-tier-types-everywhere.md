---
id: "02"
title: "Tier types everywhere \u2014 ls, next, site, items and status read each tier\u0027s own types"
sp: 4
status: pending
plan: "plans/202610152146_project-level-schemas/index.md"
---

# M02: Tier types everywhere — ls, next, site, items and status read each tier's own types

`booping specs ls|next|site`, `booping items add|scan` and `booping status` read each tier's own type set, so a type a tier adds (`mechanic`) is listed, numbered, rendered and scanned, and a translated rule is still injected.

**Scope**: replace every tier-blind type list with the tier's map from M01: `commands/specs.py` (`_known_types` / `_format_dir` callers in `_run_ls`, `_run_next`, `_run_site`), `commands/items.py` (`_run_add`, `_run_scan` — today they import `_known_types`), `status.py` (`record_types` builds types from the plugin root directly — switch it to the project tier's map), `specs/site/model.py` `load_site` and `specs/site/pages.py` `build_site` (each `SiteRoot` gets the overlay of its own root's `_schemas/`, C3). Remove `_known_types` once nothing calls it; `_format_dir` stays only where the shipped dir is meant. `booping specs next {type}` for a type the tier does not have keeps its existing "unknown type" error, now naming the tier's types. Rule injection (`specs/rules.py`) needs no code change (C9).

Tests (integration tier, `booping-python/e2e/cases/specs/`, hand-derived): a project tier with `_schemas/mechanic.yaml` and one `mechanic/0001-*.md` record — `booping specs ls` lists `mechanic/0001`, `booping specs next mechanic` prints `mechanic/0002`, `booping specs check` passes it, `booping specs site` writes its type page; `booping specs next mechanic` in a tier without that schema exits 1 with the unknown-type error; `render-playbook` injects a targeted, `accepted` rule written under a Russian `_schemas/rule.yaml` (case under `e2e/cases/render-playbook/`).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | `ls`, `next`, `site` and the site model per tier. | `booping-python/src/booping/commands/specs.py`, `booping-python/src/booping/specs/site/model.py`, `booping-python/src/booping/specs/site/pages.py` | 2 | pending |
| 2.2 | `items add|scan` and `status` per tier. | `booping-python/src/booping/commands/items.py`, `booping-python/src/booping/status.py` | 1 | pending |
| 2.3 | The e2e cases above. | `booping-python/e2e/cases/specs/*mechanic*.txtar`, `booping-python/e2e/cases/render-playbook/*russian-rule*.txtar` | 1 | pending |

## Definition of Done

### Task 2.1

- [ ] `grep -rn "_known_types" booping-python/src` prints nothing.
- [ ] `booping specs site` renders a page for an added type and none for a type the root lacks.

### Task 2.2

- [ ] `booping status` and `booping items scan` on this repo's vault print what they printed before (no `_schemas/`).

### Task 2.3

- [ ] The cases exist and pass.

Return: the list of changed and created files, nothing else.

## References

- `booping-python/e2e/cases/specs/ls-tier-global-reads-the-home-dir-specs.txtar` — `ls` case shape.
- `booping-python/e2e/cases/render-playbook/the-rules-section-lists-one-rule-per-tier-in-core-global-project-order.txtar` — rule-injection fixture layout.

## Verify

`cd booping-python && uv run pytest e2e/cases/specs e2e/cases/render-playbook e2e/cases/status e2e/cases/items -q`
