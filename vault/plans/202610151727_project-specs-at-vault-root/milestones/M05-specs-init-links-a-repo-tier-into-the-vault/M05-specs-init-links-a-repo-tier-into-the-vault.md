---
id: "05"
title: "specs init \u2014 nothing at the vault root, a repo tier linked into the vault"
sp: 4
status: pending
plan: "plans/202610151727_project-specs-at-vault-root/index.md"
---

# M05: specs init — nothing at the vault root, a repo tier linked into the vault

`booping specs init --tier project` with the default tier creates nothing and prints the vault root; with a tier root outside the vault it creates the directory and its README and links `{vault}/specs` to it — the setup playbook's step 7 provisions both through it unchanged.

**Scope**: `booping-python/src/booping/specs/init.py` `plan()`. Vault-rooted tier (M04's flag) → no action at all; stdout is the absolute root alone. Tier root not inside the vault → the missing directories and `README.md` as today, plus the `{vault}/specs` link, whether the vault sits in the repo or not. Tier root inside the vault but not the vault itself (an explicit path into it) → directories and README, no link. The existing refusals stay: `{vault}/specs` a symlink pointing elsewhere, or a non-symlink, raises before anything is written. Output stays one action line per change, then the absolute tier root as the last line (migration 004 reads it with `tail -n 1`). `PROJECT_README` loses any sentence placing the tier at `{vault}/specs` by default. The global tier is untouched.

Tests: integration tier, txtar, under `booping-python/e2e/cases/specs/`:

| Case | Change |
|------|--------|
| `init-project-tier-in-repo-vault-creates-vault-specs.txtar` | renamed `init-project-tier-default-is-the-vault-root-and-creates-nothing.txtar`, rewritten |
| `init-project-tier-default-outside-the-repo-creates-nothing.txtar` | new |
| `init-project-tier-outside-vault-creates-repo-specs-and-links-it.txtar` | pinned `path: specs` |
| `init-a-repo-tier-beside-an-in-repo-vault-is-linked.txtar` | new |
| `init-a-conflicting-vault-specs-writes-nothing.txtar`, `init-an-existing-readme-is-left-byte-identical.txtar`, `init-a-second-run-changes-nothing.txtar` | pinned to an explicit `path` where they need a root of their own |

`init-project-tier-in-repo-vault-creates-vault-specs.txtar` becomes `init-project-tier-default-is-the-vault-root-and-creates-nothing.txtar` — in-repo vault, null path: stdout is the vault root alone, no file created. New `init-project-tier-default-outside-the-repo-creates-nothing.txtar` — the same for a vault outside the repo. `init-project-tier-outside-vault-creates-repo-specs-and-links-it.txtar` keeps its subject with `core.specs.tiers.project.path: specs` set in the vault config. New `init-a-repo-tier-beside-an-in-repo-vault-is-linked.txtar` — vault in the repo, `path: specs`: creates `specs/`, its README and the `vault/specs` link. `init-a-conflicting-vault-specs-writes-nothing.txtar`, `init-an-existing-readme-is-left-byte-identical.txtar` and `init-a-second-run-changes-nothing.txtar` take an explicit `path` where they need a root of their own. Expected output hand-written.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | `plan()` per Scope; `PROJECT_README` wording. | `booping-python/src/booping/specs/init.py` | 2 | pending |
| 5.2 | The renamed, new and pinned cases in Tests. | `booping-python/e2e/cases/specs/init-*.txtar` | 2 | pending |

## Definition of Done

### Task 5.1

- [ ] Default tier: exit 0, stdout the vault root alone, nothing written.
- [ ] A tier root outside the vault: `{vault}/specs` links to it, in either vault placement.
- [ ] A refused `{vault}/specs` exits non-zero with its stderr message and writes nothing.

### Task 5.2

- [ ] Every case in Tests exists and passes; no `init-*` case seeds `vault/specs/` as the default tier.

Return: the list of changed files, nothing else.

## References

- `booping-python/e2e/cases/specs/init-project-tier-outside-vault-creates-repo-specs-and-links-it.txtar` — link case shape.
- `playbooks/setup/setup-project/opus-5.md` step 7 — the caller and its expected output.

## Verify

`just e2e -k init-`
