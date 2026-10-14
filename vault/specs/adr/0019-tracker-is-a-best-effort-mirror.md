---
type: adr
title: The task tracker is a best-effort mirror of the vault
summary: The vault stays authoritative; tracker hooks run in a separate CLI, absorb the tracker's failures with a warning, and booping-tracker sync reconciles by hand.
created_by: claude
created_at: 2026-10-14
updated_at: 2026-10-14
status: accepted
values: [values/0001#everything-in-one-place, values/0001#plans-run-to-the-end]
sources: [CHANGELOG.md, CLAUDE.md]
---

## Context

Groom mirrors a plan's status and its clarification questions onto an issue
tracker through `script` hooks on its transitions. `playbook-transition` writes
`status:` before it runs the hooks, so a hook that fails aborts the transition
with the vault already advanced and the tracker behind. Tracker providers need an
HTTP client and per-provider code.

## Decision

Every tracker interaction lives in a second CLI, `bin/booping-tracker`, a separate
uv project that keeps tracker concerns and `httpx` out of `booping-python`; it
reads its config by shelling to `booping config-get core.tracker`. The hooks
`tracker-sync` and `tracker-comment` absorb the tracker's exit code and warn on
stderr, so an unreachable tracker never fails a transition. The vault is
authoritative; `booping-tracker sync --artifact …` by hand is the reconcile. One
driver ships, `cli`, a receipts-only no-op; an unknown driver name is a hard error.

## Alternatives

| Option | Status | Complexity | Reversibility | Verdict |
|---|---|---|---|---|
| [Hooks absorb tracker failures](#hooks-absorb-tracker-failures) | accepted | low | high | The run never stalls on the tracker |
| [A tracker failure fails the transition](#a-tracker-failure-fails-the-transition) | rejected | low | high | Vault advanced, transition aborted |
| [Tracker code inside booping-python](#tracker-code-inside-booping-python) | rejected | low | medium | Pulls tracker concerns and httpx into the core CLI |

### Hooks absorb tracker failures

The hook reports and warns; the transition stands.

- **Pros:** the run continues whatever the tracker does; the vault is the single
  truth.
- **Cons:** the tracker can lag until someone re-runs `sync`.
- **Complexity:** low.
- **Reversibility:** high.

### A tracker failure fails the transition

The hook's exit code propagates.

- **Pros:** a failure is impossible to miss.
- **Cons:** status is written before hooks, so the transition aborts with the vault
  advanced and the tracker behind.
- **Complexity:** low.
- **Reversibility:** high.

### Tracker code inside booping-python

Providers live in the core CLI.

- **Pros:** one CLI.
- **Cons:** tracker concerns and an HTTP dependency in the framework.
- **Complexity:** low.
- **Reversibility:** medium.

## Consequences

- With no tracker configured, groom behaves as before; the `cli` driver prints a
  receipt and nothing more.
- A real provider is another module behind the same facade, with its token named by
  `api_key_env`, never carried in config.
