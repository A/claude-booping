{%- set _types = task_types | default(config.core.task_types, true) or [] -%}
{%- if _types -%}
| type | fits when | guidance |
| --- | --- | --- |
{% for t in _types -%}
| `{{ t.type }}` | {{ t.description | replace("|", "\|") | replace("\n", " ") }} | [guidance]({{ t.doc_uri }}) |
{% endfor -%}
{%- endif %}
