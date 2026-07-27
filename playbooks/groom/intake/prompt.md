---
name: intake
title: Intake
summary: "Owns project context, task classification, and the challenge-scope craft rule; ends with the literal web-research flag line that decides whether research-web runs."
agent: null
review_gate: null
---
{% import "_partials/_task_classification.j2" as task_classification with context %}
{% include "_partials/_project_context.j2" %}

{{ task_classification.render() }}

## Intake

1. Restate the request in one or two sentences. Name the outcome the user wants, not the implementation.
2. Classify the work per Task Classification above and load the matched type's linked doc before going further.
3. **Challenge scope**: ask upfront what new components, dependencies, APIs, or workflow changes this likely needs. Surface anything the request implies but does not say — new services, schema changes, migrations, config surfaces, permissions, user-visible copy, rollout steps.
4. Ask the user the open questions this raises. Wait for answers; do not assume defaults on anything that changes the shape of the work.
5. Decide whether web research is warranted. Answer **yes** when any of these hold:
   - the request names an external reference that must be checked against current docs — package version, image tag, API endpoint, CLI flag, config option;
   - the work is novel or non-obvious for this codebase and competing approaches / known pitfalls should be compared before design locks;
   - a third-party service, protocol, or standard the repo does not already encode is involved.

   Otherwise **no** — work entirely inside the existing codebase and its conventions.

## Output contract

Return, in this order:

- **Request** — the restated request, 1–2 sentences.
- **Type** — the chosen task type.
- **Scope answers** — the user's answers to the scope questions, one line each.
- **Codebase unknowns** — what `research-codebase` must map: named files, modules, integrations, surfaces.
- **Web unknowns** — what `research-web` must verify or compare, one line each. Empty when the flag below is `no`.
- Then, as the **last line of the output and nothing after it**, exactly `web-research: yes` or exactly `web-research: no`.

That last line must be byte-exact: bare text, no bold, no code fence, no bullet marker, no trailing punctuation, nothing after it. The driver parses only this literal line — a mention of web research anywhere else in the output is not the flag.
