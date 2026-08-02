{%- set _skill = agents_skill | default("groom") -%}
{%- set _cfg = config.skills.get(_skill, {}) or {} -%}
{%- set _agents = _cfg.get("agents", {}) or {} -%}
{%- set _hide_internal = _cfg.get("disable_internal_agents", False) -%}
{%- if _agents %}
## Available Agents

Delegate heavy reads to the agents below, under the return contract the step states — the step
itself stays yours. Never delegate to an agent that is not on this list.

{% for agent, spec in _agents.items() %}
{%- if not (_hide_internal and spec.get("internal", False)) %}
### `{{ agent }}`

Invoke via the `Agent` tool with `subagent_type="{{ "booping:" ~ agent if spec.get("internal", False) else agent }}"`. Pass the briefing in the `prompt` arg.

{% if spec.good_for %}
**Good for:**
{% for t in spec.good_for -%}
- {{ t }}
{% endfor %}
{% endif -%}
{% if spec.bad_for %}
**Bad for:**
{% for t in spec.bad_for -%}
- {{ t }}
{% endfor %}
{% endif -%}
{%- endif -%}
{% endfor -%}
{%- endif %}
