---
type: reference
title: "Postmortem: the budget gate slipped into the core unasked"
summary: On 2026-10-15 a usage-limit gate the owner never asked for reached the core through a one-line mention, a package approval and autonomous runs; removed on 2026-10-17.
created_by: claude
created_at: 2026-10-17
updated_at: 2026-10-18
status: live
tags: [postmortem]
---

## Facts

- 2026-10-15 07:14–07:18 UTC, orchestrator session 36dbf90d (hermes-pet): the owner asked to fold `orchestrate` and `backlog-run` into one core playbook; usage limits were not mentioned.
- ~07:21: a research subagent listed backlog-run's budget gate as one of its unique mechanics and recommended carrying budget and window gates into autonomous mode.
- The agent passed it to the owner as one line in prose — «autonomous: гейт бюджета, ночное окно, пачки по размеру» — and asked whether to keep the nightly timer; the question was never answered.
- 08:12: the owner approved the package («Ну вроде ок все, давай планируй»); 30 s later adr/0028 was committed with "carries over backlog-run's budget and window gates, pause and resume", under "The owner settled the shape".
- 13:49: the orchestrator agent, not the owner, wrote the request of plan 202610152053_project-manager-autonomous-extras; groom and develop ran autonomously, the plan was approved by the run itself ("the owner was unavailable"), with no code review and no retro.
- The values the plan cited (value/0015, value/0009, value/0007, value/0005, value/0006) justified how the gate was built, never whether booping should have one; no value then marked a scope boundary.
- 2026-10-17 the owner ruled usage limits out of scope (adr/0028, value/0017); removal is OI-0004, done on 2026-10-18. On 2026-10-18 adr/0028 itself, a decision with no real alternative, gave way to value/0019 and story/0023.
- Causes: the agent's own proposal was buried in prose instead of a list the owner could accept line by line; an unanswered question counted as a yes; adr/0028 attributed agent proposals to the owner, against rule/0002; nothing in the values said what booping does not do.
- Remedies: booping:rule/0033 (decisions listed for acceptance), value/0017 and the value/0006 / value/0018 split (scope boundary).

## How to check

- Transcript /home/anton/.claude/projects/-home-anton-Dev--A-hermes-pet/36dbf90d-0102-4f43-add1-4a69775c2e2f.jsonl around 2026-10-15T07:14–08:20Z.
- vault/plans/202610152053_project-manager-autonomous-extras/{request.md,clarifications.md}; commit 1e4dfd6 (adr/0028).
