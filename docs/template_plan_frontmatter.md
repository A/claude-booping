---
title: {{Descriptive Title}}
type: feature | bug | refactoring
status: in-spec                  # active groom runs write directly here; parked ideas and split stubs start in `backlog`
sp: {{total}}
split_from: null                 # sibling stubs only: path to the primary plan this was split from
created: YYYY-MM-DD              # date this file was first written
planned: null                    # set when transitioning in-spec → awaiting-plan-review (draft finalized)
started: null                    # set when transitioning ready-for-dev → in-progress (/develop claims)
completed: null                  # set on terminal transition (done/fail/cancelled) or entry to awaiting-retro
retro: null                      # path to retrospective file, set by /retro
goal: null                       # success | partial | fail — set by /retro
business_goal: ""                # features and refactorings: user/internal-visible outcome
---