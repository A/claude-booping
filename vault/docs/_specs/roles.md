---
reviewed_at: 2026-08-08 18:24
---

# claude-booping — Documentation roles

## Users

- **Who** — an experienced developer or tech lead who installed booping and runs the groom → develop → retro → learn loop on their own repo via `/playbook`.
- **Comes for** — installation and setup, the quick-start loop, what each playbook does to their repo and asks of them, per-playbook status vocabularies, the sprint/SP model, and where vault artifacts land.
- **Depth** — commands, playbook names, status names, vault paths, and the shape of a plan. Never internals: no template pipeline, no Jinja rendering, no Python module names, no state-machine YAML.
- **Tone** — second person, imperative, worked examples over description; one happy path first, variations after.
- **Withhold** — build-time architecture, config-merge mechanics beyond "put a `config.yaml` in your vault", eval and snapshot infrastructure, unreleased behaviour.
- **Reads** — README, docs site (Home, Quick start, Install, Vault, the Workflow pages), GitHub release notes.

## Advanced users

- **Who** — a user shaping booping to a specific codebase: tuning config, authoring templates and lessons, writing their own playbooks, wiring in external agents.
- **Comes for** — the three-tier config merge and per-project `config.yaml` keys, plan and review templates, targeted lessons, playbook authoring (graphs, states, hooks), and external-agent integration.
- **Depth** — every user-facing config key, the full playbook manifest surface (`playbook.yaml`, step prompts, `detached:`, lesson targets), query specs and scaffold trees as consumable features. Never plugin internals: no build pipeline, no `src/files/` templates, no Python source layout, no CI gates.
- **Tone** — second person, reference-style; key tables and manifest shapes over narrative, one minimal example per mechanism.
- **Withhold** — how the render pipeline is implemented, snapshot/eval harness internals, undocumented config keys the core reserves for itself.
- **Reads** — docs site (Project config, Playbooks, Integrating external agents, Vault), the `playbook-authoring` playbook, template files in their own vault.

## Contributors

- **Who** — someone changing the plugin itself: editing templates, playbooks, the `booping` CLI, or the testing infrastructure, and sending PRs.
- **Comes for** — the build/render pipelines, `src/config.yaml` semantics, playbook runtime mechanics (graphs, states, hooks, lessons), the snapshot and eval workflows, and the CI gates a change must pass.
- **Depth** — full internals, down to module and template names, with pointers to source over restated literals; the schema is the truth and prose only orients. Never duplicated reference: no prose copies of config values, status sets, or agent ids that the source already declares.
- **Tone** — terse, declarative, repo-relative paths; assumes the repo is checked out and `just` is on hand.
- **Withhold** — speculative roadmap and unconverged design directions; only shipped mechanics and the current consolidation work are documented.
- **Reads** — repo `CLAUDE.md`, `documentation/playbook.md` and `documentation/project_config.md`, plugin-internal `docs/` fragments, `src/config.yaml` comments, `justfile`, `bin/booping --help`, PR and commit history.
