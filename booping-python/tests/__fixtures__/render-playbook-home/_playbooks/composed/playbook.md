---
name: composed
title: Composed Playbook
summary: Fixture exercising graph-driven step rendering.
trigger: when the user says composed
graph:
  gather: []
  draft: [gather]
  named-step: [gather]
  plain: [draft, named-step]
---

# Composed Procedure

Plain prose preamble that must pass through verbatim, including this literal
token: {{ leftover }} — no Jinja evaluation happens here.
