---
name: jinja-composed
title: Jinja Composed
summary: Fixture exercising opt-in Jinja rendering.
trigger: when the user says jinja composed
jinja: true
graph:
  first: []
  second: [first]
---

# Jinja Preamble

Preamble threshold: {{ config.core.sprint.default_threshold_sp }}

{% include "_partials/_project_context.j2" %}
