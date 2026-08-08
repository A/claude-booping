---
reviewed_at: 2026-08-08 15:16
---

# claude-booping — Briefing

## What it is

booping is a Claude Code plugin that runs a self-learning, project-scoped sprint workflow: a feature idea moves through the **groom → develop → retro → learn** loop, with a side-route **code-review** pass over a finished plan's diff. One shipped skill (`/playbook`) drives everything; every procedure is a **playbook** — a directory of step prompts plus a `playbook.yaml` declaring a step graph and per-track state machines, advanced only by the `booping playbook-transition` CLI. The plugin ships eight core playbooks (`groom`, `develop`, `code-review`, `retro`, `learn`, `setup`, `migrate`, `playbook-authoring`) and discovers user-authored ones beside them from global and per-project roots.

Run artifacts live in a per-project **vault** — `~/Claude/{project}/` by default, or a repo-local directory via the `.booping` marker — as plain, Obsidian-ready markdown with YAML frontmatter: `plans/` (one directory per sprint), `retrospectives/`, `codereviews/`, targeted `_lessons/`, user `_playbooks/`, plan and review templates. The plan track ends when develop closes a plan at `done`; retro and learn then run as a second track over a standalone `retrospectives/{slug}.md` artifact, linked back by the plan's `retro:` key. The tracks join through plan frontmatter (`retro:`, `code_reviews:`), never a shared status vocabulary. The repo itself is a uv Python project (`booping` CLI) plus Jinja template pipelines that render skills, agents and playbook bodies with full project context; a MkDocs site under `documentation/` is the public reference.

## Who it serves

- **Users** — experienced developers and tech leads running iterative, agile-style work on their own repos; they come for installation and setup, the quick-start loop, per-playbook command reference, status vocabularies, and the sprint/SP model.
- **Advanced users** — users shaping booping to a codebase; they come for the three-tier config merge, per-project `config.yaml` keys, plan and review templates, targeted lessons, authoring their own playbooks, and wiring in external agents.
- **Contributors** — people changing the plugin itself; they come for the build/render pipelines, `src/config.yaml` semantics, playbook mechanics (graphs, states, hooks, lessons), snapshot and eval workflows, and the CI gates.

## Where it is heading

The project has just converged on its v1.0 shape — everything procedural is a playbook, driven by one skill over a declarative graph-and-states runtime, with the plan, retro and code-review tracks split into independent state machines joined only by plan frontmatter, and the whole surface held by testing infrastructure (committed render snapshots, mdcheck structural gates, promptfoo eval suites). The near-term work is consolidation on top of that foundation: bringing the public documentation current with the playbook framework delivered on PR #19, and incremental runtime instrumentation such as session active-time metrics.
