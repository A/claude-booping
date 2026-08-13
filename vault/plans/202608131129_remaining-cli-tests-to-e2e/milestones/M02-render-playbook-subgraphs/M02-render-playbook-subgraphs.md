---
id: "02"
title: "render-playbook subgraphs"
sp: 4
status: pending
plan: "vault/plans/202608131129_remaining-cli-tests-to-e2e/index.md"
---

# M02: render-playbook subgraphs

A subgraph playbook's render — its table rows, its intro, its inner step sections and every notice that names the subgraph — is pinned by txtar cases.

**Scope**: `render-playbook` against manifests whose `graph:` carries a mapping node. Files: new `booping-python/e2e/cases/render-playbook/*.txtar`. Ported from the `subgraphs` section of `tests/test_render_playbook.py` (lines 249–570), the largest single section in the file; nothing is deleted here. Fixture conventions come from M01 — the subgraph fixtures add inner step directories under the playbook dir, addressed by the mapping node's own `graph:`.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | Happy-path subgraph render in one case: the table listing the subgraph row tagged `*(subgraph)*` followed by its inner rows tagged `*(in {name})*`, the section order across outer steps and the `## Subgraph:` intro, the intro's bullets including `Repeat:` and `After:`, and no notice line anywhere | `booping-python/e2e/cases/render-playbook/*.txtar` | 1 | pending |
| 2.2 | Inner-step section cases: the `Part of:` bullet and delegation-bullet order on an inner step, an intro without `Repeat:` producing neither the bullet nor the `Part of:` suffix, outer steps carrying no `Part of:` bullet, and `--step` on an inner step printing its bare body | `booping-python/e2e/cases/render-playbook/*.txtar` | 1 | pending |
| 2.3 | Structural notice cases: a bad node, a bad inner node whose notice names the subgraph, a nested subgraph, a duplicate step across scopes, an inner unknown dependency and an inner cycle — the last four all naming the subgraph in their text | `booping-python/e2e/cases/render-playbook/*.txtar` | 1 | pending |
| 2.4 | Discovery and inline-interaction cases: a missing inner step directory notices, an inner step directory is not reported as an orphan, an unwired directory still is, inline steps sharing an inner wave notice, an inline inner step in a parallel outer wave notices, the same step alone in its outer wave does not, and a parallel-wave notice is emitted once rather than per scope | `booping-python/e2e/cases/render-playbook/*.txtar` | 1 | pending |

## Definition of Done

### Task 2.1

- [ ] One case pins the full stdout of a subgraph playbook: table rows in order with their `*(subgraph)*` and `*(in {name})*` tags, then outer sections, the `## Subgraph:` intro, and the inner `## Step:` sections.
- [ ] The intro's `Repeat:` prose and its `After:` list are asserted verbatim.
- [ ] The happy-path case carries no `**STOP` and no `**Note` line, and the subgraph key itself is never reported as a missing step.

### Task 2.2

- [ ] An inner step's section shows `Part of:` naming its subgraph, with the repeat suffix, ahead of its delegation bullets.
- [ ] A subgraph whose intro declares no `Repeat:` renders neither the intro bullet nor the `Part of:` suffix.
- [ ] An outer step's section contains no `Part of:` bullet.
- [ ] `--step {inner}` prints the inner step's body alone, with no intro and no surrounding sections.

### Task 2.3

- [ ] Six fixtures, one per fault, each render at exit 0 with the full notice text pinned.
- [ ] The bad-inner-node, nested-subgraph, inner-unknown-dependency and inner-cycle notices each name the subgraph they came from.
- [ ] The duplicate-step notice names the step and both scopes it appears in.

### Task 2.4

- [ ] A subgraph naming an inner step with no directory renders the missing-step notice.
- [ ] A wired inner step directory produces no orphan note, while a directory wired nowhere still does — asserted in two cases over near-identical fixtures.
- [ ] Two inline steps sharing an inner wave render the notice; an inline inner step in a parallel outer wave renders it; the same inline inner step alone in its outer wave renders no notice.
- [ ] A fixture whose fault appears in both the outer graph and a subgraph renders the parallel-wave notice exactly once, asserted by pinning the whole stdout rather than a substring.

## Verify

```
cd booping-python && uv run pytest e2e -k render-playbook
```

Every case passes without `--txtar-update`, and a follow-up `--txtar-update` run leaves the working tree clean.
