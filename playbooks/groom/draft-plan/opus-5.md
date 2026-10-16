# Draft the plan

Produce an implementation plan an autonomous developer agent will execute milestone by milestone in the attached repository, from the framing this conversation carries. Change no repository file. `{plan-dir}` is the preamble's `Plan dir:` line, `{slug}` its last segment. Work in four stages.

## 1. Research

Read the code the request touches and anything it depends on; delegate bulk reads to `{{ config.core.research_agent }}`. Post the facts, each with its file path, in chat, then advance the run to `drafting`.

## 2. Draft

Pick the template ([Available plan templates](#available-plan-templates)) and write the whole plan to `{plan-dir}/draft.md`: every section of its `# Plan Body`, in its order, the milestones under `## Milestones` in this format:

```
### M{nn} — {title}

sp: {n}
depends_on: [M{nn}, …]
{% for name in config.core.groom_playbook.split.sections %}
#### {{ name }}
{% endfor %}```

- `{nn}` is the milestone's position in execution order, two digits; `sp` is 1–5, `depends_on` is `[]` when nothing precedes it.
- Each milestone has one Verify command scoped to that milestone; the whole-repo check goes only in Final Verification.
- Decide what the code and the request settle, and record each assumption in the plan. A call only the user can make goes to the user: in a supervised run ask it in chat; in an autonomous run write it to `clarifications.md` (format: `${CLAUDE_PLUGIN_ROOT}/docs/clarifications.md`) and park the run on `awaiting-clarification`.
- Sprint total past **{{ config.core.sprint.default_threshold_sp }} SP** — offer the user a split at a dependency seam (the first slice shippable on its own, each later one useless without it), keep only the first slice that fits the threshold in this plan, and park the rest as sibling stubs to be groomed in their own runs. They may decline and keep one plan.

## 3. Split

```
booping plan split {plan-dir}/draft.md --replace
```

Exit 3 (no milestone heading) or 4 (written with `flag:` lines) — the draft is off-format.
{%- if config.core.groom_playbook.split_fallback_agent %} Spawn a `general-purpose` sub-agent with model and effort `{{ config.core.groom_playbook.split_fallback_agent }}`, handing it `draft.md`'s path, the split's stderr and the format above: it rewrites the draft into that format at `/tmp/booping-split-{slug}/draft.md` and writes nothing in the vault.{% else %} Rewrite the draft into the format above yourself at `/tmp/booping-split-{slug}/draft.md`.{% endif %} Copy that file over `{plan-dir}/draft.md` and split again. Exit 1 or 2 — stop and report the `error:` line.

## 4. Check

```
booping plan check {plan-dir}
```

Exit 1 — fix the milestones its findings name in `draft.md`, then back to stage 3. At most three rounds; findings left after the third are carried to `present`.

Then set the summary — one line of plain plan intent, ≤ ~120 chars / ~20 words:

```
booping frontmatter-update {plan-dir}/index.md summary="{one line}"
```

`sp` is not yours — split stamps it.

## Hard rules

- Never edit files outside `{project}/plans/`.
- User approval is **explicit** — "looks good" is enough; silence is not.

{% include "_partials/plan_templates.md" %}

{% include "_partials/sprint_planning.md" %}
