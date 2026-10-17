---
id: "05"
title: "The driving protocol and every prompt name the new verbs"
sp: 3
status: pending
plan: "plans/202610180333_vault-file-operators/index.md"
---

# M05: The driving protocol and every prompt name the new verbs

## Tasks

**Goal**: rendered skills and playbooks tell the driver `booping state`, `booping transition … --playbook`, `booping set`, `booping config`.
**Scope**: `src/templates/_partials/_playbook_driving.j2` (Run state), `src/templates/_partials/_playbook_graph.j2` (State intro, `Advance:` line), `booping-python/src/booping/commands/render_playbook.py` entry dicts if the line needs new fields, all prompts under `playbooks/**` and `vault/_playbooks/**` naming `playbook-transition`/`playbook-state`, `playbooks/specs/playbook.yaml` header comment, script comments in `playbooks/**/_scripts/*`, render-playbook e2e expected outputs.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 5.1 | Rewrite the Run state section and the graph partial: `booping state {workdir}/{artifact} --playbook {name}`, `Advance: booping transition {artifact path} <to> --playbook {name}[ --state X]`, instance paths for per-instance machines | `src/templates/_partials/_playbook_driving.j2`, `src/templates/_partials/_playbook_graph.j2` | 2 | pending |
| 5.2 | Switch every prompt, playbook.yaml comment and script comment; rebaseline the render-playbook cases whose expected text names the commands | `playbooks/specs/playbook.yaml`, `playbooks/develop/develop-loop/base.md`, `booping-python/e2e/cases/render-playbook/` | 1 | pending |

Tests: integration tier — render-playbook cases for a stateful playbook (groom), a per-instance machine (develop milestone) and a no-artifact machine (code-review).

## Definition of Done

- [ ] Task 5.1: `bin/booping render-playbook groom` shows `Advance: booping transition` with `--playbook groom`; `bin/booping render-playbook develop` shows the milestone instance path; `bin/booping render-playbook code-review` shows `--playbook code-review` with its target.
- [ ] Task 5.2: `grep -rn 'playbook-transition\|playbook-state'` outside history returns nothing.

## References

- `src/templates/_partials/_playbook_graph.j2` — the current State section.

## Verify

`just e2e -k render-playbook`
