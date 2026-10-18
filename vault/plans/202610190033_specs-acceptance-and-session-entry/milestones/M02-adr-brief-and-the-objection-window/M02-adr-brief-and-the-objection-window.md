---
id: "02"
title: "ADR brief and the objection window"
sp: 8
status: done
plan: "plans/202610190033_specs-acceptance-and-session-entry/index.md"
---

# M02: ADR brief and the objection window

## Tasks

**Goal:** recording an ADR in the specs playbook ends with the locked brief and a gentle objection ask; the answer sets the level with evidence.
**Scope:** `playbooks/specs/guide/prompt.md` (`## Record`, `## Site review`), a new core rule record, the lines elsewhere that say `reviewed` is the owner's alone.

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 2.1 | `## Record`: an ADR is drafted `proposed`, then the brief (locked output above) is shown; no objection → `status: accepted`, `review: shown` with evidence; an explicit yes → `review: accepted` with the quote; a discussion → `discussed`; an objection → back to the draft. Autonomous: the brief is logged as an agent decision, no `review` key (Decision 11) | `playbooks/specs/guide/prompt.md` | 3 | done |
| 2.2 | `## Site review`: the `{ref} — accepted {date}` line sets `review: accepted`, `review_evidence: "site review — {date}"` | `playbooks/specs/guide/prompt.md` | 1 | done |
| 2.3 | Core rule record `specs/rule/0036-adr-accepted-after-a-brief.md`: the brief before acceptance and the objection window, `targets: [specs]`, a `brief:` line, `## Follows from` value/0008 and value/0009 | `specs/rule/0036-adr-accepted-after-a-brief.md` | 1 | done |
| 2.4 | Stale lines: every "never set `reviewed`" / "reviewed stays yours" becomes the level rule of Decision 7 | `playbooks/specs/playbook.md`, `documentation/specs_playbook.md`, `documentation/learn.md`, `playbooks/learn/**` where it says so, `migrations/004_lessons_to_rules/migration.md` left as history | 1 | done |
| 2.5 | Eval fixture for the guide: recording an ADR from a dialogue ends with the brief in the locked shape and the objection ask; smoke tier asserts the table, `Ключевые моменты:`, `Задевает:`, `Решил сам:` and the ask line | `playbooks/specs/guide/tests.yaml`, `playbooks/specs/guide/_fixtures/` | 2 | done |

Test surface: the specs guide step, eval smoke tier (deterministic asserts on the brief's shape); `just specs-check` for the rule record.

## Definition of Done

Task 2.1
- [x] `## Record` names the brief's parts in the locked order and the three answers with the level each sets.

Task 2.2
- [x] `## Site review` has no `reviewed` key left.

Task 2.3
- [x] `just specs-check` passes with the new rule; `bin/booping render-playbook specs` shows its brief under `## Rules`.

Task 2.4
- [x] `grep -rn "never set \`reviewed\`\|reviewed\` stays" playbooks documentation src` returns nothing.

Task 2.5
- [x] `just smoke specs/guide` passes on the new fixture.

Return: the files changed and the Verify verdict, nothing else.

## References

- `playbooks/specs/guide/_fixtures/what-is-open.md` — fixture shape.
- `specs/rule/0033-decisions-listed-for-acceptance.md` — rule record shape.

## Verify

`bin/booping render-playbook specs | grep -n "rule/0036" && just specs-check`
