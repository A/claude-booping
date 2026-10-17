---
type: adr
title: Config is a three-tier deep merge with no schema gate
summary: Config merges core, global and project tiers, later winning and lists replacing; any key loads in any tier, and playbook keys live in the core file under core.{name}_playbook.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-17
status: accepted
values: [value/0005, value/0003, value/0006]
sources: [CLAUDE.md, CHANGELOG.md, vault/researches/20260802-01-31_framework-cli-extraction-research.md]
---

## Context

Booping's structured data — query specs, scaffold trees, macros, sprint scale,
agents, task types — lives in config and is rendered from there. Users and projects
need to add and override it: the global tier carries `home_dir`, the project tier
carries agent registrations and settings such as the cross-review agent. Before
v1.0.0 an unrecognised key produced an unknown-key warning. The framework research
proposed a fourth tier between core and global — defaults shipped inside each
playbook directory — and noted that a playbook could not ship config defaults of its
own.

## Decision

Three tiers, deep-merged core → global → project: `src/config.yaml` ←
`${XDG_CONFIG_HOME:-~/.config}/booping/config.yaml` ← `{vault}/config.yaml`. Later
tiers win; lists replace wholesale. There is no schema gate and no tier restriction:
any key loads in any tier. The top level is `home_dir` plus `core`; a key one
playbook owns lives at `core.{name}_playbook`, a shared key directly under `core`,
and a user's own playbook namespace copies that shape. Any mapping can be a query
spec or a scaffold tree, declared beside its consumer, never in a central registry.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [Three tiers without a schema gate](#three-tiers-without-a-schema-gate) | accepted | low | medium | Any tier adds or overrides any key |
| [Schema gate with unknown-key warnings](#schema-gate-with-unknown-key-warnings) | rejected | medium | high | Dropped in v1.0.0; reason not named in the source |
| [A playbook-defaults tier](#a-playbook-defaults-tier) | rejected | medium | medium | Proposed in research; not adopted |

### Three tiers without a schema gate

Core, global and project config deep-merge with no validation of key names.

- **Pros:** a user or project tier extends any part of the config, including a
  user's own playbook namespace, without registering it anywhere.
- **Cons:** a misspelt key is silently ignored; a consumer that needs a closed set,
  such as the tracker driver name, has to reject unknown values itself.
- **Complexity:** low.
- **Reversibility:** medium.

### Schema gate with unknown-key warnings

The merge warns on a key the core schema does not declare.

- **Pros:** typos surface at load.
- **Cons:** a key booping does not know is not a typo by default — user code
  (playbooks, scripts, templates) reads its own keys, so a project's config extends
  booping's logic; a warning would flag every such key (owner, 2026-10-14).
- **Complexity:** medium.
- **Reversibility:** high.

### A playbook-defaults tier

Each playbook ships its own config defaults in its directory, merged between core
and global.

- **Pros:** a playbook owns its keys and their defaults; core config shrinks to
  framework keys.
- **Cons:** a fourth tier to resolve and document; not named further in the source.
- **Complexity:** medium.
- **Reversibility:** medium.

## Consequences

- Core playbooks' keys live in `src/config.yaml` under `core.{name}_playbook`.
- `core.tracker.driver` treats an unknown name as a hard error, because the merge
  has no schema gate to catch it.
- [clarify] Whether a playbook-defaults tier is rejected or only deferred is not
  named in the source.
