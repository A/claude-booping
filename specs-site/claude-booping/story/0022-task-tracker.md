---
type: story
title: Task tracker
summary: The booping-tracker CLI carries every interaction with an issue tracker, and groom mirrors its run status and questions onto the tracker issue.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-20
status: done
priority: P2
sources: [booping-tracker/README.md, src/config.yaml, playbooks/groom/playbook.yaml]
---

As **an advanced user**, I want my runs mirrored onto my issue tracker, so that the
tracker shows where a plan stands without me copying it by hand.

## Scenarios

1. The user names a tracker provider in `core.tracker.driver` and the environment
   variable holding its key in `api_key_env`.
2. A groom run moves the plan along its edges; each edge's `tracker-sync` hook pushes
   the plan's status to the tracker issue through the configured status map.
3. Groom parks on a question; `tracker-comment` posts `clarifications.md` to the issue
   verbatim.
4. The user checks the issue on the tracker and sees where the plan stands.

Without a tracker: the shipped `cli` provider prints receipts and writes nothing, so a
project with no tracker runs as before.

## Edge cases

- The tracker fails during a hook: the hook only warns, the transition completes, and `booping-tracker sync --artifact …` by hand reconciles.
- A call with `--dry-run`: no provider is reached.
- An unknown driver name: a hard error.

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
