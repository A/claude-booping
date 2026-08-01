---
summary: Pick the plan template matching the dominant surface and write the plan
  against its Plan Body — milestones, tasks with DoD and Verify, story points 
  per task / milestone / sprint, `sp` and `summary` frontmatter; verify against 
  the template's Quality Checklist, then cross-review the draft when the project
  configures a reviewer and fold the findings in.
detached: opus:high
review_gate: null
inputs:
- what: the settled design — the chosen architecture and why it won, the data / 
    API / config / CLI surface changes, the alternatives rejected, the trade-off
    calls the user made, and the risks with their mitigations
- what: the confirmed framing — the restated problem, the task type, the scope 
    boundaries and the user's answers to the scope-challenge questions
- what: the blast radius — the files, modules, integrations and external 
    surfaces the work touches, with the prior art and conventions already in 
    play
- from: the attached project
  what: the plan-template catalogue — each template's name, its description and 
    the location to read its Plan Body and Quality Checklist from
- from: the attached project
  what: the plan frontmatter shape — every key, its type and its default
- from: the attached project
  what: the sizing scale — what each story-point value means — and how many 
    consecutive milestones a development run bundles into one agent briefing, 
    which bounds how large a milestone may be
- from: the attached project's config
  what: whether a cross-review agent is configured, and which agent it names
outputs:
- "plans/{slug}.md — the plan written against the chosen template's Plan Body, section
  for section: milestones carrying a goal, a Verify, a task table with exact file
  paths and per-task story points, and a checkbox DoD per task; `sp` and `summary`
  frontmatter set; always [UPDATED], never created or renamed"
- "cross-review findings folded into the plan, deferrals recorded one line each in
  `## Risk register`, and a finding that reopens a settled design call left out of
  the plan entirely and returned as a note instead"
- "a plan template authored under the project's `plan_templates/` when no catalogue
  entry fits the dominant surface"
- "the chosen template and the sprint total, the milestone and story-point breakdown,
  the Quality-Checklist verdict, and the cross-review outcome — findings by severity,
  what was folded in, what was deferred, or the line that no cross-review agent is
  configured"
reviewed_at: 20260731 20:19
---

{% include "opus-5.md" %}
