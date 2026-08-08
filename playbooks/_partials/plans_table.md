{%- set _rows = (query_plans | query) -%}
{%- set _limit = plans_limit | default(10) -%}
{%- if _limit %}{% set _rows = _rows[:_limit] %}{% endif -%}
{%- if _rows %}
| state | name | summary | path |
| --- | --- | --- | --- |
{% for plan in _rows -%}
| {{ plan.status | replace("|", "\|") | replace("\n", " ") }} | {{ plan.title | replace("|", "\|") | replace("\n", " ") }} | {{ plan.summary | replace("|", "\|") | replace("\n", " ") }} | [plan]({{ plan.path }}) |
{% endfor -%}
{%- else %}
No plans filed.
{%- endif %}
