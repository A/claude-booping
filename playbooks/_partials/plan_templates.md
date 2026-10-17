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
- `# Quality Checklist` — constraints the plan meets; read with the body, not walked as a separate pass.

Read the chosen file before drafting: neither section can be guessed from its catalogue line.

When no entry fits, author one at `{project}/plan_templates/{name}.md` first, then draft against
it — frontmatter (`name`, `description`) plus both top-level sections, generic for its surface
class: placeholders throughout, no path, milestone or story-point value from this run baked in.
Never draft into a bad-fit template, never improvise a shape and name a template after it.

The draft is one file, cut into `index.md` and the milestone files by `booping plan split`.

`summary` is yours:

```
booping set {plan-dir}/index.md summary="{one line}"
```

`sp` is not — never hand-write it.
