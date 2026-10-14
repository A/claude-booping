---
type: adr
title: Core is a playbook framework; domain behaviour lives in playbooks
summary: The booping CLI offers generic primitives — render, query, scaffold, frontmatter, state machines; plan-specific behaviour such as sprints.md lives in playbooks and their scripts.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
values: [values/0001#stack-agnostic-core, values/0001#single-source, values/0001#everything-in-one-place]
sources: [playbooks/groom/_specs/DECISIONS.md, vault/researches/20260802-01-31_framework-cli-extraction-research.md, CHANGELOG.md, CLAUDE.md]
---

## Context

The CLI carried a plan domain: a plan-only `transition` command beside
`playbook-transition`, `render-sprints` producing `sprints.md`, `vault-commit`, and
hardcoded loaders for plans, retros and templates in the context. The groom port
first put `sprints.md` out of scope, then moved its rendering into a playbook-local
script, with the direction "playbook-specific behavior lives in playbooks; booping
core stays a pure playbook framework". The framework research found the five
generic capabilities (rendering, frontmatter updates, state machines, layered
config, listing) mostly present, the playbook engine already plan-free, and the real
work to be evicting the plan domain and merging the two transition dispatchers. It
also found that without framework support the eviction produced duplication: the
groom scripts re-implemented sprints rendering and vault commits.

## Decision

Core is a framework for playbooks over markdown with frontmatter: `render`,
`render-playbook`, `playbook-state`, `playbook-transition`, `query`, `scaffold`,
`frontmatter-update`, `config-get`, `marker-set` and config-declared macros. Plan
behaviour lives in the playbooks and their `_scripts/` hooks. `render-sprints` is
gone: `sprints.md` is seeded once at setup as an Obsidian Bases view and written by
nothing, and `booping query --config core.plans` is its machine-readable
equivalent. Listing is a generic query over config-declared specs, not a loader
per domain type.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [Generic framework core](#generic-framework-core) | accepted | high | low | One mechanism serves every playbook |
| [Plan domain in core](#plan-domain-in-core) | rejected | medium | medium | Two dispatchers; hardcoded plan types |
| [Sprints report left to the user](#sprints-report-left-to-the-user) | rejected | low | high | First groom answer; revised within the hour |

### Generic framework core

The CLI knows frontmatter, templates, queries, trees and state machines, never
plans.

- **Pros:** user playbooks get the same primitives as core ones; one transition
  dispatcher; the plan shape is config, so plan-as-directory changed a glob, not a
  loader.
- **Cons:** playbooks carry scripts for their side effects; a large migration of the
  plan lifecycle out of core.
- **Complexity:** high.
- **Reversibility:** low.

### Plan domain in core

Plans, retros and their lifecycle stay first-class in the CLI.

- **Pros:** no scripts for plan side effects.
- **Cons:** duplicated transition dispatchers and interpolation code; hardcoded plan
  types; playbook machines could not reach the plan hooks and re-implemented them.
- **Complexity:** medium.
- **Reversibility:** medium.

### Sprints report left to the user

`sprints.md` is out of booping's scope; the user scripts it or a later published
command handles it.

- **Pros:** nothing to maintain.
- **Cons:** not named in the source; the decision was revised to keep it in scope.
- **Complexity:** low.
- **Reversibility:** high.

## Consequences

- Plan, retro and code-review lifecycles are playbook `states:` blocks, not core
  config.
- Scripts shared by several playbooks live in `playbooks/_scripts/`, resolved
  playbook-local first.
- [clarify] Whether the framework CLI is published as a package separate from the
  plugin was an open question in the research; it still ships inside the plugin.
