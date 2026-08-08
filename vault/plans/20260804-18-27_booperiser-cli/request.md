# Framing brief — Booperiser CLI

## Request

> groom let's make a new cli that later replace booping. Name it booperiser. And there we need to add 3 features first: 1. project/vault resolution, 2. config merge (core global project), ideally if merged config be just proxied into the jinja, we prefer simple implementation now, 3. basic jinja render. The new cli should cover only playbooks

## Task type

`feature`

- Not `bug` — nothing diverges from expected behavior; there is no defect, reproduction, or regression to fix. The existing `booping` CLI works.
- Not `refactoring` — the test for refactoring is "no user-visible behavior change". This adds a new executable with its own command surface that users invoke directly, so behavior changes visibly even if the eventual goal is replacement of an existing tool.
- `feature` — new capability with its own surface, needing design, milestones, and DoD.

## Problem

Today all runtime work goes through one CLI, `bin/booping` (uv project at `booping-python/`), whose scope has grown to cover the whole plugin: plan lifecycle transitions, sprints rendering, frontmatter mutation, vault commits, build-time file rendering, scaffolding, debug dumps, and playbooks. `Context.assemble()` loads plans, lessons, templates, playbooks, and config together, so even a playbook render pays for the whole vault model.

The target is a second CLI, `booperiser`, that will eventually replace `booping` but starts narrow: **playbooks only**. Its first three capabilities are the foundation everything else sits on:

1. **Project/vault resolution** — find the repo, the `.booping` marker, and the resolved vault path (default `<home_dir>/{project}/`, or the marker's `vault_path:`).
2. **Config merge** — deep-merge core → global → project config, with the merged mapping proxied into Jinja as-is rather than modelled into typed objects. Simple implementation preferred at this stage.
3. **Basic Jinja render** — render a template with that config in scope.

Everything else `booping` does (transitions, sprints, build, scaffold, frontmatter, vault-commit) stays out of `booperiser` for now.

## Clarifications and Decisions

- Runtime: Python, **new uv project** (`booperiser-python/`) beside `booping-python/` — same toolchain, clean-slate module tree.
- Command surface: **one command, `render`**, with a polymorphic target — not booping's `render` / `render-playbook` split. Two commands would duplicate the argument surface, the `--set` implementation and the context-assembly path for what is one operation.
- Scope of **this** plan: **config merge + render only**. Playbook rendering is deferred to the next plan.
- Playbook rendering **pilots on one playbook**, not all seven. `setup` is the pick — 2 steps, no states, no subgraph, no core-partial dependencies.
- Coexistence: **parallel and independent** — `booping` is untouched, no shared code imported from `booping-python`, booperiser is proven on its own.
- Config in Jinja: **raw merged dict, no typing** — the merged mapping is injected as `config` with plain dict access; no dataclasses, no validation, no schema layer.
- Out of scope: transitions, sprints rendering, frontmatter mutation, vault commits, build, scaffold, debug dumps, plan/lesson/template loading.
