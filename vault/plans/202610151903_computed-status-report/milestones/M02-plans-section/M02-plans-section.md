---
id: "02"
title: "Plans section"
sp: 3
status: in-progress
plan: "plans/202610151903_computed-status-report/index.md"
---

# M02: Plans section

`booping status` prints a `plans:` line after `items:` (and the `ideas:` slot M03 fills before it); `booping status plans` prints `## plans` with three sub-tables — active plans, done plans without code review, done plans without retro.

**Scope**: add to `src/config.yaml`, directly under `core` after `core.plans`, a commented `status:` block holding `queries:` with two query specs: `active_plans` (`sort: created`, `columns: [status, sp, title]`; its status filter is built per call, never stated in config) and `unreviewed_plans` (`where: {status: done, code_reviews: []}`, `sort: "-created"`, `columns: [sp, title, completed]`). The retro queue is the existing `core.retro_playbook.queries.candidates` — read, not copied.

In `booping-python/src/booping/status.py` add the `plans` section, placed in `SECTIONS` so the final order is `items, ideas, plans, records, marks`. Active statuses: walk the `run` machine of the `groom` playbook then of `develop` from `ctx.playbooks`, keeping each status that machine declares non-terminal, first occurrence wins (`ready-for-dev` stays active because develop declares it non-terminal); reuse `open_items.open_statuses` for the terminal test, moved to a shared place only if the import would be circular. Run each spec in-process with `booping.query.build_spec`/`resolve_spec`/`run` (active with `{"where": {"status:in": active}}`), the way `open_items.index_rows` does. Summary: `plans: {n} {status}, … — done: {a} without code review, {b} without retro`, active statuses in the walk order, zero counts omitted; no active plan → `plans: none active`; the ` — done: …` tail omitted when both counts are zero. Detail: `### active`, `### without code review`, `### without retro`, each a blank line then `booping.query.as_table` over the spec's `columns` plus `path`, or `none`. A missing `groom`/`develop` playbook or `run` machine is an `error: …` exit 1.

Tests (integration tier, e2e `booping-python/e2e/cases/status/`, hand-derived): a vault with plans in `drafting`, `ready-for-dev`, `in-progress`, a `cancelled` one, a `done` one with `code_reviews: []` and `retro: null`, a `done` one reviewed with a retro — short line and `status plans` detail; a vault with only reviewed, retro'd done plans prints `plans: none active` with no tail.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | `core.status.queries` in config; the plans section — active filter from the machines, three specs run in-process, summary and detail. | `src/config.yaml`, `booping-python/src/booping/status.py` | 2 | pending |
| 2.2 | e2e cases for the plans section. | `booping-python/e2e/cases/status/*.txtar` | 1 | pending |

## Definition of Done

### Task 2.1

- [ ] `bin/booping config-get core.status` prints the two query specs.
- [ ] `bin/booping status` in this repo prints `items:` then `plans:` in the locked shape.
- [ ] `status.py` names no plan status literal; `done` appears only in `src/config.yaml`.

### Task 2.2

- [ ] The two plans cases pass, with every M01 case.

Return: the list of changed and created files, nothing else.

## References

- `src/config.yaml` `core.retro_playbook.queries.candidates` — query spec shape and comment style; `booping-python/src/booping/specs/open_items.py` `index_rows` — in-process query run.
- `playbooks/groom/playbook.yaml`, `playbooks/develop/playbook.yaml` — the two `run` machines read.

## Verify

`cd booping-python && uv run pytest e2e/cases/status -q`
