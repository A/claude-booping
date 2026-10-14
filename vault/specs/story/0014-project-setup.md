---
type: story
title: Project setup
summary: The setup playbook takes a repo from any state to a working booping project and re-runs without changing what is already set up.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: done
sources: [vault/docs/_specs/features.md]
---

As **a user**, I want one playbook that takes my repo from any state to a working booping
project, so that I can start the loop without wiring anything by hand.

## Criteria

- Resolves and writes machine-level config with a working `home_dir`.
- Scaffolds the Project Vault from the config-declared tree, including `sprints.md` as
  a live Obsidian Bases view seeded once, never regenerated.
- Writes the marker to attach the repo (`vault_path:` for a repo-local vault) and
  symlinks a repo-local vault into the home dir for Obsidian.
- Seeds a fresh Project Vault at the highest shipped migration id, so no migration is
  pending.
- Detects phases already satisfied and skips them, so a re-run reports state instead
  of changing it.
