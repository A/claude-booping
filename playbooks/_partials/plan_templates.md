## Available plan templates

Pick the entry whose name and description match the **dominant surface** of the work — the surface
most of the milestones land on. A near miss loses on that surface, not on taste.

{% if context.plan_templates -%}
| Name | Source | Description | Read from |
| --- | --- | --- | --- |
{% for t in context.plan_templates -%}
| `{{ t.name }}` | {{ t.source }} | {{ (t.description or "—") | replace("|", "\|") | replace("\n", " ") }} | `{{ "${CLAUDE_PLUGIN_ROOT}/" if t.source == "core" }}{{ t.path }}` |
{% endfor -%}
{%- else %}
_No plan templates found — author one before drafting._
{%- endif %}
Each template is one file with two top-level sections:

- `# Plan Body` — the structure the plan is written against, section for section, in its order.
  None dropped, none extra.
- `# Quality Checklist` — walked item by item against the plan as written, before the plan is
  returned. An unsatisfied item is fixed, not reported as satisfied.

Read the chosen file before drafting: neither section can be guessed from its catalogue line.

When no entry fits, author one at `{project}/plan_templates/{name}.md` first, then draft against
it — frontmatter (`name`, `description`) plus both top-level sections, generic for its surface
class: placeholders throughout, no path, milestone or story-point value from this run baked in.
Never draft into a bad-fit template, never improvise a shape and name a template after it.

A plan is two surfaces: the run's `index.md`, already carrying its frontmatter and title, holding the template's top-level sections under them; and one file per milestone, written as [Write the milestone files](#write-the-milestone-files) describes, against the template's milestone-file section.

`summary` is yours:

```
booping frontmatter-update {plan-dir}/index.md summary="{one line}"
```

`sp` is not — never hand-write it.
