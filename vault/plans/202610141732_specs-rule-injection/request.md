# Request

## Request

> Rule injection: `booping render-playbook` (and agent/skill bodies, where lessons are injected today) also inject every accepted rule from all three tiers whose `targets:` match, as its `brief` plus a link to the record. Lessons keep working unchanged in parallel until a later migration.

Groom invocation (2026-10-14, autonomous run):

> Groom this parked stub (rule injection: render-playbook and agent/skill bodies inject every accepted rule from all three tiers whose targets match, as its brief plus a link; lessons keep working in parallel). The parent plan 202610141731 is done; its clarifications.md answers C11-C13 bind this plan.

Split off from [specs as a core feature — first plan](../202610141731_specs-core-format-cli-injection/index.md) (item 4 of its request) because the full request passed the 35 SP split threshold.

## Task type

`feature` — a new capability every booping user sees in their runs: rules from their own tiers reach the steps, agents and skills they target. Not `bug`: nothing behaves against an expectation today; rules with `targets:` are simply never read by a render surface. Not `refactoring`: rendered output changes for every user with a targeted rule (and for every core playbook, through booping's own core-tier rules), so behaviour is not preserved.

## Problem

Today the only targeted knowledge injected into a render is a lesson: markdown files in `<home_dir>/_lessons/` and `{vault}/_lessons/` with `targets:`, injected by `render-playbook` (composed, `--step`, inline-step surfaces) and by internal agent and skill bodies. The specs format shipped by the parent plan gives rules `targets:` + `brief:` and three tiers (`core.specs.tiers`), and rule/0001 says a taken lesson is written as a rule whose brief — not body — reaches the targeted step with a link to the record. No render surface reads rules yet, so a targeted rule is documentation only. What must change: every render surface that injects lessons also injects every `status: accepted` rule, from the core, global and project tiers, whose `targets:` match the surface — its `brief` plus a link to the record — while lesson injection stays as it is.

## Clarifications and Decisions

- Binding from the parent plan's clarifications: C11 — rule/0012, 0013, 0015 carry no targets/brief and never inject; the remaining targeted core rules (0001, 0004, 0006–0010) are meant to inject for every user. C12 — lesson/rule duplicates in booping's own runs are accepted until the lessons migration. C13 — core rules showing up in the committed `_reports/output.md` snapshots is accepted drift.
- Autonomous run: the owner is unavailable; every default the run takes is recorded in `clarifications.md` as an answered item marked as a default.
- Out of scope: migrating lessons to rules, retiring `_lessons/`, a `## Rules` surface for anything that does not inject lessons today.
