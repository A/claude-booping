---
type: reference
title: Audience
summary: Booping is read by three roles — users, advanced users and contributors — each coming for different things at a different depth, in a different voice.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-15
status: live
sources: [https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/roles.md, https://github.com/A/claude-booping/blob/c7e43b43dfe5fc1c0fafe253dd148d7e62ea231e/vault/docs/_specs/index.md]
---

## Facts

- Every role is a technical professional; people without a technical background are
  not the audience ([value/0014 — Comfort for non-technical users](../value/0014-comfort-for-non-technical-users.md)).
- **User** — an experienced developer or tech lead who installed booping and runs the
  groom → develop → retro → learn loop on their own repo via `/playbook`. Comes for
  installation and setup, the quick-start loop, what each playbook does to their repo
  and asks of them, per-playbook status vocabularies, the sprint/SP model and where
  vault artefacts land.
- User depth: commands, playbook names, status names, vault paths and the shape of a
  plan; never internals (template pipeline, Jinja rendering, Python modules,
  state-machine YAML). Withheld: build-time architecture, config-merge mechanics beyond
  "put a `config.yaml` in your vault", eval and snapshot infrastructure, unreleased
  behaviour. Voice: second person, imperative, worked examples over description, one
  happy path first and variations after. Reads the README, the docs site and release
  notes.
- **Advanced user** — a user shaping booping to a specific codebase: tuning config,
  authoring templates and rules, writing their own playbooks, wiring in external
  agents. Comes for the three-level config merge and per-project config keys, plan and
  review templates, targeted rules, playbook authoring (graphs, states, hooks) and
  external-agent integration.
- Advanced-user depth: every user-facing config key, the full playbook manifest
  surface, query specs and template trees as features; never plugin internals (build
  pipeline, Python source layout, CI gates). Withheld: how the render pipeline is
  implemented, snapshot and eval harness internals, config keys the core reserves for
  itself. Voice: second person, reference style, key tables and manifest shapes over
  narrative, one minimal example per mechanism. Reads the docs site, the
  `playbook-authoring` playbook and the template files in their own vault.
- **Contributor** — someone changing the plugin itself: templates, playbooks, the
  `booping` CLI or the testing infrastructure, sending PRs. Comes for the render
  pipeline, `src/config.yaml` semantics, playbook runtime mechanics, the snapshot and
  eval workflows and the CI gates a change must pass.
- Contributor depth: full internals down to module and template names, with pointers
  to the source over restated literals — the schema is the truth and prose only
  orients. Withheld: speculative roadmap and unconverged design directions. Voice:
  terse, declarative, repo-relative paths, assumes a checkout and `just`. Reads the
  repo `CLAUDE.md`, `documentation/`, the `docs/` fragments, `src/config.yaml`
  comments, the `justfile`, `bin/booping --help` and PR and commit history.
