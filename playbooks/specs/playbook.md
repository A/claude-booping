---
name: specs
title: Specs
summary: Work the project's specs records — set up a tier, settle values, record decisions, ideas and rules, review the set, sync it with the code and work its open items.
trigger: anything about this project's specs — values, rules, ADRs, ideas, open items, a specs review or a specs-to-code sync
jinja: true
inline_steps: true
requires_project: true
---
The run keeps no state of its own. The `open_item` machine below tracks one open-item file each: its workdir is the vault, and only `booping specs open-items` moves it — never call `booping playbook-transition` for it, and never create a run workdir for it.

{% set playbook_agents = config.core.get('specs_playbook', {}) -%}
{% include "_partials/playbook_agents.md" %}

{% include "_partials/playbook_shared_instructions.md" %}
