# Agent wiring

How extra context flows from project artifacts into skill orchestrators and sub-agents.

## Skill orchestrator startup (Phase 0)

Every skill, before Phase 1:

1. **Resolve the project** — `.booping-project` marker → `~/Claude/.booping/projects.json` → ask the user. Store the name in context as `{project}`.
2. **Read project-local skill extension** — `~/Claude/{project}/_booping/skill_<name>.md` if it exists (name is hardcoded per skill). Merge its rules on top of the plugin-shipped SKILL.md.
3. **Read the lesson index** — enumerate `~/Claude/{project}/lessons/*.md`, read each file's frontmatter + body. Hold them in context for filtering when briefing workers.

## Lesson domain classification

Every lesson file has `domain:` in its frontmatter. Values:

| Domain | Rule type | Examples |
|--------|-----------|----------|
| `tech` | Architecture, design patterns, framework usage | SOLID principles, injection-seam, backend-protocol, repository vs ORM |
| `product` | Requirements, scope, business-goal framing | "always ask the user problem before solutioning", "business goal must be user-visible" |
| `qa` | Testing strategy, coverage, regression | "integration tests over mocked DB", "migration replay test required" |
| `code` | Worker-level code discipline | Boy Scout Rule, monkey-patch smell, flag unexpected test passes |
| `all` | Cross-cutting, applies to every agent | "lessons are load-bearing", "no TBD in plans" |

Missing `domain:` in legacy lessons is treated as `all` until `/learn` backfills them.

## Per-agent domain filter

When the orchestrator spawns a sub-agent, it filters the in-context lesson set and cites only the relevant files in the briefing.

| Agent | Domains passed |
|-------|----------------|
| `booping-teamlead` | all (synthesizer) |
| `booping-techlead` | `tech`, `code`, `all` |
| `booping-product-manager` | `product`, `all` |
| `booping-qa-lead` | `qa`, `all` |
| `booping-developer-junior` | `code`, `tech`, `all` |
| `booping-developer-middle` | `code`, `tech`, `all` |
| `booping-developer-senior` | `code`, `tech`, `all` |
| `booping-reviewer` | `code`, `tech`, `all` |

Within the filtered set, the orchestrator further narrows by relevance to the specific task before citing paths — a lesson about Django migrations doesn't go into a frontend-only task's briefing even if it's `tech`.

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
- `Applicable lessons` — pre-filtered by the domain map above and task-relevance. Paths relative to `project_root`.

> **Developer-agent exception:** All three developer agents (`booping-developer-junior`, `booping-developer-middle`, `booping-developer-senior`) share a single extension at `~/Claude/{project}/_booping/agent_booping-developer.md` (not per-tier). The orchestrator passes this single path as `agent_extension` regardless of which tier is briefed.

## Agent startup

Every agent's file contains a **Startup** section that runs before any other action:

1. If the briefing supplies `agent_extension`, read it — those are rules written by `/learn` for this specific agent in this project.
2. Read every path under `Applicable lessons:`. Do not read the full `lessons/` directory — trust the orchestrator's filtering.
3. Proceed with the agent-specific workflow.

This is the only place an agent crosses the project boundary. Workers never scan `~/Claude/{project}/lessons/` themselves.

## Why this split

- **Skills** hold methodology (how to groom, how to develop) — cross-project, shipped with the plugin.
- **Project-local extensions** (`_booping/skill_*.md`, `_booping/agent_*.md`) hold project-shape calibration (SP thresholds, deploy checklists, agent-specific code patterns).
- **Lessons** hold experience — concrete incidents distilled into triggers + checks — tagged by domain so the right agent sees them.

A product manager agent reviewing a requirements spec doesn't need to know about SOLID; a be-dev implementing a migration doesn't need to know about business-goal framing. Domain tags keep each agent's briefing tight.
