---
id: "01"
title: "booping set` replaces frontmatter-update and marker-set"
sp: 4
status: pending
plan: "plans/202610180333_vault-file-operators/index.md"
---

# M01: booping set` replaces frontmatter-update and marker-set

## Tasks

**Goal**: one `set` verb writes frontmatter of a markdown file or keys of the `.booping` marker; the hook verb follows.
**Scope**: `booping-python/src/booping/commands/` (new `set.py` from `frontmatter_update.py` + `marker_set.py`), `cli.py`, `context/lifecycle.py` (prepended `set status=<to>`), `commands/playbook_transition.py` hook dispatch, every `playbook.yaml` hook list (`playbooks/**`, `vault/_playbooks/**`), `playbooks/_scripts/stamp-session`, prompts and `src/config.yaml` comments naming either command, e2e `cases/frontmatter-update/` + `cases/marker-set/` → `cases/set/`, unit tests.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 1.1 | Add `set`: `.booping` basename → marker write (one or more pairs, `latest_migration` rule kept), else frontmatter write with `--remove`/`--append`; remove both old commands and their registration | `booping-python/src/booping/commands/set.py`, `booping-python/src/booping/cli.py` | 2 | pending |
| 1.2 | Rename the hook verb to `set` in the lifecycle prepend, the hook dispatcher and every `playbook.yaml`; switch every prompt, script and comment calling either old command | `booping-python/src/booping/context/lifecycle.py`, `playbooks/*/playbook.yaml`, `playbooks/_scripts/stamp-session` | 1 | pending |
| 1.3 | Move the e2e cases to `cases/set/`, rewriting command lines; one case per marker path and one for a rejected `latest_migration`; adjust unit tests | `booping-python/e2e/cases/set/`, `booping-python/tests/context/lifecycle_test.py` | 1 | pending |

Tests: integration tier, txtar cases — frontmatter set/remove/append, marker set incl. `@latest`, a hook-driven `set` through a transition.

## Definition of Done

- [ ] Task 1.1: `booping set {file}.md k=v` writes frontmatter; `booping set .booping latest_migration=@latest` writes the marker; `booping frontmatter-update` and `booping marker-set` exit 2 as unknown commands.
- [ ] Task 1.2: `grep -rn 'frontmatter-update\|marker-set'` outside `vault/plans`, `*/_specs`, `_reports`, CHANGELOG history and migration old-path columns returns nothing.
- [ ] Task 1.3: `just e2e -k set` passes; no `cases/frontmatter-update/` or `cases/marker-set/` directory remains.

## References

- `booping-python/src/booping/commands/frontmatter_update.py`, `booping-python/src/booping/commands/marker_set.py` — the behaviour merged.
- `booping-python/e2e/cases/frontmatter-update/` — case shape.

## Verify

`just e2e -k "set or playbook-transition"`
