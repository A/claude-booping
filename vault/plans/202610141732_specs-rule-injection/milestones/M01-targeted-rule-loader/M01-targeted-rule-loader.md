---
id: "01"
title: "Targeted rule loader across the three tiers"
sp: 7
status: done
plan: "vault/plans/202610141732_specs-rule-injection/index.md"
---

# M01: Targeted rule loader across the three tiers

Every `Context.assemble()` carries `targeted_rules` — each `status: accepted` rule with `targets:` and `brief:` from the core, global and project specs tiers, deduplicated by realpath — and `rule_skips` for the targeted rules it could not take.

**Scope**: new module `booping-python/src/booping/specs/rules.py`; `booping-python/src/booping/context/__init__.py` (`Context` fields + `assemble`). No render surface changes here — M02 and M03 consume the two fields. Callers unaffected: every existing render ignores the new fields until then.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | `TargetedRule` model and `load_targeted_rules(tiers)` — reads only each tier's `rule/` directory through `load_record`, filters, parses targets, builds ref, brief and link, dedupes by realpath | `booping-python/src/booping/specs/rules.py` | 3 | done |
| 1.2 | Wire into `Context.assemble`: resolve tiers with `resolve_tiers` from the merged config, `home_dir`, the project's `repo_directory`, the vault and `vault_override is not None`; set `targeted_rules` and `rule_skips` | `booping-python/src/booping/context/__init__.py` | 2 | done |
| 1.3 | Unit tests for the loader and the assemble wiring | `booping-python/tests/specs/rules_test.py`, `booping-python/tests/context/assemble_test.py` | 2 | done |

Model and behaviour (locked in [clarifications.md](../../clarifications.md) C1–C3, C6):

- `TargetedRule` fields: `ref` (str), `title` (str), `brief` (str, whitespace collapsed to single spaces), `link` (str), `tier` (`TierName`), `path` (Path, the record file), `parsed_targets` (`list[LessonTarget]` from `booping.context.lesson.parse_target`). `RuleSkip` fields: `path` (Path), `reason` (str).
- Considered: records under `{tier.root}/rule/*.md` only. A record with `status` other than `accepted` is ignored silently. An accepted record with neither `targets` nor `brief` is ignored silently (documentation-only rule).
- Skipped with a `RuleSkip`: a `frontmatter_error` (reason = that error); `targets` present without a non-empty string `brief`, or `brief` without a non-empty `targets` list (reason `targets and brief must come together`); any target entry `parse_target` rejects (reason `target {entry!r}: {rejection.reason}`).
- `ref`: `{tier.namespace}:rule/{NNNN}` when the tier has a namespace, else `rule/{NNNN}`; `NNNN` zero-padded to four digits from `Record.number`. A record whose filename has no number is skipped with reason `filename is not NNNN-slug.md`.
- `link`: core → `${CLAUDE_PLUGIN_ROOT}/{path relative to tier.anchor}`; project → the path relative to `tier.anchor` (the repo root); global, and any core or project record outside its anchor → the absolute path. Always POSIX separators.
- Order: tiers in `resolve_tiers` order (core, global, project), records within a tier by number. Dedupe: a record whose `path.resolve()` was already taken is dropped — the first tier wins.
- Missing tier root → no rules from that tier, no skip.

## Definition of Done

### Task 1.1

- [x] `load_targeted_rules` returns `(list[TargetedRule], list[RuleSkip])` in the order and with the ref, link and brief forms above.
- [x] Retired, untargeted and non-rule records never appear in either list.
- [x] Function is pure over the tiers passed in — no config or environment reads.

### Task 1.2

- [x] `Context.targeted_rules` and `Context.rule_skips` default to empty lists and are filled by `assemble`.
- [x] With `vault_override` set, no global-tier rule is loaded (the tier is absent from `resolve_tiers`); core and project still load.
- [x] With no attached project, core and global rules still load.

### Task 1.3

- [x] Tests build real tier directories under `tmp_path` and pass `Tier` objects to the loader — no mocks.
- [x] Parametrized over the skip reasons: frontmatter error, targets without brief, brief without targets, unparseable target, numberless filename.
- [x] Cover: retired and untargeted rules absent; core/global/project ref and link forms, including `${CLAUDE_PLUGIN_ROOT}/vault/specs/rule/0004-x.md` for a core record under the anchor; a core record outside its anchor gets an absolute link; core and project tiers on one directory yield each rule once with the core ref; tier then number order; multi-line brief collapsed.
- [x] `assemble_test.py`: a vault override drops a global-tier rule present under the fixture home; an un-pinned assemble loads it.
- [x] Expected values are literals in the test, not derived from the loader.

## References

- `booping-python/src/booping/context/lesson.py` — `parse_target`, `LessonTarget`, `load_targeted`: the loader shape to mirror.
- `booping-python/src/booping/specs/records.py`, `booping-python/src/booping/specs/tiers.py` — `load_record`, `Tier`, `resolve_tiers` to reuse; `booping-python/src/booping/commands/specs.py` `_resolve` shows the `resolve_tiers` call.
- `booping-python/src/booping/context/review_template.py` — the core-relative `${CLAUDE_PLUGIN_ROOT}` link precedent; `booping-python/tests/specs/tiers_test.py` — test shape.

## Verify

`uv run --project booping-python pytest booping-python/tests/specs/rules_test.py booping-python/tests/context/assemble_test.py -q` — all pass.

Return: only the list of changed files, then the last line of the Verify output.
