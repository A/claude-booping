---
id: "05"
title: "One directory as core and project tier injects each rule once"
sp: 2
status: done
plan: "vault/plans/202610150110_lessons-migration-rule-only-injection/index.md"
---

# M05: One directory as core and project tier injects each rule once

An e2e case proves that when the core and the project tier resolve to one directory — booping's own repo, where the vault is in the plugin root and `vault/specs` is both — a targeted rule injects once, as `booping:rule/NNNN`.

**Scope**: one new txtar case under `booping-python/e2e/cases/render-playbook/` whose fixture plugin root holds an in-repo vault with `vault/specs/rule/0001-*.md` (accepted, targeted at the fixture playbook), `core.specs.tiers.core.path: vault/specs` and project `path: null`, so both tiers resolve to the same absolute directory through `resolve_tiers()`, not a synthetic `Tier`. Asserts: the `## Rules` section lists the rule once, its ref is `booping:rule/0001`, and the count sentence says 1. A second case: `booping specs ls --tier project` and `--tier core` both list the record — one directory, two tiers. No code change expected; if the case fails, the dedup in `booping-python/src/booping/specs/rules.py` (`load_targeted_rules`, `seen` by resolved path) is the place to fix.

Tests: this milestone is the test — integration tier, against the real config merge.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | The render case and the `specs ls` case, expected output hand-written. | `booping-python/e2e/cases/render-playbook/a-directory-that-is-core-and-project-tier-injects-each-rule-once.txtar`, `booping-python/e2e/cases/specs/ls-core-and-project-on-one-directory-list-the-same-records.txtar` | 2 | done |

## Definition of Done

### Task 5.1

- [x] The render fixture reaches the shared directory through the plugin root and the vault's own config, never by stubbing tiers.
- [x] The rendered rule appears exactly once, ref `booping:rule/0001`.
- [x] Mutating `load_targeted_rules` to skip the `seen` check makes the render case fail (checked once by hand, reverted).

Return: the list of changed files, nothing else.

## References

- `booping-python/e2e/cases/specs/check-namespace-core-ref-resolves.txtar` — how a case sets up a core tier under a fixture plugin root.
- `booping-python/tests/specs/rules_test.py` — `test_shared_directory_yields_each_rule_once_with_first_tier`, the unit-level statement of the same behaviour.

## Verify

`just e2e -k "core and project"`
