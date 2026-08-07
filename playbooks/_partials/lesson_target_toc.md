## Targets

Every lesson names its targets in its `targets:` frontmatter list — exact names only, no globs, no wildcards, no negation:

1. `{playbook}` — the whole playbook. Target it when a lesson affects several of its steps.
2. `{playbook}/{step}` — one step. Target it when a lesson concerns that step alone.
3. `agent:{id}` — a core booping agent (researcher, developer). Target it when a lesson should guide the agent in everything it does.

The table of contents below is the whole space. Pick the playbooks a candidate actually touches and fetch their targets — step summaries, lessons already targeting them, addressable agents — with the command on each entry. Several names fetch in one call: `--set targets_for=a,b`.
{% for _ltc_pb in context.playbooks %}
### {{ _ltc_pb.name }}

{{ _ltc_pb.summary | replace("\n", " ") | trim }}

- Steps: {% for _ltc_step in _ltc_pb.steps | sort(attribute="name") %}`{{ _ltc_step.name }}`{{ ", " if not loop.last else "" }}{% else %}—{% endfor %}
- Targets: `booping render playbooks/_partials/lesson_target_space.md --set targets_for={{ _ltc_pb.name }}`
{% endfor %}
