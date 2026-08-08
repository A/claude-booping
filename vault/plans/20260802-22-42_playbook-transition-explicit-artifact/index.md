---
status: cancelled
title: Explicit artifact target for playbook-transition
type: feature
created: 2026-08-02 22:42
summary: "Positional artifact argument for booping playbook-transition, addressing
  the run's state file directly instead of workdir + declared path"
agents: {}
plan_status: in-spec
sessions:
- 494e626e-fcb1-4068-bfed-7b5b82f39417
metrics_active_minutes: 47
metrics_models:
- claude-opus-5
metrics_tokens_input: 13130
metrics_tokens_output: 161610
metrics_tokens_cache_creation: 1310019
metrics_tokens_cache_read: 14991261
---

# Explicit artifact target for `playbook-transition`

## Framing

See [request](request.md) for the full framing brief.

### Request

> groom 1. use positional argument to set file. 2. It should work for cases like develop/groom/retro which all keep state on one index.md plan file. 3. Exmpicit

### Restated problem

`booping playbook-transition` resolves the file it mutates as `workdir / machine.artifact`, with `{instance}` interpolated first — the target is always addressed indirectly, through the machine's declared relative path plus a directory. For `develop`, `groom` and `retro`, all of which keep run state on a single `index.md` that is the plan file itself, the caller already knows the file and has to decompose it into a directory plus a manifest-declared leaf. Where the indirection blocks work outright is a move against a file the machine's path does not describe: retro's dropped sibling plans sit outside the run workdir, so they can only move via `booping transition done <plan>`, leaving one run with two state writers. The change: take the artifact file as an explicit positional argument.

### Task type

`feature` — a new CLI argument and a new artifact-resolution path. Not `bug` (nothing diverges from specified behaviour), not `refactoring` (the command's public contract changes).
