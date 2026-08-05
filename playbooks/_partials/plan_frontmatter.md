{% from "_partials/timestamps.md" import human_ts -%}
{% raw %}---
title: {Descriptive Title}
type: feature | bug | refactoring
status: framing                  # the run machine's status — written by `booping playbook-transition`, never by hand
sp: {total}                      # sprint total, summed from milestone totals
split_from: null                 # sibling stubs only: path to the primary plan this was split from
{% endraw %}created: {{ human_ts }}{% raw %}        # when the plan directory was created — the run's clock, to the minute
planned: null                    # date keys — owned by the run machine's edge hooks, same shape as `created`
started: null
completed: null
retro: null
goal: null
summary: ""                      # one-line plan intent for search + plan listings (≤ ~120 chars)
commit: null
---{% endraw %}
