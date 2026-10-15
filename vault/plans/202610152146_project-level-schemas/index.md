---
title: "Project-level schemas — tiers carry their own mdcheck schemas, tags dictionary,
  ADR alternatives checks, Russian set"
type: "feature"
status: in-progress
sp: 26
related_to: null
created: 2026-10-15 21:46
planned: null
started: 2026-10-15 22:11
completed: null
code_reviews: []
sessions:
- 2740a7e8-9ead-4aa2-92ad-5cf9208bef05
- f2280e4c-6a1f-4aa5-992a-85b25a75da65
retro: null
summary: A tier carries its own mdcheck schemas (override, add types), tags 
  dictionary, ADR alternatives checks, Russian set via init --schemas
commit: 7959557867b9f7f928ab95e408f1c22ed124b7dc
tracker_provider: null
tracker_request: null
tracker_issue: null
return_to: null
agents:
  research-codebase: a27f2a0098a805df6
  research-web: a0afe17b358721481
  cross-review: a7c243a8562aa2c3f
reviewed_at: 2026-10-15 22:01
---

# Project-level schemas — tiers carry their own mdcheck schemas, tags dictionary, ADR alternatives checks, Russian set

## Context

`booping specs` checks every tier — core, global, project — against the one shipped schema set (`core.specs.format` → `src/specs/schemas/{type}.yaml`); the record types are its stems, identical for every tier, and every surface (`specs ls|next|check|site`, `items add|scan`, `status`) builds that list once, tier-blind. A project writing its records in Russian, or carrying a type booping does not ship (`mechanic`), cannot pass `check` and cannot be listed, numbered or sited — against [adr/0001](../../adr/0001-specs-tiers.md) and [value/0005](../../value/0005-stack-agnostic-core.md), which say a tier adds and overrides. After this plan:

- A tier carries its own mdcheck schemas at `{tier root}/_schemas/{type}.yaml`: a same stem overrides the shipped shape for that tier, a new stem adds a type; every `booping specs` surface, `items add|scan` and `status` read the tier's effective set; rule injection keeps working under a translated rule schema.
- A tier with `{tier root}/tags.yaml` has every record's `tags:` checked against that dictionary.
- `check` verifies an ADR's alternatives across the file — table rows ↔ `###` blocks, exactly one `accepted` — under the section and column names the record's schema declares, so a translated set gets the same check.
- booping ships `src/specs/schemas-ru/`; `booping specs init --schemas ru` copies it into a tier; the specs playbook guides importing existing specs, including splitting an area-file `values` record into one record per value.

Frontmatter keys and the values code reads stay English in every set.

## Decisions

> Owner decision 2026-10-15 (C-owner) supersedes every Russian-set and `init --schemas` line below: structural headings stay English in every tier; M05 states that rule, M06 is removed, M07 guides a heading rename.

- **Location**: `{tier root}/_schemas/{type}.yaml`; `_`-prefixed directories are never record directories — C1, C11, C12.
- **Overlay**: per tier, shipped ∪ own, no cascade between tiers; site roots read like tiers — C3.
- **Tags**: `{tier root}/tags.yaml`, `area[:sub]` kebab-case, area must exist for a sub; check kind `tags` — C4.
- **Alternatives**: names derived from the record's effective schema (`SECTION("…") > TABLE` with `columns:`; status column = the `TD` rule whose enum holds `accepted`); exactly one accepted for `accepted`/`superseded`, at most one otherwise; check kind `alternatives` — C5.
- **Broken tier schema**: one `schema` finding on the schema file, exit 1; broken shipped schema stays exit 2 — C6.
- **Russian set**: a translation of all eight shipped schemas, frontmatter and status cells untouched, one value per record — C7.
- **`init --schemas SET`**: sets discovered as `schemas-*` beside `schemas/`; all-or-nothing on existing files — C8.
- **Rule injection**: no code change, one e2e case holds it — C9.
- **Area-file import**: guidance in `docs/specs-import.md` behind an `Import` scenario; judgement stays with the model — C10.
- **One plan**: 26 SP — C13.
- **External references**: mdcheck (`markdown-checker` 0.1.1, the version `just mdcheck` installs) checked locally on 2026-10-15 — rule-file keys are exactly `doc` and `rules`; an unknown key, top-level or nested, is exit 2 `unknown field`. That is why the alternatives names are derived from existing rule literals, not a booping key in the rule file.

### Values in play

- [value/0005 Stack-agnostic core](../../value/0005-stack-agnostic-core.md) / [value/0006 A constructor](../../value/0006-a-constructor-not-a-fixed-solution.md) — the core ships the English and Russian sets as examples; a tier's language and extra types are the tier's own files.
- [value/0003 Single source](../../value/0003-single-source.md) — the schema is the one source of a type's names: the alternatives check reads them from it, schema sets are discovered from directories, not listed.
- [value/0015 Deterministic where it can be](../../value/0015-deterministic-where-it-can-be.md) — tags and alternatives become code checks; only splitting an area file into values stays the model's judgement.
- [value/0010 Proven to work](../../value/0010-proven-to-work.md) — every new check, the overlay, the extra type, rule injection and `init --schemas` are held by e2e cases; a stem-parity test keeps the Russian set complete.
- [value/0002 Minimal effective context](../../value/0002-minimal-effective-context.md) — the import guidance is a lazy-linked doc, the scenario two lines.

### Departures

- [rule/0013](../../rule/0013-snapshot-baselines-accepted-by-user.md): the develop run accepts the plan-described snapshot drift (`playbooks/specs/_reports/output.md`, M07) under the owner's standing permission for this feature (2026-10-14), listing it in `develop-defaults.md`.
- The request's reference set (hermes-pet) uses an area-file `values` type and `summary` ≤ 160; the Russian set keeps booping's one-value `value` type and ≤ 200 (C7, request (c)).

