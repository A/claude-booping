---
name: design
title: Design
summary: "Owns the draft-design-with-the-user craft rule and the delegation table; iterates on architecture and trade-offs until the user aligns, before any plan is written."
agent: null
review_gate: "Design agreed? On a change request, re-enter this design step with the requested change, revise, and present again — do not move on to drafting. If the change needs facts you do not have, re-run the research wave first."
---
{% import "_partials/_available_agents.j2" as available_agents with context %}
{{ available_agents.render("groom") }}

## Design

Synthesize the research-wave output into a design the user signs off on. Nothing is written to a plan file in this step.

Cover, in this order:

1. **Approach** — the architecture and pattern choices, stated against the prior art the codebase research found. Name what is reused and what is new.
2. **Surface changes** — data, API, config, CLI, and UI surfaces that change: schemas, migrations, endpoints, config keys, env vars, flags.
3. **Trade-offs** — the open decisions, each with the options, the cost of each, and your recommendation. Where the web research produced competing approaches, present them here rather than picking silently.
4. **Out of scope** — what this work deliberately does not do.
5. **Risks** — what could invalidate the design, and the cheapest way to find out early.

Rules:

- Present the design and ask for a decision on every open trade-off. Iterate until the user is aligned — do not proceed to drafting on unanswered questions.
- If a decision needs a fact nobody has, say so and get it: delegate a bounded follow-up to an agent from the table above rather than guessing.
- Do not estimate, do not decompose into milestones, do not write the plan file — that is the next step.

## Output

- **Approach** — ≤ 10 lines.
- **Surface changes** — one line each.
- **Decisions** — one line per resolved trade-off, in the form `decision — rationale`.
- **Out of scope** / **Risks** — one line each.
