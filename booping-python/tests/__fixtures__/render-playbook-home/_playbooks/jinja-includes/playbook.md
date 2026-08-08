---
name: jinja-includes
title: Jinja Includes
summary: Fixture exercising the playbook include search chain.
trigger: when the user says jinja includes
jinja: true
graph:
  first: []
  second: [first]
---

# Jinja Includes Preamble

{% include "_references/rules.md" %}
