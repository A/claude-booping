---
title: {{Descriptive Title}}
type: feature | bug | refactoring
status: framing                  # the owning playbook's run status — written by `booping playbook-transition`, never by hand
sp: {{total}}
split_from: null                 # sibling stubs only: path to the primary plan this was split from
created: YYYY-MM-DD HH:MM        # when this file was first written — the grooming run's clock, to the minute
planned: null                    # date keys — owned by the run machines' edge hooks, same YYYY-MM-DD HH:MM shape
started: null                    # set by the develop run machine when the sprint starts
completed: null                  # set by the develop run machine when the sprint ends
code_reviews: null               # list of code-review artifact paths, appended by the code-review playbook
sessions: []                     # Claude Code session ids, appended by the groom and develop edge hooks
retro: null                      # path to retrospective file, set by the retro playbook
goal: null                       # success | partial | fail — set by the retro playbook
summary: ""                      # one-line plan intent for search + plan listings (≤ ~120 chars)
commit: null                     # repo HEAD, snapshotted by the develop run machine at sprint entry
---

