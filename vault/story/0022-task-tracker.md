---
type: story
title: Task tracker
summary: The booping-tracker CLI carries every interaction with an issue tracker, and groom mirrors its run status and questions onto the tracker issue.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: done
sources: [booping-tracker/README.md, src/config.yaml, playbooks/groom/playbook.yaml]
---

As **an advanced user**, I want my runs mirrored onto my issue tracker, so that the
tracker shows where a plan stands without me copying it by hand.

## Criteria

- `bin/booping-tracker` is the only path from playbooks and hook scripts to a tracker,
  with the verbs `states`, `show`, `comment`, `issue-create`, `issue-update`, `relate`
  and `sync`; `--dry-run` reaches no provider.
- The provider is named by `core.tracker.driver` (`--driver` per call); the one shipped
  provider, `cli`, prints receipts and writes nothing, so a project without a tracker
  behaves as before, and a real tracker slots in as another provider.
- Groom's edges run `tracker-sync` to push the plan's status through the configured
  status map, and `tracker-comment` to post `clarifications.md`; `sync` is idempotent.
- A tracker failure in a hook only warns, so a transition never aborts with the vault
  advanced; `booping-tracker sync --artifact …` by hand reconciles.
- Secrets are never in config: `api_key_env` names the environment variable holding the
  key.
