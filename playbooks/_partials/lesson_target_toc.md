## Lesson Target Space

Every lesson targets exactly one entry from the target space, written into its `targets:` frontmatter list. Entry forms — exact names only, no globs, no wildcards, no negation:

- `{playbook}` — the whole playbook, e.g. `{{ context.playbooks[0].name if context.playbooks else "groom" }}`
- `{playbook}/{step}` — one step of it, e.g. `{{ context.playbooks[0].name ~ "/" ~ context.playbooks[0].steps[0].name if context.playbooks and context.playbooks[0].steps else "groom/intake" }}`
- `agent:{id}` — one agent, e.g. `agent:booping-developer`

The table of contents below is the whole space. Pick the playbooks a candidate actually touches and fetch their targets — step summaries, lessons already targeting them, addressable agents — with the command on each entry. Several names fetch in one call: `--set targets_for=a,b`.
{% for _ltc_pb in context.playbooks %}
### {{ _ltc_pb.name }}

{{ _ltc_pb.summary | replace("\n", " ") | trim }}

- Steps: {% for _ltc_step in _ltc_pb.steps | sort(attribute="name") %}`{{ _ltc_step.name }}`{{ ", " if not loop.last else "" }}{% else %}—{% endfor %}
- Targets: `booping render playbooks/_partials/lesson_target_space.md --set targets_for={{ _ltc_pb.name }}`
{% endfor %}
