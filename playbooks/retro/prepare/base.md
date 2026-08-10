Read each plan in the working set in full — `index.md` plus `{{ config.core.plans.milestones.glob }}` beside it — for **context only**: scope, SP totals, dates, decisions on record. The plan is a reference for understanding issues that surface in the later steps, not a target for orchestrator analysis (no derived "decisions deviated" / "tech debt" / "coverage gap" findings — the user owns issue identification; the step does homework and suggests options).

{{ tools.render('src/templates/_partials/_lessons.j2') }}

In parallel, delegate two reads per the agent roster above. Pass the lesson set verbatim with each brief (use the `Lessons` block already loaded above).

**A. Session-log mining** — execution-stage extraction:

{% include "_partials/_session_log_extraction.j2" %}

**B. Plan-stage lesson check** — separate brief, run in parallel with A:

{% include "_partials/_plan_lesson_check.j2" %}

The output of this step is the **issue list** — every tension, late change, code-feedback, execution-stage ignored-lesson, and plan-stage lesson-gap item from the agents' deliverables, held in context. Each item carries: source (tension / late change / code feedback / ignored lesson / plan-stage lesson gap), trigger, and a one-line orchestrator interpretation.

**Orchestrator cross-check** (still before `gather-feedback`): re-scan the lesson set and `_booping/skill_retro.md` against both agents' full output. Add any lesson-related item either agent missed; drop or correct any false positive. Use only what is in context — no additional loads.

Do **not** present this list to the user yet — `gather-feedback` runs first to avoid anchoring.
