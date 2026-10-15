---
name: specs
title: Specs
summary: Work the project's specs records — set up a tier, settle values, record decisions, ideas and rules, review the set, sync it with the code and work its open items.
trigger: anything about this project's specs — values, rules, ADRs, ideas, open items, a specs review or a specs-to-code sync
jinja: true
inline_steps: true
requires_project: true
---
{% set specs = config.core.specs -%}
Specs are typed records about why the project is the way it is; every type, its frontmatter and the principles behind the set are in [the specs format guide](${CLAUDE_PLUGIN_ROOT}/{{ specs.format }}/README.md) — read it before writing a record.

Tiers (`core.specs.tiers`; every `booping specs` verb takes `--tier`, default `project`):

{% for tier in booping.specs_tiers -%}
- `{{ tier.name }}` — `{{ tier.root }}`{% if tier.namespace %}, namespace `{{ tier.namespace }}`{% endif %}.
{% endfor -%}
{% if booping.specs_tiers | selectattr('name', 'equalto', 'project') | list | length == 0 -%}
- `project` — none: no repo is attached.
{% endif %}
Writing a record:

- Number it with `booping specs next {type}`.
- Set `created_by: claude`; never set `reviewed`.
- Run `booping specs check` after every write and fix what it reports.

The run keeps no state of its own. The `open_item` machine below tracks one open-item file each: its workdir is the vault, and only `booping specs open-items` moves it — never call `booping playbook-transition` for it, and never create a run workdir for it.

{% set playbook_agents = config.core.get('specs_playbook', {}) -%}
{% include "_partials/playbook_agents.md" %}

{% include "_partials/playbook_shared_instructions.md" %}
