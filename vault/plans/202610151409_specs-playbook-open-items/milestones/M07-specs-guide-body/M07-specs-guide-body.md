---
id: "07"
title: "The specs guide \u2014 preamble and scenarios"
sp: 4
status: pending
plan: "plans/202610151409_specs-playbook-open-items/index.md"
---

# M07: The specs guide — preamble and scenarios

`/playbook specs` renders a guide: the preamble explains specs by reference and resolves the tiers, the `guide` step lists the user's scenarios and lets the model act from the dialogue (adr/0024).

**Scope**: `playbooks/specs/playbook.md` preamble, added above M01's paragraph — what specs are and every type and principle by one link to `${CLAUDE_PLUGIN_ROOT}/src/specs/README.md` (never restated: no type table, no frontmatter list); the resolved tier roots rendered from config (`core.specs.tiers`) or a macro, never typed; the record-writing invariants a model would otherwise miss: `booping specs next {type}` for the number, `created_by: claude`, never set `reviewed`, `booping specs check` after every write. `playbooks/specs/guide/prompt.md` body: one opening line (act on the request; scenarios orient, never restrict; never ask which action), then one `##` per scenario, 2–5 lines each, each ending with the next call ([rule/0005](../../../../specs/rule/0005-next-step-is-named.md)):

- **Init** — no project tier: offer `booping specs init --tier project`, then the alignment guide (link `${CLAUDE_PLUGIN_ROOT}/docs/specs-alignment.md`, written in M08).
- **Alignment** — refine values: the alignment guide's values-then-boundaries order.
- **Auto-review** — read values, rules and ADRs; contradictions become `conflict` records or `open-items add --direction conflict`.
- **Record** — a decision → ADR (one choice, real alternative, reason not recoverable from code); an idea → idea; a constraint → rule with `targets`/`brief`; an ADR with a confirmation line → `booping specs open-items add --record adr/NNNN`.
- **Sync specs and code** — compare records with the code; each gap → `open-items add --source sync` with its direction; `open-items scan` for marks and check findings.
- **Retro to rules** — a retrospective exists → `/playbook learn`; a lesson from the dialogue → a rule record directly.
- **Open items** — `open-items list`; the user picks; hand off to `/playbook groom` naming the ids (groom links them); dropping → `close --dropped --reason`.

Every structured value (directions, statuses, verbs' flags) comes from the CLI's `--help` or config, not prose ([rule/0017](../../../../specs/rule/0017-structured-data-rendered-not-restated.md)).

Tests: none at this tier — M09's smoke suite covers the rendered guide.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 7.1 | The preamble: README link, rendered tiers, record-writing invariants. | `playbooks/specs/playbook.md` | 2 | pending |
| 7.2 | The guide body: opening line and the seven scenarios. | `playbooks/specs/guide/prompt.md` | 2 | pending |

## Definition of Done

### Task 7.1

- [ ] No sentence restates `src/specs/README.md`; the README is linked once.
- [ ] Tier paths render from config — `bin/booping render-playbook specs` shows this repo's resolved tiers.
- [ ] The information-architecture pass ([booping:rule/0006](../../../../../specs/rule/0006-information-architecture-pass.md)) holds: no motivation, no "you are" preamble.

### Task 7.2

- [ ] Seven scenarios, each ending with the named next call.
- [ ] No list of directions or statuses typed in prose.
- [ ] The alignment-guide link is the only place it is referenced.

Return: the list of changed files, nothing else.

## References

- `playbooks/learn/playbook.md` — a jinja preamble with includes and a config-rendered value.
- `playbooks/setup/playbook.md` — an ephemeral playbook's preamble.

## Verify

`bin/booping render-playbook specs`
