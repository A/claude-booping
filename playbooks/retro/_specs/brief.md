---
reviewed_at: 20260802 14:22
---

# retro — Brief

## Goal

Convert booping's core `/retro` skill into a playbook, now that the `groom` and `develop`
playbooks have landed: the same retrospective procedure — pick up a plan sitting in the status
retro owns, mine the session logs and plan-stage lesson checks for an issue list, collect the
user's raw open-ended feedback before any anchoring, triage each issue with the user, do
per-issue root-cause research and prevention design, synthesize the retrospective against the
retrospective template, then save it and take the plan's exit transition — expressed as discrete
playbook steps with review gates instead of one monolithic skill body. The port stays close to
the original prose (step bodies carry the skill's existing wording rather than rewritten,
expanded prose) and wires in every surface the skill leans on: the retrospective template, the
session-log extraction and plan-lesson-check partials, the pre-save summary format doc, the
available-agents roster and the plan-transitions slice. Two things change relative to the skill:
the retrospective no longer lives in a vault-wide `retrospectives/` directory but is written as
`retro.md` inside the plan directory, and the run's main artifact stays the plan itself
(`index.md`), whose lifecycle statuses drive the run. A run may still cover several plans: the
shared `{vault}/plans/{primary-slug}/retro.md` is the single retrospective and the sibling plans
link to it. The
canonical `/retro` skill is untouched — the playbook ships alongside it, with no `src/config.yaml`
edits and no change to the existing `retro=retrospectives/...` frontmatter hook.

## Success result

A run ends with `{vault}/plans/{primary-slug}/retro.md` written — grounded in
session logs, code diff and the user's own feedback, with per-issue root causes, prevention
options and the user's goal verdict — the plan's frontmatter stamped with the retro reference
and verdict, and the plan moved through retro's exit transition into the status `/learn` claims.
The playbook is bound to the plan lifecycle statuses retro owns, so a run can be resumed from
the plan's own status. Step prompts are no longer than the skill prose they replace, and every
reference doc the original skill loads is reachable from the playbook.

## Artifact home

`{vault}/plans/{slug}/retro.md`

## Wishes

- Stay close to the original `/retro` prose; do not inflate short prompts into large prose.
- Wire in the docs and partials the skill references (retrospective template, session-log
  extraction, plan-stage lesson check, retro pre-save summary format, agent and transition
  surfaces) instead of leaving them unlinked.
- The retro artifact is `{vault}/plans/{slug}/retro.md`; the run's main artifact stays the plan
  (`index.md`).
- Keep the multi-plan option: one run may cover several plans, the single shared retrospective is
  `{vault}/plans/{primary-slug}/retro.md`, and the sibling plans link to it.
- Leave the canonical `/retro` skill untouched — ship the playbook in parallel, with no
  `src/config.yaml` edits and no rewrite of the `retro=retrospectives/...` frontmatter hook.
- Bind the playbook to the plan lifecycle statuses retro owns, joined at the edges to develop's
  machine (develop ends where retro picks up) and to `/learn` at the exit.
- Evals are out of scope for this run — no llm-tests, fixtures, step suites or optimizer work;
  evals come later.
- Ping the user for review when the briefing is done, and again when the migration is finished.
