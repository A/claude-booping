# booping

**A project-scoped sprint workflow for Claude Code — grooming, execution, retro, lessons — with mandatory sub-agent delegation so your main context never drowns in implementation detail.**

Most Claude Code plans disappear into session memory. booping makes them durable: every feature is groomed into a spec on disk, executed milestone-by-milestone by specialist sub-agents, reviewed in a retrospective against what actually shipped, and folded back into lessons that bind future sprints. Artifacts live under `~/Claude/{project}/` — one folder per codebase, no cross-contamination between a backend and a frontend you happen to work on the same day.

## Installation

### Development (fastest)

```bash
claude --plugin-dir /path/to/claude-booping/
```

Loads the plugin into the current session only.

### Via Claude Code marketplace (persistent)

```
/plugin marketplace add /path/to/claude-booping/
/plugin install booping@booping-local
```

The plugin ships with a `.claude-plugin/marketplace.json` so the second command works.

### Via git URL

```
/plugin marketplace add https://github.com/<you>/claude-booping
/plugin install booping@booping-local
```

After installing, `cd` into a repo and run `/install` to scaffold `~/Claude/{project}/`.

## Skills

| Slash | Purpose |
|-------|---------|
| `/help` | Tour of commands, agents, layout, workflow |
| `/install` | Scaffold `~/Claude/{project}/`, register the current repo |
| `/chat` | Read-only discussion over plans/retros/lessons |
| `/groom` | Spec a feature/bug/refactor into `plans/YYYYMMDD-*.md` with milestones, DoD, estimates |
| `/develop` | Execute a groomed plan milestone-by-milestone via sub-agents, update `sprints.md` |
| `/retro` | Compare plan vs built, gather feedback, produce a retrospective |
| `/learn` | Extract lessons from the retro into durable rules the next `/groom` and `/develop` will read |

## Sub-agents

Orchestrators — spawned by skills, never write application code:

| Agent | Role |
|-------|------|
| `booping-teamlead` | User-facing coordination, writes `sprints.md` and retrospective documents, tracks metrics |
| `booping-techlead` | Codebase research, blast radius mapping, tech-debt feedback |
| `booping-product-manager` | Validates requirements, web-research for alternatives, judges business-goal delivery |
| `booping-qa-lead` | Test strategy, regression risk, coverage review |

Workers — invoked from `/develop` per task:

| Agent | Role |
|-------|------|
| `booping-be-dev` | Backend (Python/Django/DRF/Rust/Axum/migrations/Temporal) |
| `booping-fe-dev` | Frontend (React/TypeScript/Leptos) |
| `booping-reviewer` | Milestone-diff review before merge |

## Artifacts tree

```
~/Claude/
├── .booping/
│   └── projects.json              # CWD → project mapping
└── {project}/
    ├── CLAUDE.md                   # project instructions
    ├── sprints.md                  # sprint registry — written ONLY by /develop
    ├── Notebook.md                 # active scratch pad
    ├── plans/                      # /groom output: YYYYMMDD-kebab-title.md
    ├── retrospectives/             # /retro output
    ├── lessons/                    # /learn output: {N}_{title}.md
    ├── notes/                      # freeform research, user stories
    ├── metrics/
    │   ├── lesson-hits.md          # how often each lesson was applied
    │   └── sp-rollup.md            # story points per sprint + monthly totals
    └── _booping/                   # project-local skill/agent extensions
        ├── skill_{name}.md         # read at the start of every invocation
        └── agent_{name}.md
```

## Use cases

Patterns observed across ~15 sprints on a real Django/DRF/Temporal backend.

**Multi-week feature programs.** A single feature takes 40-60 story points across model changes, migrations, workflow rewrites, and frontend alignment. booping keeps the original design visible in `plans/`, so after a weekend away you don't re-litigate decisions — you read the spec and resume.

**Tech-debt campaigns.** Extracting a service layer or migrating an LLM client touches dozens of files across multiple sprints. Each sprint has a narrow "Reduce technical debt" goal; `lessons/` catches the meta-rules ("prefer protocol over base class", "don't mock the DB") so later sprints don't repeat the mistakes of earlier ones.

**Business-goal divergence.** A sprint finishes technically (`done`) but the business goal fails — e.g. the event-tracker feature shipped but "the user-visible event system is slow and unstable". `/retro` records this explicitly (`goal: fail`), and `/learn` turns the root cause into a rule that blocks the same pattern next time.

**Small unblocker sprints.** 7-SP spikes — a test helper, a migration dry-run, a preflight check — that unblock larger work. Grooming them is fast; skipping grooming means they grow into 3-day rabbit holes.

**Cross-repo coordination.** One feature that spans `aurora-api` and `aurora-frontend`. booping keeps one sprint row per project; retros cross-reference each other. Parallel-session isolation (two terminals, two projects) is on the roadmap.

**Solo engineering with Claude Code.** A human driver + Claude handles planning and execution. Sub-agent delegation is the key lever: the orchestrator's context stays under control because worker agents handle the actual edits, and the human can review the diff without wading through intermediate chain-of-thought.

booping is not useful for one-shot scripts or throwaway prototypes. It earns its weight when you're on a codebase long enough to care about what shipped last month.
