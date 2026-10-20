---
type: story
title: Project setup
summary: The setup playbook takes a repo from any state to a working booping project and re-runs without changing what is already set up.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-20
status: done
priority: P0
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/features.md]
---

As **a user**, I want one playbook that takes my repo from any state to a working booping
project, so that I can start the loop without wiring anything by hand.

## Scenarios

1. The user runs `/playbook setup` in a repo with nothing set up yet.
2. The playbook settles the machine level first: it resolves the home dir and writes the
   machine-level config.
3. It then settles the project level: it asks for the vault location — the default under
   the home dir or a repo-local directory — creates the Project Vault from the
   config-declared tree, and writes the `.booping` marker that attaches the repo.
4. The user runs `/playbook` in the same repo and sees the shipped playbooks listed with
   no STOP notice, ready for a first groom.

Re-running: the user runs `/playbook setup` again on a wired-up project; every phase is
detected as satisfied and the run reports the state instead of changing it.

## Edge cases

- A repo-local vault: the marker carries `vault_path:` and the vault is symlinked into the home dir for Obsidian.
- A fresh vault starts at the highest shipped migration id, so no migration notice appears on the first render.
- `sprints.md` already exists: it is never regenerated, the seeded view stays the user's.

## Criteria

- Resolves and writes machine-level config with a working `home_dir`.
- Creates the Project Vault from the config-declared tree, including `sprints.md` as
  a live Obsidian Bases view seeded once, never regenerated.
- Writes the marker to attach the repo (`vault_path:` for a repo-local vault) and
  symlinks a repo-local vault into the home dir for Obsidian.
- Seeds a fresh Project Vault at the highest shipped migration id, so no migration is
  pending.
- Detects phases already satisfied and skips them, so a re-run reports state instead
  of changing it.
