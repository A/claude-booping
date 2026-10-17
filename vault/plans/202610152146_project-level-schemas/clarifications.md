# Clarifications

Autonomous run — the owner was unavailable; every question below was settled by the run with a default.

## C1 — where a tier's own schemas live — answered

**Asked:** 2026-10-15 — intake

**Question:** The request suggests `{tier root}/_schemas/{type}.yaml` and asks for a location that never collides with record type directories at the vault root. Which?

**Answer:**

`{tier root}/_schemas/{type}.yaml`. A type name is a schema stem — a kebab-case latin word — so a leading underscore can never name a type, and the vault already uses `_`-prefixed directories (`_playbooks/`, `_runs/`) for booping-owned non-record content, which a vault-rooted tier ignores. swarmlight's `specs/schemas/` moves to `specs/_schemas/` when it adopts the feature.

## C2 — one plan or a split — answered

**Asked:** 2026-10-15 — intake

**Question:** The request bundles per-tier schemas, the Russian set with `init --schemas ru`, a tags dictionary, ADR alternatives checks and area-file guidance. One plan or several?

**Answer:**

Decided at draft-plan against the 35 SP split threshold. The per-tier schema mechanism is the seam everything else stands on, so it is the first slice either way.

## C3 — whose schemas a tier sees — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** Do a tier's own schemas cascade (core → global → project, the way config merges), or apply to that tier only?

**Answer:**

That tier only: a tier's effective schema set is the shipped set (`{core.specs.format}/schemas/*.yaml`) overlaid by its own `{tier root}/_schemas/*.yaml` — a same stem overrides, a new stem adds a type. The request says "override the shipped schema of the same type for that tier". A cascade would let one person's Russian global set reject an English project they work on; each tier's records are written in that tier's language, so each tier is checked by its own set. The same overlay applies to every `core.specs.site.roots` entry, which is read like a tier.

## C4 — where the tags dictionary lives and what it checks — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** Where is a tier's `tags.yaml`, and what is checked against it?

**Answer:**

`{tier root}/tags.yaml` — a file, never a type (types are schema stems under `_schemas/`), and where hermes-pet and swarmlight already keep it. Shape: a mapping `{tag: one-line description}`. When the file exists, every record's optional `tags:` frontmatter list is checked: each tag matches `area[:sub]` kebab-case (`^[a-z0-9]+(-[a-z0-9]+)*(:[a-z0-9]+(-[a-z0-9]+)*)?$`), is a key of the dictionary, and a `area:sub` tag needs `area` in the dictionary too (hermes-pet's convention). Errors are check kind `tags`; a `tags.yaml` that is not a mapping of strings is one `tags` error on the file itself. No `tags.yaml` → no tag check. Whether a type requires `tags` is the schema's business (mdcheck `FRONTMATTER has`), not this check's.

## C5 — how the ADR alternatives check finds its names — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** The rows ↔ H3 and exactly-one-accepted checks must work under Russian names. Where do the names come from?

**Answer:**

