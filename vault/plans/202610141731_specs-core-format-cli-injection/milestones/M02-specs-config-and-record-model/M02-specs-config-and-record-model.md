---
id: "02"
title: "Specs tier config and record model"
sp: 7
status: pending
plan: "plans/202610141731_specs-core-format-cli-injection/index.md"
---

# M02: Specs tier config and record model

Config names each tier's specs root and namespace under `core.specs`, and a `booping.specs` package resolves the three tiers and loads their records — the model every `booping specs` verb (M03–M05) and the sibling plan's rule injection build on.

**Scope**: `src/config.yaml` gains the `core.specs` block exactly as in the plan's Decisions → Config shape, commented like its neighbours. New package `booping-python/src/booping/specs/` with `tiers.py` and `records.py`; no CLI yet. Tier anchors: core → plugin root (`rendering.get_plugin_root()`), global → `home_dir` from the core+global merge (as `Context.assemble()` resolves it), project → the attached project's repo directory. The project tier's null `path` resolves to `{vault}/specs` when the vault directory is inside the repo directory, else `{repo}/specs`. A null global namespace reads the `USER` environment variable. With an explicit vault override (`--project`) the global tier is absent. No project attached → the project tier is absent. Tests: unit tests for the pure logic only — `parse_filename`, `parse_ref` (parametrized: plain, namespaced, malformed, wrong width), project-path resolution (vault inside / outside the repo, explicit path, absolute path); the tier resolution end to end is covered by M03's e2e cases.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Add `core.specs` (`format`, `tiers.core`, `tiers.global`, `tiers.project`) to `src/config.yaml` with one comment line per key naming its base directory and null semantics. | `src/config.yaml` | 1 | pending |
| 2.2 | `booping/specs/tiers.py`: `Tier(name, namespace, root, anchor)` and `resolve_tiers(...) -> list[Tier]` ordered core, global, project, implementing the anchors, path bases (relative → tier anchor, absolute or `~` → as is), project null-path rule, `$USER` fallback and hermetic drop described in Scope; `types(format_dir) -> list[str]` from `schemas/*.yaml` stems, sorted. | `booping-python/src/booping/specs/__init__.py`, `booping-python/src/booping/specs/tiers.py` | 3 | pending |
| 2.3 | `booping/specs/records.py`: `parse_filename(name) -> (number, slug) | None` (`^\d{4}-[a-z0-9]+(-[a-z0-9]+)*\.md$`), `parse_ref(text) -> Ref(namespace, type, number) | None` (`[{ns}:]{type}/{NNNN}`), `Record(type, number, slug, path, frontmatter, body, frontmatter_error)` and `load_tier(tier, types) -> list[Record]` reading every `*.md` under `{root}/{dir}/` for every directory under the root (an unknown directory still loads, so check can report it), skipping the root's own `README.md`; frontmatter via the existing `booping.context._yaml` helper, a YAML error captured on the record, not raised. Unit tests per Scope. | `booping-python/src/booping/specs/records.py`, `booping-python/tests/specs/__init__.py`, `booping-python/tests/specs/records_test.py`, `booping-python/tests/specs/tiers_test.py` | 3 | pending |

## Definition of Done

### Task 2.1

- [ ] `bin/booping config-get core.specs` prints the block with the defaults from the plan's Decisions.
- [ ] `just snapshots` reports no drift caused by the new key.

### Task 2.2

- [ ] `resolve_tiers` returns core with namespace `booping` and root `{plugin root}/vault/specs`; global with root `{home_dir}/_specs` and namespace `$USER` when unset; project per the null-path rule.
- [ ] With a vault override the global tier is absent; with no project the project tier is absent.
- [ ] `types()` returns the eight shipped type names, sorted, read from `src/specs/schemas/`.

### Task 2.3

- [ ] `parse_ref("booping:rule/0003")` → namespace `booping`, type `rule`, number 3; `parse_ref("rule/0003")` → namespace None; `parse_ref("rule/3")`, `parse_ref("rule")`, `parse_ref(":rule/0003")` → None.
- [ ] A record with broken YAML loads with `frontmatter_error` set and empty `frontmatter`.
- [ ] `uv run pytest tests/specs` passes in `booping-python/`.

Return: the list of changed files, nothing else.

## References

- `booping-python/src/booping/context/lesson.py` — shape of a loader over a tier directory and the target parser M04 reuses.
- `booping-python/src/booping/context/__init__.py` — how `home_dir`, the vault and the hermetic override are resolved in `Context.assemble()`.
- `booping-python/tests/context/lesson_test.py` — unit test style.
- Format spec: `src/specs/README.md` (from M01).

## Verify

```
cd booping-python && uv run pytest tests/specs -q
```

All pass.
