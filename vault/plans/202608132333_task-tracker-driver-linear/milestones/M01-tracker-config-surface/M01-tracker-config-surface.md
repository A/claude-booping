---
id: "01"
title: "Tracker config surface"
sp: 2
status: pending
plan: "plans/202608132333_task-tracker-driver-linear/index.md"
---

# M01: Tracker config surface

`core.tracker` exists in the merged config with a `cli` default, so `booping config-get core.tracker` answers with the driver, the Linear connection settings and groom's status and label maps.

**Scope**: `src/config.yaml` (new `core.tracker` block and the groom scaffold's new frontmatter keys), `booping-python/e2e/cases/config-get/`. No Python changes — the config merge is schema-free and loads any key as-is. Consumers written in later milestones: the tracker CLI (M02, M03), the hook scripts (M04) and the injected partials (M06).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Add the `core.tracker` block: `driver: cli`, and `linear:` holding `api_key_env: LINEAR_API_KEY`, `api_url: https://api.linear.app/graphql`, `team`, and `playbooks.groom` with a `statuses:` map (playbook status to Linear workflow-state name, one entry per groom status including `awaiting-clarification`) and a `labels:` map (`request`, `plan`). Comment each key with its semantics in the file's existing heavy-comment style, including that `api_key_env` names an environment variable and never holds a token. | `src/config.yaml` | 1 | pending |
| 1.2 | Extend `core.groom_playbook.scaffold`'s `index.md` frontmatter with `tracker_provider: null`, `tracker_request: null`, `tracker_issue: null` and `return_to: null`, keeping the existing `tojson` treatment of templated values. | `src/config.yaml` | 1 | pending |

## Definition of Done

### Task 1.1

- [ ] `bin/booping config-get core.tracker` prints the block as YAML and exits 0.
- [ ] `bin/booping config-get core.tracker.driver` prints `cli`.
- [ ] `core.tracker` sits directly under `core`, not under a per-playbook namespace, because several playbooks will read it — matching the placement rule in `src/config.yaml`'s header comment.
- [ ] The `statuses:` map has one entry for every status in `playbooks/groom/playbook.yaml`, `awaiting-clarification` included, and no entry that is not a groom status.
- [ ] No config value contains a token, a secret, or a `${…}` interpolation.

### Task 1.2

- [ ] A fresh `bin/booping scaffold core.groom_playbook.scaffold {tmpdir} --set title=T --set type=feature` emits an `index.md` whose frontmatter carries the four new keys, all null.
- [ ] Existing keys and their order are unchanged; the diff against the previous seed is additive only.

## Verify

```
bin/booping config-get core.tracker
bin/booping config-get core.tracker.linear.playbooks.groom.statuses
bin/booping scaffold core.groom_playbook.scaffold /tmp/m01-scaffold-check --set title="T" --set type=feature
just e2e -k config-get
```

Expected: the first two print the mapping as YAML at exit 0; the scaffold diff shows `tracker_provider`, `tracker_request`, `tracker_issue` and `return_to` all null; the `config-get` corpus passes.
