# Decisions

`[2026-08-02 12:14]` Migrating the existing `/retro` skill into a playbook, now that the develop and groom playbooks have landed.
`[2026-08-02 12:14]` The retro artifact lives next to the plan, in the plan directory.
`[2026-08-02 12:14]` The retro's main artifact stays the plan itself.
`[2026-08-02 12:14]` The retro playbook is bound to its plan statuses.
`[2026-08-02 12:14]` Evals are explicitly out of scope for this run — no llm-tests, fixtures, step-suite, smoke-optimizer or regress-optimizer work. Evals will be done later.
`[2026-08-02 12:14]` User wants a review ping when the briefing is done, and again when the migration is finished.
`[2026-08-02 12:14]` Runner proposal (pending user confirm at the manifest gate): destination root is the core plugin root `/home/anton/Dev/@A/claude-booping/playbooks/`, matching the groom and develop playbooks.
`[2026-08-02 12:14]` Multi-plan runs are kept: a retro run may cover several plans; the shared retrospective artifact lands in the primary plan's directory and the sibling plans link to it.
`[2026-08-02 12:14]` The canonical `/retro` skill stays untouched and ships in parallel with the playbook, same as `groom` and `develop`. No `src/config.yaml` edits, no rewrite of the `retro=retrospectives/...` frontmatter hook, no skill retirement.
`[2026-08-02 12:14]` The retrospective artifact is a file named `retro.md` in the plan directory — `{vault}/plans/{slug}/retro.md`. In a multi-plan run it lives at `{vault}/plans/{primary-slug}/retro.md` and the sibling plans link to it.
`[2026-08-02 12:14]` At the brief gate the user confirmed the brief and instructed the run to continue without further review gates — do not ask for review at the remaining gates.
`[2026-08-02 12:14]` The run stops when the step prompts are done: no eval work (llm-tests, fixtures, step suites, smoke/regress optimizers) is performed in this run.
`[2026-08-02 23:35]` Step bodies mirror the skill's phases verbatim, with only the deviations a playbook step needs (phase cross-refs become step names, lessons rendered in-step). `mine-issues` and `triage-issues` are retired: `prepare` is built exactly on the skill's Phase 1, and `gather-feedback` absorbed Phase 2b (issue triage + per-plan goal verdicts), mirroring Phase 2 whole. Graph: intake → prepare → gather-feedback → research-issues → synthesize → save.
`[2026-08-02 23:35]` `research-issues` is built exactly on the skill's Phase 3. The playbook-invented `## What the step leaves behind` report format and the "lesson verdict" machinery are removed; lesson-tagged findings take the retrospective template's short `### Lesson gaps` shape.
`[2026-08-02 23:35]` The retrospective template moved out of the eagerly-embedded `_partials/_retrospective_template.j2` into the lazy-loaded `docs/retrospective_template.md`; both the `/retro` skill and the playbook's `synthesize` read it at draft time. Amends "the canonical `/retro` skill stays untouched": the skill body now carries the lazy link instead of the embedded template (behaviour otherwise unchanged).
`[2026-08-02 23:35]` The save closing report carries, per plan, a table of the issues reported into the retro with their root causes and action items.
