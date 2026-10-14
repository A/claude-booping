---
id: "06"
title: "Setup provisions the specs tiers and namespace"
sp: 3
status: pending
plan: "vault/plans/202610142150_lessons-become-rules/index.md"
---

# M06: Setup provisions the specs tiers and namespace

`setup` stores the global namespace and creates the global specs tier on the machine level, and creates the project specs tier on the project level, both through `booping specs init`.

**Scope**: `playbooks/setup/setup-booping/sonnet-5.md`, `playbooks/setup/setup-project/opus-5.md`. Namespace storage and asking rule: `clarifications.md` C8. The vault scaffold's `_lessons:` entry stays (C8).

Tests: the rendered step bodies; the mechanics are `specs init`'s, covered in M01.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | setup-booping: a `## Global specs tier` section — when the merged config has no `core.specs.tiers.global.namespace` (`booping config-get core.specs.tiers.global.namespace` prints null), ask once via `AskUserQuestion` (default `$USER`), add the key to the global config file keeping every other key; then `booping specs init --tier global` and report its output. Applies on both branches; the already-initialized branch's "config is never edited" line gains the namespace key as its one exception. | `playbooks/setup/setup-booping/sonnet-5.md` | 2 | pending |
| 6.2 | setup-project: after the marker step, `booping specs init --tier project` from the repo root, report its output; the already-initialized report gains a `specs:` line (the tier root, or `none` with the init command); the hard rule naming what may be written adds the specs tier. | `playbooks/setup/setup-project/opus-5.md` | 1 | pending |

## Definition of Done

### Task 6.1

- [ ] The namespace is asked only when the key is absent; the written YAML nests it as `core: specs: tiers: global: namespace:`.
- [ ] No directory creation is described in prose — only the `specs init` call.

### Task 6.2

- [ ] The step creates no `specs` path itself; the symlink case is `specs init`'s, not the step's.

Return: the list of changed files, nothing else.

## References

- `playbooks/setup/setup-project/opus-5.md` step 5 — the home-dir symlink precedent and numbered-step style.

## Verify

`bin/booping render-playbook setup`
