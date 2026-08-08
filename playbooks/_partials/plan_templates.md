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
