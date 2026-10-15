---
id: "06"
title: "Retro prepare reads the corrections feed"
sp: 2
status: pending
plan: "plans/202610151532_corrections-log/index.md"
---

# M06: Retro prepare reads the corrections feed

Retro's `prepare` step starts from the corrections feed: each logged correction is an issue item, and its dialogue links steer session-log mining.

**Scope**: `playbooks/retro/prepare/base.md` — before the two delegated reads, run `booping correction list --plan {plan}` for each plan in the working set; each entry becomes an issue item with source `correction` (trigger = its `Said`, interpretation from `Did` and `Why`); brief A (session-log mining) receives the entries' `Dialogue` links to read around them; in the orchestrator cross-check, a mined item whose trigger is a message the feed already links (same session and uuid) is dropped as a duplicate. The issue-list sentence names `correction` among the sources. `playbooks/retro/prepare/prompt.md` frontmatter `summary` names the feed. `src/templates/_partials/_session_log_extraction.j2` is not changed — the extra input goes into the brief this step composes.

Tests: none new — retro has no eval suite for `prepare`; `just snapshots` shows the step's drift.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | The feed in `prepare`'s body and summary. | `playbooks/retro/prepare/base.md`, `playbooks/retro/prepare/prompt.md` | 2 | pending |

## Definition of Done

### Task 6.1

- [ ] `bin/booping render-playbook retro --step prepare` names `booping correction list --plan` and the `correction` issue source.
- [ ] The cross-check names the session + uuid duplicate test.
- [ ] The body grows by at most about six lines (value/0002).

Return: the list of changed files, nothing else.

## References

- `playbooks/retro/prepare/base.md` — the body edited.
- `docs/corrections.md` — the entry fields (from M05).

## Verify

`bin/booping render-playbook retro --step prepare | grep -n "correction list"`
