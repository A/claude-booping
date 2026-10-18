---
id: "03"
title: "Project-manager intake files only what outlives the session"
sp: 6
status: pending
plan: "plans/202610190307_core-rules-open-item-filter-and-staged-experiments/index.md"
---

# M03: Project-manager intake files only what outlives the session

## Tasks

**Goal:** intake files an item only for later work or a waiting owner question, keeps session instructions, gate answers, policies and decisions out, and lists filed items as `Создан {id}: {title}` / `Created {id}: {title}`.
**Scope:** `playbooks/project-manager/intake/` (prompt, tests, fixtures); the targeted rule from M01 reaches this step through `render-playbook`.
**Tests:** surface the intake step under the promptfoo smoke harness; cases — "пингани, как будет релиз" files nothing, "пауза pi на 2 часа" files nothing, two requests + a real-work aside still file three, the filed-ids reply uses the new line; tier — smoke (deterministic asserts on written files and the return).

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Replace "each distinct ask, asides included" with the filter: a request is filed only when it must outlive the session — work for later or a question waiting on the owner; an instruction for this session, a gate answer or UAT confirmation, a standing policy (→ `specs` rule) or a decision (→ ADR) files nothing and is done or kept in the session. Change the final posting line to `Создан {id}: {title}` / `Created {id}: {title}`, one line each, in the user's language. Keep the verbatim-heredoc and answer paragraphs as they are. | `playbooks/project-manager/intake/prompt.md` | 2 | pending |
| 3.2 | Two new smoke fixtures + cases, Russian dialogues: "пингани, как будет релиз" and "пауза pi на 2 часа" — each asserts no file written (`allow_no_files` already on). | `playbooks/project-manager/intake/_fixtures/session-instruction-ping.md`, `playbooks/project-manager/intake/_fixtures/session-instruction-pause.md`, `playbooks/project-manager/intake/tests.yaml` | 3 | pending |
| 3.3 | Update the `filed-ids-posted` case's ONE-LINE-PER-ITEM asserts to the new line — an entry regex for `Created OI-000N: {title}` (or `Создан`, matching the fixture's language) at line start. | `playbooks/project-manager/intake/tests.yaml` | 1 | pending |

## Definition of Done

Task 3.1
- [ ] The phrase "asides included" is gone from the prompt; the filter names both item kinds and the four non-item kinds with their destinations.
- [ ] `bin/booping render-playbook project-manager --step intake` shows the new filter and the M01 rule under `## Rules`.

Task 3.2
- [ ] Both new cases pass under `just smoke project-manager/intake`; the fixtures follow `two-requests-and-an-aside.md`'s shape (no shell, stated outputs).

Task 3.3
- [ ] `two-requests-and-an-aside`, `answer-only` and `filed-ids-posted` still pass.

## References

- `playbooks/project-manager/intake/_fixtures/answer-only.md` — a no-new-item fixture.
- `playbooks/project-manager/intake/tests.yaml` — case and assert shapes.

## Verify

`just smoke project-manager/intake`
