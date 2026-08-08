# claude-booping — Glossary

Canonical names the spec set uses consistently — one term per line, never a synonym.

- **Project Vault** — the per-project directory holding all run artifacts (`plans/`, `retrospectives/`, `codereviews/`, `_lessons/`, `_playbooks/`, templates, `sprints.md`) — `~/Claude/{project}/` by default, or repo-local via the marker's `vault_path:` key
- **Core level** — the plugin repo itself: the shipped playbooks, agents, the `/playbook` skill, and `src/config.yaml` defaults
- **Global level** — the machine-wide tier: `<home_dir>/` (`_playbooks/`, `_lessons/`, templates) and `~/.config/booping/config.yaml`
- **Project level** — the tier scoped to one attached repo: the Project Vault and its `config.yaml`
- **Levels** — the discovery and config-merge ladder, always named "the core, global and project levels"; later levels win on merge, names are unique across levels on discovery
- **Playbook** — a multi-step guided procedure: a directory with `playbook.md`, an optional `playbook.yaml` (`graph:` + state machines), and one directory per step
- **Step** — one unit of a playbook's graph: a directory holding `prompt.md`, optionally per-model bodies and an eval suite
- **Subgraph** — a mapping node in `graph:`: its own dependencies, an inner graph of steps, an optional prose `repeat:`, one nesting level only
- **Inline** — a delegation level: the runner performs the step itself in the driving context
- **Assisted** — a delegation level: the runner performs the step but hands heavy reads to the config-named research agent for a bounded return
- **Detached** — a delegation level: the step runs in its own sub-agent, declared by the step's `detached:` field
- **Plan** — a groomed sprint's document and run artifact, `plans/{slug}/index.md` in the Project Vault
- **Retrospective artifact** — the standalone `retrospectives/{slug}.md` the retro track advances, linked back from the covered plan's `retro:` key
- **Targeted lesson** — a markdown note injected into exactly the playbooks, steps, agents, or skills its `targets:` list names; an untargeted one injects nowhere
- **Marker** — the repo's `.booping` file attaching it to a Project Vault: `project_name:`, optional `vault_path:`, and the `latest_migration:` watermark
- **Migration watermark** — the marker's `latest_migration:` key, the highest shipped migration id a Project Vault has applied
- **Run artifact** — the frontmatter-carrying file a state machine advances: a plan's `index.md`, a retrospective artifact, a code review
- **Cancelled** — a terminal run outcome, reachable from any non-terminal status of an active run and carrying its own exit hooks
- **Query spec** — a config-declared mapping at any dotted path describing a frontmatter query over a markdown directory
- **Scaffold tree** — a config-declared file tree `booping scaffold` materialises at a destination
- **Spec set** — the `docs/_specs/` files this documentation effort maintains: briefing, feature index, glossary, roles, targets
