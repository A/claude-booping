---
id: "08"
title: "Docs for one-pass groom and the plan commands"
sp: 3
status: pending
plan: "plans/202610161319_groom-one-pass-and-plan-split/index.md"
---

# M08: Docs for one-pass groom and the plan commands

**Goal**: the docs describe groom's one-pass draft and `booping plan split` / `plan check` as shipped.

**Scope**: `documentation/groom.md`, `documentation/project_config.md`, `documentation/vault.md`, `README.md`, `CLAUDE.md`, `CHANGELOG.md`. Audience: booping users (docs, README, CHANGELOG) and contributors (CLAUDE.md).

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 8.1 | `documentation/groom.md`: steps table (intake, draft-plan, cross-review, present), what draft-plan does (research stage, `draft.md`, split, check, fallback, three fix rounds), the plan directory now holding `draft.md`; a "booping plan split / plan check" section with the I/O contract from `index.md`; `## Groups` in `index.md`. `documentation/vault.md`: `draft.md` in the plan directory listing. | `documentation/groom.md`, `documentation/vault.md` | 1 | pending |
| 8.2 | `documentation/project_config.md`: `core.groom_playbook.split.sections` and `split_fallback_agent`. `README.md` Statuses: `researching` now "draft-plan's research stage over the code is running" (rule/0023); the develop bundling sentence "up to two consecutive milestones" corrected to packing by `core.sprint.max_sp` SP. `CHANGELOG.md`: one entry under the unreleased heading in the file's existing style. | `documentation/project_config.md`, `README.md`, `CHANGELOG.md` | 1 | pending |
| 8.3 | `CLAUDE.md` `## Commands`: add `plan` (`split`, `check`) to the runtime CLI subcommand list. | `CLAUDE.md` | 1 | pending |

Audience filter (rule/0008): user-facing pages say what groom does and how to call the commands — no benchmark numbers beyond one line pointing at adr/0030/0031, no internal port history.

Tests: surface the docs build; case — `mkdocs build --strict` clean; tier docs build.

## Definition of Done

### Task 8.1

- [ ] `grep -n -E 'research-codebase|research-web' documentation/groom.md` prints nothing; `plan split` and `plan check` are each documented with flags and exit codes.

### Task 8.2

- [ ] README's Statuses `researching` line and the bundling sentence match the shipped behaviour; CHANGELOG has the entry.

### Task 8.3

- [ ] `grep -n 'plan' CLAUDE.md` shows `plan` (`split`, `check`) in the subcommand list.

## References

- `documentation/groom.md` — page being updated.
- `documentation/project_config.md` — how an existing `core.groom_playbook` key (`cross_review_agent`) is documented.

## Verify

```
just docs
```
