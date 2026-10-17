---
id: "04"
title: "A vault-rooted tier reads only type directories"
sp: 4
status: done
plan: "plans/202610151727_project-specs-at-vault-root/index.md"
---

# M04: A vault-rooted tier reads only type directories

When the project tier root is the vault, loading and `specs check` read only directories named after a known type and skip every other vault directory and root-level file; a tier with its own root — core, global, a repo-pointed project tier — still reports unknown directories and stray root files as `layout` errors.

**Scope**: `booping-python/src/booping/specs/tiers.py` gives the project `Tier` a `vault_rooted` flag, true when its root resolves to the vault directory. `booping-python/src/booping/specs/records.py` `load_tier()` skips non-type directories when the flag is set; `booping-python/src/booping/specs/check.py` `check_tier()` skips the root-level stray scan when it is set. Known types stay the schema stems. Every consumer of `load_tier` / `check_tier` — `specs ls`, `next`, `check`, `site`, `open-items scan` — inherits it; `rules.py` reads `{root}/rule` and is untouched.

Tests: integration tier, txtar. New `booping-python/e2e/cases/specs/check-a-vault-rooted-tier-ignores-non-type-directories.txtar` — a default-tier vault holding `plans/p/index.md`, `retrospectives/r.md`, `open-items/OI-0001.md`, `notes/n.md`, `sprints.md`, `README.md` and one valid `value/0001-x.md`: `specs check --tier project` exits 0 with no finding. New `ls-a-vault-rooted-tier-lists-only-records.txtar` — the same vault: `specs ls --tier project` lists the one value. `check-layout-unknown-type-directory.txtar` and `check-layout-stray-file-at-the-root.txtar` set an explicit repo `core.specs.tiers.project.path` in their vault config and keep their expected `layout` errors unchanged. Expected output hand-written.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | `vault_rooted` flag; loader and check honour it. | `booping-python/src/booping/specs/tiers.py`, `booping-python/src/booping/specs/records.py`, `booping-python/src/booping/specs/check.py` | 2 | done |
| 4.2 | The two new cases; the two layout cases pinned to a repo tier. | `booping-python/e2e/cases/specs/check-a-vault-rooted-tier-ignores-non-type-directories.txtar`, `booping-python/e2e/cases/specs/ls-a-vault-rooted-tier-lists-only-records.txtar`, `booping-python/e2e/cases/specs/check-layout-unknown-type-directory.txtar`, `booping-python/e2e/cases/specs/check-layout-stray-file-at-the-root.txtar` | 2 | done |

## Definition of Done

### Task 4.1

- [x] A vault-rooted tier yields no `layout` finding for any non-type directory or root-level file.
- [x] A non-vault-rooted tier reports unknown directories and stray root files exactly as before.

### Task 4.2

- [x] Each case in Tests exists and passes; the two layout cases' expected stdout is byte-identical to before.

Return: the list of changed files, nothing else.

## References

- `booping-python/e2e/cases/specs/check-layout-unknown-type-directory.txtar` — case shape.
- `src/specs/README.md` `## Check` — the finding names.

## Verify

`just e2e -k 'check-layout or vault-rooted'`
