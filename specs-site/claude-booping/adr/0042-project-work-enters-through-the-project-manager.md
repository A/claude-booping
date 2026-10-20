---
type: adr
title: Every request in a booping session enters through the project-manager
summary: Every request in a booping project session, questions and debugging 
  included, goes to the project-manager, which routes it and launches and 
  orchestrates the other playbooks.
created_by: claude
created_at: 2026-10-19
updated_at: 2026-10-19
status: accepted
values: [value/0013, value/0019, value/0009, value/0002, value/0003, value/0010]
rules: [rule/0025, rule/0033]
supersedes: [adr/0039]
review: accepted
review_evidence: «Да, все супер, принимаем» — 2026-10-19, chat (decision lines 
  1–8)
---

## Context

[ADR 0039](0039-session-start-points-to-playbooks.md) made the session-start hook inject the playbook table and tell the session to offer the fitting playbook, the project-manager when nothing narrower fits. In a live session on 2026-10-19 the agent picked the right playbook but neither ran it nor offered it properly, and gathered the project status by hand instead: the routing was right, the hand-off never happened.

Someone has to route an opening request to a playbook and then carry the work through. The candidates are the session itself (the hook's prose), the `/playbook` skill, a dedicated entry playbook, a config key, or the project-manager.

A screen on 2026-10-19 measured routing alone: one Opus call per request, 18 opening requests, isolated `claude -p` with no tools, JSON output (private note, not published). The bare `/playbook` router chose the expected playbook for 16 of 18, the other 2 acceptable alternatives (a feature routed to groom, a typo fix to no playbook); with a targeted rule added, 18 of 18. Neither asked which playbook to run. Not measured: whether the session actually invokes the playbook rather than doing the work by hand, repeats, and hard or ambiguous requests.

Cheap options: prose in a prompt is option A (today's hook) and option B (a targeted rule on the skill); extending an existing primitive is option E (the project-manager playbook gains a route) and option D (the config tiers); building nothing is option A.

## Criteria

- A project-work request reaches a playbook that runs, not just an offer.
- The work is managed past the first playbook — groom → develop → review → merge — not routed once and dropped.
- No new code for the entry now ([rule/0025](../rule/0025-who-reads-the-result-decides.md): prose first, a CLI over it is a later optimisation).
- Context cost per session entry.

## Decision

Option E (owner, 2026-10-19: «мы всегда запускаем PM»).

1. Every request in a booping project session enters through the `project-manager` playbook — questions, explanations and debugging included; there is no no-playbook exception (owner: «иначе это все будет работать мимо спека, мимо известной информации»).
2. The project-manager is the smarter router: it routes, manages the work, and launches the specific playbooks itself — groom, develop, code-review, specs, retro, docs, pr-description, backlog-manage, model-benchmark, playbook-authoring, migrate and the rest — and orchestrates them (owner: «это его задача»). The change to the manager is OI-0036.
3. For now the wiring is prose: the session-start hook tells the session to run `/booping:playbook project-manager` on every request; no new code for a direct entry.
4. Rendering the manager and the playbook table straight into session start is a later optimisation, OI-0037, done only once the manager entry proves itself.

Why (owner, 2026-10-19):

- Many projects run as a series of sprints, plus other work such as updating the specs. Narrow entries make every session a separate session for one narrow task. Working with a project manager is far more convenient: one contact the owner talks everything through with, who organises the work — "groom this task", or "groom a scope bigger than one sprint and start it right away" — grooms, and escalates to the owner when needed. The owner no longer drives tasks that are already being handled.
- Stricter work goes through the manager too — "research this carefully, groom, I review, first iteration, ping me, second iteration…": the meta-level of the work moves to the manager.
- The manager knows the specs and how to work with them out of the box: it escalates a conflict it sees in a decision, files open items for the tails left behind, and given "I have an hour" walks the open items and the specs, collects the conflicts and surfaces the critical ones for the owner to answer.
- Observed on 2026-10-19: a session that chatted without running a playbook had not read the specs or the details and its suggestions were poor; once the playbook ran, quality rose sharply. So the manager starts right away; about 5K tokens per entry is not a cost worth weighing against that.
- The manager's handling of edge cases is tuned later, instead of tuning plain routing.

This record supersedes [ADR 0039](0039-session-start-points-to-playbooks.md) (owner: «мы переосмыслили это»): its hook and its table stay; its "offer the fitting playbook", its "questions and debugging need no playbook" and its rejection of "load the project-manager on every session start" are reversed.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [Hook routes straight to the narrow playbooks](#hook-routes-straight-to-the-narrow-playbooks) | rejected | low | high | Did not work in practice; routing without orchestration |
| [The /playbook skill routes, with a targeted rule](#the-playbook-skill-routes-with-a-targeted-rule) | rejected | low | high | Routing only, no orchestration |
| [A dedicated entry: an intro playbook or a config key](#a-dedicated-entry-an-intro-playbook-or-a-config-key) | rejected | medium | high | Routing only, no orchestration |
| [Always the project-manager](#always-the-project-manager) | accepted | medium | high | One contact that routes, orchestrates and escalates; meaningful work starts at once |

### Hook routes straight to the narrow playbooks

Option A, the state before this record ([ADR 0039](0039-session-start-points-to-playbooks.md)): the hook tells the session to offer the fitting playbook and run it once the user agrees, else offer the project-manager. Building nothing. Its variants fall under the same verdict: hook prose that runs the fitting narrow playbook straight away instead of offering it, and a split entry where single-shot requests (a retro, docs, a PR description) go straight to their playbook and only plan-track or unclear work goes to the manager.

- **Pros:** nothing to build; the cheapest per entry — no manager render, no status call; a narrow request goes straight to its playbook.
- **Cons:** did not work in practice — in a live session on 2026-10-19 the agent named the right playbook but neither ran nor offered it and gathered status by hand; the variants route without orchestrating, so every session narrows to one task (owner).
- **Complexity:** low.
- **Reversibility:** high.

### The /playbook skill routes, with a targeted rule

Option B: the `/playbook` skill is the router, sharpened by a `skill:playbook` rule — no narrow match or several playbooks → project-manager; questions, explanations, debugging → no playbook.

- **Pros:** prose only, on an existing primitive; the screen routed 16/18 bare and 18/18 with the rule, never asking which playbook.
- **Cons:** routing only, no orchestration (owner): adding orchestration is what improves the experience, because meaningful work starts at once; the screen also measured the routing answer only, not whether the session invokes the playbook.
- **Complexity:** low.
- **Reversibility:** high.

### A dedicated entry: an intro playbook or a config key

Option C: a new `intro` playbook as the session's entry, routing to the others. Option D: a key `core.entry_playbook` naming the playbook the hook sends project work to.

- **Pros:** C is an entry shaped only for routing, light to render; D is overridable per tier today, unlike rules, which have no cross-tier override, so a project or user could pick its own entry.
- **Cons:** routing only, no orchestration (owner); C is also a new playbook to author and test, D a new config key.
- **Complexity:** medium.
- **Reversibility:** high.

### Always the project-manager

Option E: the decision above.

- **Pros:** one contact that routes, organises and carries the work through groom, develop, review and merge, escalating to the owner when needed ([value/0019](../value/0019-projects-are-built-along-a-roadmap.md)); knows the specs out of the box; meaningful work starts at once; reuses an existing playbook; the hook change is prose only.
- **Cons:** the manager today classifies only tiny fix, plan, question and decision, so until OI-0036 narrow requests — a retro, docs, a PR description, a benchmark — are squeezed into those classes; about 5K tokens per entry, the manager render plus a `booping status` call ([value/0002](../value/0002-minimal-effective-context.md)) — not worth weighing against the quality gain (owner); two routing tables, the skill's and the manager's, until OI-0037 merges them ([value/0003](../value/0003-single-source.md)).
- **Complexity:** medium.
- **Reversibility:** high.

## Consequences

- The session-start hook's prose sends every request in the session, questions and debugging included, to `/booping:playbook project-manager` instead of offering a playbook.
- OI-0036 must deliver: the project-manager gains a route "a narrow playbook fits → run it" and launches and orchestrates every other playbook; it escalates a conflict it sees in a decision to the owner; it files open items for the tails a piece of work leaves behind; given "I have an hour", it walks the open items and the specs, collects the conflicts and surfaces the critical ones for the owner to answer.
- OI-0037: soldering the manager render and the playbook table into session start waits until the manager entry proves itself.
- "Proves itself" for OI-0037 is the owner's call after about three days of working with the manager entry, with no numeric measure; feedback during those days comes as corrections, and OI-0038 asks the owner on 2026-10-22 whether the entry works and whether to solder it in, unless the feedback has overturned the concept by then ([value/0010](../value/0010-proven-to-work.md)).
- Projects carry different levels of responsibility, so the manager's behaviour differs per project ([value/0009](../value/0009-adjustable-control.md)): a home pet project or a product-fit experiment, where breakage costs little and the agent writes as much as it can — the owner only stays aligned by looking at the ADRs and the corpus of records the decisions rest on, and corrects them; a project past proof of concept, where the owner works closer to the code and wants more control; and a production system handling money, attribution and payouts, where a loss is very costly and the owner reviews everything by eye. This is set per project through project-tier rules targeted at `project-manager`; no new mechanism is needed now (owner, 2026-10-19).
