---
name: playbook-authoring
title: Author a Playbook
summary: Turn a procedure description into a working playbook — an interviewed brief, a confirmed step decomposition, an early manifest, and then per step a confirmed spec, test plan, fixtures, prompt, suite, and optimizer passes to green.
jinja: true
trigger: creating a new playbook; turning a workflow, skill, or procedure description into playbook steps with evals
---

# Author a Playbook

Your goal is a new playbook under a playbook root: steps a fresh, context-isolated agent can
run, review gates that catch drift while review is still cheap, and eval suites that guard
each step's contract. The method is `_playbooks/docs/evals.md` — when a step's instructions
and that document disagree, the document wins.

Run state is harness-managed. The workdir is the target playbook dir `<root>/<slug>/`
(created before the first transition); the machine artifacts are `_specs/index.md` and
`_specs/steps/<step>/index.md`. Sub-agents writing a machine artifact preserve its
frontmatter and never write `status:`, `reviewed_at`, or any stamp — `booping
playbook-transition` is the only writer. There is no `confirmed:` key: confirmation is the
user's explicit chat signal at a gate, captured as the transition out of an
`awaiting-*-confirm` status — never run past a gate on silence. The transition's exit hooks
then stamp `reviewed_at=@now` (or, for a subject that cannot carry frontmatter, the
`<subject>_reviewed_at` compromise stamp) on the file that was reviewed.

`record-decision` runs once in wave 1 as bootstrap, then OUT of wave order: re-invoke it
whenever a step's return or a review-gate outcome carries a user decision, passing the
decision summaries verbatim. `_specs/DECISIONS.md` is the only decisions log — no step
writes a `## Decisions` section anywhere else.

Interview is skippable when the user's input already carries what the brief would. Two
decisions travel with every wave after `decompose`: the **target model** (default
`opus:medium`) and the **destination root** (default the global `_playbooks/`); ask both in
one question after the decomposition is confirmed — a sub-agent that does not receive them
will guess.

No step of this playbook runs an eval itself. The harness runs the smoke tier between
`smoke-optimizer` invocations — re-invoke with the fresh report while red; the same check red
three attempts without progress goes to the user — and runs the regress baseline before
`regress-optimizer` and its verify pass after (skip decided once per run, user can flip). All
other eval runs are proposed to the user, never launched.
