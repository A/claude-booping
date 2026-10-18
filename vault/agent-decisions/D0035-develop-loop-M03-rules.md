---
step: "develop/develop-loop"
asked: "M03 DoD wants rule/0037 under ## Rules in the --step intake render, but playbook-level targets inject only into the full render \u2014 retarget the rule or accept?"
decision: "Accepted as met: rule/0037 keeps targets [project-manager, specs] (owner decision 4) and shows under ## Rules of render-playbook project-manager, whose inline_steps body is how intake runs"
why: "project-manager is inline_steps: true and intake is runner-performed, so the full render\u0027s rules bind the step; adding a project-manager/intake target would depart from the owner\u0027s targets decision"
state: open
session: "6b1a350c-f2b9-578a-8dd5-509a79cd2988"
logged_at: "2026-10-19 03:23"
artifact: "plans/202610190307_core-rules-open-item-filter-and-staged-experiments/index.md"
---
