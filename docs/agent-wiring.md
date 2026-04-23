# Agent wiring

How extra context flows from project artifacts into skill orchestrators and sub-agents.

## Skill orchestrator startup (Phase 0)

Every skill, before Phase 1:

1. **Resolve the project** — `.booping-project` marker → `~/Claude/.booping/projects.json` → ask the user. Store the name in context as `{project}`.
2. **Read project-local skill extension** — `~/Claude/{project}/_booping/skill_<name>.md` if it exists (name is hardcoded per skill). Merge its rules on top of the plugin-shipped SKILL.md.
3. **Read all lessons** per [docs/partial_read_lessons.md](partial_read_lessons.md) — load every file under `~/Claude/{project}/lessons/`, log a summary to the user, hold the set in context for relevance filtering when briefing workers.

## Briefing template

Every briefing sent via `Agent()` starts with this header:

```
project_root: ~/Claude/{project}
agent_extension: ~/Claude/{project}/_booping/agent_<agent-name>.md

Applicable lessons:
- lessons/0007_injection-seam.md
- lessons/0012_backend-protocol.md
- ...

Task / goal: ...
Decisions that apply: ...
Files you may touch: ...
```

- `project_root` — the resolved project vault path. The agent uses this to locate its own extension.
- `agent_extension` — the exact path the agent should read (if it exists). Computed by the orchestrator using the agent's own name.
- `Applicable lessons` — a subset of the loaded lesson set, filtered by the orchestrator for relevance to this specific task. Paths are relative to `project_root`.

> **Developer-agent exception:** All developer agents share a single extension at `~/Claude/{project}/_booping/agent_booping-developer.md` (not per-tier). The orchestrator passes this single path as `agent_extension` regardless of which tier is briefed.

## Agent startup

Every agent's file contains a **Startup** section that runs before any other action:

1. If the briefing supplies `agent_extension`, read it — those are rules written by `/learn` for this specific agent in this project.
2. Read every path under `Applicable lessons:`. Do not read the full `lessons/` directory — trust the orchestrator's filtering.
3. Proceed with the agent-specific workflow.

This is the only place an agent crosses the project boundary. Workers never scan `~/Claude/{project}/lessons/` themselves.

## Why this split

- **Skills** hold methodology (how to groom, how to develop) — cross-project, shipped with the plugin.
- **Project-local extensions** (`_booping/skill_*.md`, `_booping/agent_*.md`) hold project-shape calibration (SP thresholds, deploy checklists, agent-specific code patterns).
- **Lessons** hold experience — concrete incidents distilled into triggers + checks — loaded once per skill run and passed to agents on a per-briefing relevance basis.

The orchestrator judges which lessons each agent needs for the task at hand, rather than classifying lessons up front. That keeps the briefing tight without adding a classification layer that can drift.