## Architecture

```
resolve_tiers ─► Tier{root, …, schemas: {stem → path}}   shipped {format}/schemas/*.yaml  ⊕  {root}/_schemas/*.yaml
                     │
   ┌─────────────────┼───────────────────────────────┬──────────────────────┐
specs ls|next|site   specs check                      items add|scan, status  render-playbook rules (unchanged: rule/, neutral frontmatter)
(tier.types)          ├─ mdcheck {tier schema} per record   (tier.types)
                      ├─ tags.py      ◄─ {root}/tags.yaml
                      └─ alternatives.py ◄─ names read from the record's schema
specs init --schemas SET ─► copy {format}/schemas-SET/*.yaml → {root}/_schemas/
```

- `specs/tiers.py` — the overlay, on `Tier`; `specs/records.py` — `_`-prefixed dirs skipped.
- `specs/check.py` — per-tier schema path, tier-schema load failure, calls `tags.py` and `alternatives.py` (new).
- `commands/specs.py`, `commands/items.py`, `status.py`, `specs/site/{model,pages}.py` — tier types instead of the tier-blind list.
- `specs/init.py` + `commands/specs.py` — `--schemas`.
- `src/specs/schemas-ru/` (new), `docs/specs-import.md` (new), `playbooks/specs/guide/prompt.md`.

## Milestones

| id | title | sp | status |
| --- | --- | --- | --- |
| 01 | [Tier schemas — each tier's effective schema set, used by booping specs check](milestones/M01-tier-schemas-in-check/M01-tier-schemas-in-check.md) | 4 | in-progress |
| 02 | [Tier types everywhere — ls, next, site, items and status read each tier's own types](milestones/M02-tier-types-everywhere/M02-tier-types-everywhere.md) | 4 | in-progress |
| 03 | [Tags dictionary — record tags checked against the tier's tags.yaml](milestones/M03-tags-dictionary/M03-tags-dictionary.md) | 3 | in-progress |
| 04 | [Alternatives check — table rows match H3 options, one accepted, names from the schema](milestones/M04-alternatives-check/M04-alternatives-check.md) | 4 | in-progress |
| 05 | [Structural headings are English in every tier](milestones/M05-russian-schema-set/M05-russian-schema-set.md) | 3 | pending |
| 06 | [(removed) init --schemas](milestones/M06-init-schemas/M06-init-schemas.md) | 3 | pending |
| 07 | [Specs import guidance — init with a language set, splitting an area file into value records](milestones/M07-import-guidance/M07-import-guidance.md) | 2 | pending |
| 08 | [Documentation — format guide, specs docs, config reference and CLAUDE.md for tier schemas](milestones/M08-docs/M08-docs.md) | 3 | pending |

## I/O contract

- **`booping specs check [--tier core|global|project]`** — unchanged shape: one line per finding, `{path}:{line}  {level}  {check}  {message}`; exit 0 clean (warnings only), 1 any error, 2 internal error. New check kinds, level error:
  - `schema` on a tier schema file: `{root}/_schemas/{type}.yaml:1  error  schema  {mdcheck's first stderr line}`.
  - `tags`: `tag {t} is not area[:sub] kebab-case` · `tag {t} is not in tags.yaml` · `tag {t} needs its area {a} in tags.yaml` · on `tags.yaml` itself `tags.yaml must map each tag to a one-line description` · on a record `tags must be a list of strings`.
  - `alternatives`: `option {anchor} names no ### in {name}` · `### {heading} has no row in {name}` · `### {heading} has {n} rows in {name}` · `{n} options accepted in {name}; a {status} record needs exactly one` · `{n} options accepted in {name}; at most one`.
- **`booping specs ls|next|site`** — unchanged output; the type set is the tier's. `next {type}` for a type the tier lacks: the existing unknown-type error, exit 1.
- **`booping specs init --tier global|project [--schemas SET]`** — stdout `created dir {path}` / `created file {path}` per action, the set's files last; errors on stderr, exit 1, nothing written: `error: {path} exists; init writes nothing`, `error: unknown schema set {set}: one of {sets}`.
- **Tier files** — `{tier root}/_schemas/{type}.yaml` (mdcheck 0.1.1 rule file), `{tier root}/tags.yaml` (mapping `tag: description`).

## Final Verification

- [ ] `just ci` green, run to completion.
- [ ] `just snapshots` drift only in `playbooks/specs/_reports/output.md` (the guide step's `Import` scenario and `Init` sentence); accepted per the owner's snapshot policy and listed in `develop-defaults.md`.
- [ ] `bin/booping specs init --help` names no `--schemas` option (owner decision 2026-10-15, C-owner: no Russian set, no `init --schemas`; M05–M07 amended).
- [ ] `just specs-check` green on this repo — both tiers, with the new `tags` and `alternatives` checks active.

## Out of scope

- A cascade of tier schemas (global → project) — C3.
- A schema for hermes-pet's area-file `values` form — request (c).
- Migrating swarmlight or hermes-pet; a `mechanic` schema or a `tags.yaml` shipped by booping.
- Anchor resolution for links outside the alternatives table (the existing `link` check stays file-level).
- Re-running the specs/guide eval suite (owner-run, subscription auth).

## CLAUDE.md impact

`## Config` `core.specs` line (types per tier, `_schemas/` overlay) and `## Layout` `src/specs/` line (`schemas-{lang}/` sets) — M08.
