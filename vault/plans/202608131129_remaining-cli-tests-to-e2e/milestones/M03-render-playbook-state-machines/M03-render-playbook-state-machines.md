---
id: "03"
title: "render-playbook state machines"
sp: 3
status: pending
plan: "vault/plans/202608131129_remaining-cli-tests-to-e2e/index.md"
---

# M03: render-playbook state machines

The `## State` section a stateful playbook renders — its presence rule, its entries, its status rows and its notices — is pinned by txtar cases.

**Scope**: `render-playbook` against manifests carrying `state:` / `states:`. Files: new `booping-python/e2e/cases/render-playbook/*.txtar`. Ported from the `state machines` section of `tests/test_render_playbook.py` (lines 605–778) minus the graph-in-both notice, which M01 covers. Fixtures reuse M01's conventions and add a `states:` block; the instance-entry fixture reuses M02's subgraph shape with a `state:` on the mapping node.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Presence and placement cases: a playbook without `states:` renders no `## State` section at all; a stateful one renders it after the step sections, with its entries ordered by the execution graph rather than manifest order | `booping-python/e2e/cases/render-playbook/*.txtar` | 1 | pending |
| 3.2 | Entry-content cases over one two-machine fixture: the outer entry's `Referenced by`, `Artifact`, `Initial status` and `Advance:` invocation; its status rows with `Status`, `To`, `When` and `Gates` cells including terminal rows; and the instance entry whose artifact path carries `{instance}` and whose `Advance:` invocation adds `--instance` | `booping-python/e2e/cases/render-playbook/*.txtar` | 1 | pending |
| 3.3 | State notice cases: a malformed `states:` block, an unknown state reference on the outer graph, an unknown state reference inside a subgraph whose notice names the subgraph, and the non-blocking note for a declared machine no node references | `booping-python/e2e/cases/render-playbook/*.txtar` | 1 | pending |

## Definition of Done

### Task 3.1

- [ ] A stateless fixture's pinned stdout contains no `## State` heading.
- [ ] A stateful fixture renders `## State` after the last `## Step:` section, and its entries appear in execution-graph order — asserted by a fixture whose manifest declares the machines in the opposite order.

### Task 3.2

- [ ] The outer entry names the graph that references it, its `artifact:` relative path, its initial status, and the exact `booping playbook-transition {name} <to> --workdir <run workdir>` line.
- [ ] The status table's rows are pinned in full, including a terminal row rendering `*(terminal)*` and an em-dash cell where a transition declares no gates.
- [ ] The instance entry renders its `{instance}`-bearing artifact path unexpanded and an `Advance:` invocation carrying `--instance <slug>`.

### Task 3.3

- [ ] Each notice fixture renders at exit 0 with its full notice text pinned.
- [ ] The unknown-state notice names the state and the node that referenced it; the inner one additionally names the subgraph.
- [ ] The orphan-state note renders as a `**Note` line and the render still carries its `## State` section for the referenced machines.

## Verify

```
cd booping-python && uv run pytest e2e -k render-playbook
```

Every case passes without `--txtar-update`, and a follow-up `--txtar-update` run leaves the working tree clean.
