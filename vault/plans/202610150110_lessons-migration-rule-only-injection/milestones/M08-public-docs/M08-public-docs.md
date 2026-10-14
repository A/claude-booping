---
id: "08"
title: "Public docs describe rules as the one carrier"
sp: 4
status: pending
plan: "vault/plans/202610150110_lessons-migration-rule-only-injection/index.md"
---

# M08: Public docs describe rules as the one carrier

The public docs site and the README describe targeted rules as the one way to shape a playbook, step, agent or skill: no `_lessons/` directory, no `## Lessons` section, no `--no-lessons` flag.

**Scope**: `documentation/playbook.md` — delete the `## Lessons` section and every lessons aside in `## Rules` and the flag reference (`--no-lessons` gone, `--no-rules` stands alone, `--project` pins discovery "for playbooks and rules"); one sentence in `## Rules` saying a vault's former lessons are converted by migration 004 through `/playbook migrate`. `documentation/vault.md` — drop the `_lessons/` section and the blurb mention. `documentation/project_config.md` — the scaffold sample and the setup-tree prose drop `_lessons`. `documentation/integrating-external-agents.md` and `documentation/recipes/external-agents.md` — the worked example shapes an agent with a targeted rule record in the project specs tier (`targets: [agent:{id}]`, `brief:`), not a `_lessons/` file. `documentation/specs.md:29`, `documentation/learn.md` (the dedup sweep reads no lessons), `documentation/install.md`, `documentation/quick_start.md`, `documentation/index.md`, `documentation/groom.md`, `README.md` — every mention of lesson files, targeted lessons or their injection becomes rules. Out of scope: the retro / code-review / groom cross-review "lesson check" wording (`documentation/retro.md`) — the legacy cross-check set is parked (`clarifications.md` C3) and stays true; "lesson" as plain English for what a retro teaches stays.

Audience ([rule/0008](../../../../specs/rule/0008-audience-scoped-content.md)): plugin users and playbook authors — what they write, where it lands, what reaches a run. No module names, no `context/` internals, no history of the change beyond the one migration sentence.

Tests: `just docs` builds the site with no new warning; links resolve.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 8.1 | `playbook.md` rewrite of the lessons and rules sections and the flag reference. | `documentation/playbook.md` | 2 | pending |
| 8.2 | The remaining pages and the README, as Scope lists. | `documentation/vault.md`, `documentation/project_config.md`, `documentation/integrating-external-agents.md`, `documentation/recipes/external-agents.md`, `documentation/specs.md`, `documentation/learn.md`, `documentation/install.md`, `documentation/quick_start.md`, `documentation/index.md`, `documentation/groom.md`, `README.md` | 2 | pending |

## Definition of Done

### Task 8.1

- [ ] `rg -n -i 'lesson' documentation/playbook.md` prints only the migration-004 sentence.
- [ ] Every anchor other pages link into `playbook.md` (`#rules` and any `#lessons` link) resolves — `#lessons` links are repointed at `#rules`.

### Task 8.2

- [ ] `rg -n -i '_lessons|targeted lesson|no-lessons|## Lessons' documentation README.md` prints nothing.
- [ ] Remaining `lesson` hits in these files are plain-English retro wording or `documentation/retro.md`'s cross-check, nothing else.
- [ ] No page names a Python module, a context field or a template partial.

Return: the list of changed files, nothing else.

## References

- `documentation/specs.md` — current wording of rules and tiers to align with.
- `src/specs/README.md` — the rule record format the agent-shaping example follows.

## Verify

`just docs`
