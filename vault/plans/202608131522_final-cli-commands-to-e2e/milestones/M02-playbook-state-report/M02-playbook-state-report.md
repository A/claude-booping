---
id: "02"
title: "playbook-state report shape and ordering"
sp: 3
status: pending
plan: "vault/plans/202608131522_final-cli-commands-to-e2e/index.md"
---

# M02: playbook-state report shape and ordering

The frontier report's YAML shape — statuses, edge sets, state ordering and per-instance keys — is pinned by txtar cases.

**Scope**: `booping playbook-state <playbook> [--workdir PATH]` against multi-state and subgraph-bearing playbooks. Files: new `booping-python/e2e/cases/playbook-state/*.txtar`. The unit file is not touched here — it is deleted in M04, once M03 has ported the rest. Fixture playbooks are inlined per case under `fixtures/home/Claude/_playbooks/fx-*/` and named with the `fx-` prefix; the `playbook-transition-home` tree is not copied. A case that bootstraps or advances a machine carrying a `script` hook needs a leading `chmod +x` cmd line, per `e2e/README.md`.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Write the outer-state cases: a missing artifact reporting `not-started` with the synthetic bootstrap edge and no gates, a mid-run status carrying its full `next` edge set with `when` and `gates`, a terminal status omitting `next` entirely, and the outer state appearing before inner states in the document | `booping-python/e2e/cases/playbook-state/*.txtar` | 2 | pending |
| 2.2 | Write the instance-state cases: a per-instance machine reporting `instances: {}` before any instance exists, instances keyed by slug and sorted, and the instance key being exactly what the `{instance}` placeholder matched — one case for a flat artifact path, one for a nested one | `booping-python/e2e/cases/playbook-state/*.txtar` | 1 | pending |

## Definition of Done

### Task 2.1

- [ ] A case with a seeded workdir and no artifact file reports `status: not-started` and a `next` list holding exactly the synthetic bootstrap edge, whose `when` is the run-not-started text and which carries no `gates` key.
- [ ] A case advances the run with `booping playbook-transition` on a preceding cmd line, then pins the reported status and every outgoing edge's `to`, `when` and `gates`.
- [ ] A case advances to a terminal status and its pinned YAML has no `next` key at all.
- [ ] A case on a playbook declaring both an outer and an inner state pins the two in outer-first document order.

### Task 2.2

- [ ] A case on a per-instance machine with no instance yet pins `instances: {}`.
- [ ] A case that bootstraps two instances out of alphabetical order pins them sorted by slug, each with its own status and edges.
- [ ] Two cases differing only in the machine's `artifact:` path shape — one flat, one nested — pin the instance key as the segment the `{instance}` placeholder matched.

## Verify

```
cd booping-python && uv run pytest e2e -k playbook-state
```

Green, with every case in `e2e/cases/playbook-state/` collected.
