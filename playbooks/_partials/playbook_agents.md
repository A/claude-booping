{%- set _cfg = playbook_agents | default({}, true) -%}
{%- set _agents = _cfg.get("agents", {}) or {} -%}
{%- set _hide_internal = _cfg.get("disable_internal_agents", False) -%}
{%- macro cell(items) -%}
{{ (items or []) | map("replace", "|", "\|") | map("replace", "\n", " ") | join("; ") or "—" }}
{%- endmacro -%}
{%- if _agents %}
## Available Agents

Delegate heavy reads to the agents below, under the return contract the step states — the step
itself stays yours. Never delegate to an agent that is not on this list.

| agent | good for | bad for |
| --- | --- | --- |
{% for agent, spec in _agents.items() -%}
{%- if not (_hide_internal and spec.get("internal", False)) -%}
| `{{ "booping:" ~ agent if spec.get("internal", False) else agent }}` | {{ cell(spec.good_for) }} | {{ cell(spec.bad_for) }} |
{% endif -%}
{%- endfor -%}
{%- endif %}
