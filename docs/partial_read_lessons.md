Every skill loads the lesson set up front so the active rules are live in context for the session.

## Read all lessons

Enumerate `~/Claude/{project_name}/lessons/` and read every file in full (frontmatter + body). Don't sample; don't skip. Load everything — there is no scope filter; lessons are shared across all skills.

## Log to the user

After reading, print a short summary so the user can see which rules govern this session:

```
Loaded N lessons:
  0001 — {{title}}
  0002 — {{title}}
  ...
```

If zero lessons are present, say so explicitly (e.g. "No lessons loaded — vault has not accumulated any yet."). The log happens once per skill run, at the end of Preflight.

## Surface conflicts

Hold every loaded lesson in context for the remainder of the session. When a lesson conflicts with a user request, a plan decision, or an in-progress task, stop and flag it to the user before continuing. Never silently violate a loaded lesson.

## Pass to sub-agents

When the skill delegates to a sub-agent, pick the subset of lessons relevant to that agent's task and include their paths under `Applicable lessons:` in the briefing. The orchestrator does the relevance judgment; the agent trusts the filtered list and reads only those.