From the record's effective mdcheck schema, read by booping's code — mdcheck 0.1.1 rejects any unknown key in a rule file (verified: exit 2, `unknown field`), so no booping-only key can sit there, and a sidecar would restate what the schema already says (value/0003). The check applies to every rule whose `select` is `SECTION("{name}") > TABLE` and that declares `columns:` — the section name is `{name}`, the option column is `columns[0]`, the status column is the column whose `TD[col="…"]` rule's `enum` contains `accepted`. In that section: every table row's option cell is a `[text](#anchor)` link whose anchor is the slug (the site's existing GitHub-style `slug`) of an H3 in the same section, and every such H3 is linked by exactly one row. With a status column: exactly one row `accepted` when the record's `status` is `accepted` or `superseded`, at most one otherwise (a `proposed` ADR may have none — booping's adr/0022 has none today). Errors are check kind `alternatives`. The `accepted` cell value and the statuses stay English in every set, like every value the code reads.

## C6 — a broken tier schema — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** A tier's own schema file mdcheck cannot load (exit 2) — internal error or finding?

**Answer:**

A finding: check kind `schema`, level error, path the schema file, message mdcheck's first stderr line; the records of that type are not schema-checked further in that run (one finding, not one per record); exit 1. A broken *shipped* schema stays an internal error (exit 2), as today.

## C7 — the Russian set's content — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** What exactly does `src/specs/schemas-ru/` hold?

**Answer:**

One file per shipped type (`adr`, `conflict`, `idea`, `reference`, `rule`, `runbook`, `story`, `value`) — a translation of the shipped schema with the same rules and structure, headings and bold labels from hermes-pet: `Контекст / Критерии? / Решение / Альтернативы / Последствия`, table `Вариант | Статус | Сложность | Обратимость | Вердикт`, `**Плюсы:** / **Минусы:** / **Сложность:** / **Обратимость:**`; `Правило / Следует из ценностей / Исключения?` (booping's semantics kept: an item may link any source, not only a value); `Конфликт / Решение?`; `Идея / Как проверить / Вердикт?`; `Факты / Как проверить?`; `Когда / Перед началом? / Шаги / Проверка / Откат?`; story `Как **…**, я хочу …, чтобы …` + `Критерии`; value one record per value with H2 `На практике` and `Чем жертвуем?` — booping's one-value-per-record shape, not hermes-pet's area file (request (c)). Unchanged from the shipped set: every frontmatter key, the `status`/`kind`/`created_by` enums, `summary` ≤ 200 (swarmlight's 160 is its own override), and the alternatives Статус cell enum `accepted | proposed | rejected`. Сложность/Обратимость cells take `низкая | средняя | высокая` (hermes-pet). No `mechanic` schema and no `tags.yaml` ship — those are swarmlight's own.

## C8 — `booping specs init --schemas` — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** Shape of the flag and what happens on an existing file.

**Answer:**

`booping specs init --tier global|project --schemas {set}`; a set is a `schemas-{set}` directory beside `schemas/` under `core.specs.format`, discovered, never listed in code or config (value/0003) — today `ru`. It copies every `*.yaml` of the set into `{tier root}/_schemas/` as one more planned action, after the tier's own actions, also for a vault-rooted tier (where plain `init` writes nothing). Any target file already present → stderr `error: {path} exists; init writes nothing`, exit 1, nothing written (the same all-or-nothing shape as the conflicting-link case). Unknown set → exit 1 `error: unknown schema set {set}: one of {sets}`.

## C9 — rule injection under a translated rule schema — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** The request lists rule injection among the surfaces that use the effective type set. What changes?

**Answer:**

No code: injection reads `{tier root}/rule/*.md` and the `status`/`targets`/`brief` frontmatter, all language-neutral and kept so by every set (C7). The type name `rule` cannot be renamed by a tier — an override keeps its stem. One e2e case holds it: a project tier with a Russian `_schemas/rule.yaml` and a Russian-headed targeted rule is injected by `render-playbook`.

## C10 — the area-file import guidance — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** Where does the guidance on splitting an area-file `values` record live?

**Answer:**

A new lazy-linked `docs/specs-import.md` (value/0002), reached from a new `## Import` scenario in `playbooks/specs/guide/prompt.md`: bringing existing specs from another format into a tier — copy the project's language set with `init --schemas`, split an area file into one `value` record per H3, carry `**На практике:**`/`**Чем жертвуем:**` (or the source's labels) into the record's sections, keep numbering by `booping specs next`, rewrite links, run `booping specs check`. Which value is one value, and wording, stay the model's judgement with the owner; no schema for the area form. The `Init` scenario names `--schemas` for a project writing in another language. The step's committed report drifts — accepted under the owner's snapshot policy as plan-described.

## C11 — `_`-prefixed directories in a tier — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** A tier not rooted at the vault walks every directory as a type; `_schemas/` would be one.

**Answer:**

A directory whose name starts with `_` is never a record directory in any tier — `load_tier` skips it, so `_schemas/` raises no `layout` error. `tags.yaml` at the root is already ignored (strays are `*.md` only).

## C12 — record the location choice — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** The request says "record the choice" of location.

**Answer:**

In the format guide `src/specs/README.md` (the tier's file layout, the single source the docs link) and here (C1). No new ADR: the choice has no real alternative left once the type namespace is the schema stems (an ADR needs one).

## C13 — one plan — answered

**Asked:** 2026-10-15 — draft-plan

**Question:** Split (C2)?

**Answer:**

No: the estimate is 26 SP, under the 35 SP threshold, so the whole request is one plan.

## C14 — review gates — answered

**Asked:** 2026-10-15 — intake, present

**Question:** Intake's scope gate and present's approval gate need the owner.

**Answer:**

Auto-confirmed by the run under the session's autonomous directive: intake's framing stood as written (no change to type, problem or boundary); the cross-review (codex) returned no findings; present's approval was given by the run, moving the plan to `ready-for-dev`. The owner reviews the plan before or during develop.

## C-owner — structural headings — answered

**Asked:** 2026-10-15 — owner, during develop

**Question:** Translated schema sets for projects writing in Russian?

**Answer:** No. Structural headings, labels, table columns and frontmatter keys stay the shipped English ones in every tier; content may be in any language. M05 now states that rule, M06 (init --schemas) is removed, M07's import guidance renames headings instead. A tier's own schemas stay for its own types and fields (M01-M04 unchanged).
