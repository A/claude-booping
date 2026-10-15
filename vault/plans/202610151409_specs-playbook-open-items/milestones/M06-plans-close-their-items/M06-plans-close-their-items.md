---
id: "06"
title: "Plans link, close and reopen their items"
sp: 4
status: pending
plan: "plans/202610151409_specs-playbook-open-items/index.md"
---

# M06: Plans link, close and reopen their items

A groom request naming `OI-NNNN` links those items to the plan; develop reaching `done` closes them, develop `fail`/`cancelled` and groom `cancelled` return them to `open`.

**Scope**: new shared hook `playbooks/_scripts/open-items-follow-plan`, POSIX sh shaped like `playbooks/_scripts/tracker-sync`: argument `done` → `bin/booping specs open-items close --plan {plan}`, `open` → `reopen --plan {plan}`, `{plan}` the vault-relative path of `$BOOPING_ARTIFACT`; binary resolved from the script's own location, overridable by `BOOPING_BIN` (as `BOOPING_TRACKER_BIN` is in tracker-sync); the CLI's exit code absorbed with a `warning: open-items follow-plan failed (exit N)` line on stderr, exit 0 always, and a header comment saying why (the tracker-sync reason). Hooks: `script open-items-follow-plan done` on develop's `in-progress → done`; `script open-items-follow-plan open` on develop's `→ fail` and the `cancellable` superstate's `→ cancelled`, and on both of groom's `→ cancelled` superstate edges. groom intake (`playbooks/groom/intake/fable-5.md`): one bullet under the plan-directory section — a request naming open items (`OI-NNNN`) links each to the new plan with `booping specs open-items plan {ids} --plan {plan-dir}/index.md` once the directory exists.

Tests: integration tier, txtar cases with a fixture user playbook whose edge carries the hook — an edge with `done` closes the plan's planned item; `open` reopens it; with `BOOPING_BIN` pointing at a command that exits 1, the transition still succeeds and stderr carries the warning.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 6.1 | The hook script and its three cases. | `playbooks/_scripts/open-items-follow-plan`, `booping-python/e2e/cases/playbook-transition/open-items-follow-plan-*.txtar` | 2 | pending |
| 6.2 | Hooks on develop's and groom's edges. | `playbooks/develop/playbook.yaml`, `playbooks/groom/playbook.yaml` | 1 | pending |
| 6.3 | The groom intake bullet. | `playbooks/groom/intake/fable-5.md` | 1 | pending |

## Definition of Done

### Task 6.1

- [ ] The script is executable and exits 0 on every path.
- [ ] Three cases, one per behaviour named in Tests.

### Task 6.2

- [ ] Exactly the five edges named in Scope carry the hook; no other edge changed.

### Task 6.3

- [ ] One bullet, the command rendered as written in Scope; no restated machine statuses.

Return: the list of changed files, nothing else.

## References

- `playbooks/_scripts/tracker-sync` — the absorb-and-warn hook shape and its header comment.
- `booping-python/e2e/cases/playbook-transition/a-failing-script-hook-relays-its-stderr.txtar` — a script-hook case with a fixture playbook.

## Verify

`just e2e -k "open-items-follow-plan"`
