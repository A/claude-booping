{% set _lts_model_tiers = ["opus", "sonnet", "haiku", "fable"] -%}
{%- set _lts_wanted = (config.get("targets_for") or "") | replace(" ", "") -%}
{%- set _lts_wanted = _lts_wanted.split(",") | reject("equalto", "") | list -%}
{%- set _lts_selected = context.playbooks | selectattr("name", "in", _lts_wanted) | list -%}
{%- if _lts_selected -%}
## Lesson Targets
{% for _lts_pb in _lts_selected %}
### {{ _lts_pb.name }}

{% set _lts_steps = _lts_pb.steps | sort(attribute="name") -%}
| Step | Summary |
| --- | --- |
{% for _lts_step in _lts_steps -%}
| `{{ _lts_pb.name }}/{{ _lts_step.name }}` | {{ _lts_step.summary | replace("\n", " ") | replace("|", "\\|") | trim }} |
{% endfor %}
{%- set _lts_lessons = [] -%}
{%- for _lts_lesson in context.targeted_lessons -%}
{%- if _lts_lesson.parsed_targets | selectattr("playbook", "equalto", _lts_pb.name) | list -%}
{%- set _ = _lts_lessons.append(_lts_lesson) -%}
{%- endif -%}
{%- endfor -%}
{%- if _lts_lessons %}
**Lessons:**

{% for _lts_lesson in _lts_lessons -%}
- {{ _lts_lesson.title }} — {{ (_lts_lesson.frontmatter.get("summary") or _lts_lesson.body.strip().split("\n")[0]) | replace("\n", " ") | trim }}
{% endfor %}
{%- endif -%}
{%- set _lts_agents = [] -%}
{%- set _lts_seen = [] -%}
{%- for _lts_id, _lts_spec in (config.skills.get(_lts_pb.name, {}) or {}).get("agents", {}).items() -%}
{%- set _ = _lts_seen.append(_lts_id) -%}
{%- set _ = _lts_agents.append((_lts_id, (_lts_spec.good_for or []) | join("; "))) -%}
{%- endfor -%}
{#- a `detached` naming a model tier, or one still carrying an unrendered config
    expression, is not an addressable agent id — only named agents are targets -#}
{%- for _lts_step in _lts_steps -%}
{%- set _lts_detached = _lts_step.detached or "" -%}
{%- if _lts_detached and _lts_detached.split(":")[0] not in _lts_model_tiers and "{" not in _lts_detached and _lts_detached not in _lts_seen -%}
{%- set _ = _lts_seen.append(_lts_detached) -%}
{%- set _ = _lts_agents.append((_lts_detached, "performs step " ~ _lts_pb.name ~ "/" ~ _lts_step.name)) -%}
{%- endif -%}
{%- endfor -%}
{%- if _lts_agents %}
**Agents:**

{% for _lts_id, _lts_responsibilities in _lts_agents -%}
- `agent:{{ _lts_id }}` — {{ _lts_responsibilities }}
{% endfor %}
{%- endif -%}
{% endfor %}
{%- endif -%}
