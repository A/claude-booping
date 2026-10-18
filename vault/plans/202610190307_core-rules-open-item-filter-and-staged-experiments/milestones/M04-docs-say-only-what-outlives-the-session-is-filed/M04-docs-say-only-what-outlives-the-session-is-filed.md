---
id: "04"
title: "Docs say only what outlives the session is filed"
sp: 2
status: done
plan: "plans/202610190307_core-rules-open-item-filter-and-staged-experiments/index.md"
---

# M04: Docs say only what outlives the session is filed

## Tasks

**Goal:** the public docs and the playbook summary describe the new intake filter, not "every request, asides included".
**Scope:** `documentation/project_manager.md`, `README.md`, `playbooks/project-manager/playbook.md` (summary frontmatter only).
**Tests:** none beyond the grep in Verify — prose only.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Rewrite the "Every message" paragraph: only what outlives the session becomes an item; session instructions, gate answers, policies and decisions do not; filed ids listed with their titles. Align README's project-manager sentence and the playbook `summary:`. | `documentation/project_manager.md`, `README.md`, `playbooks/project-manager/playbook.md` | 2 | done |

## Definition of Done

Task 4.1
- [x] Audience filter: only what a user of the manager sees — which messages become items, how ids appear; no rule ids, no internal step names beyond `project-manager`.
- [x] "asides included" and "every request" appear in none of the three files.

## References

- `documentation/project_manager.md` — the paragraph at "**Every message.**".

## Verify

`! grep -rn -i "asides included\|every request" documentation/project_manager.md README.md playbooks/project-manager/playbook.md`
