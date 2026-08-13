---
id: "04"
title: "Mirror hooks on groom transitions"
sp: 3
status: pending
plan: "plans/202608132333_task-tracker-driver-linear/index.md"
---

# M04: Mirror hooks on groom transitions

Every groom transition mirrors the new status onto the tracker issue, and a transition can post a vault file as a comment — both without ever being able to fail the transition itself.

**Scope**: new `playbooks/_scripts/tracker-sync` and `playbooks/_scripts/tracker-comment`, `playbooks/groom/playbook.yaml` (hook lists on existing transitions), `booping-python/e2e/cases/playbook-transition/`. Shared `_scripts/`, not groom's own directory, because develop and the retro track will reuse them. The `awaiting-clarification` edges those hooks also serve are M05's.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 4.1 | Write `tracker-sync`: an executable shell script that runs `bin/booping-tracker sync --artifact "$BOOPING_ARTIFACT" --playbook groom`, **absorbs the tracker's exit code** — echoing `warning: tracker sync failed (exit N)` to stderr and exiting 0 — because a non-zero hook aborts `playbook-transition` after `status:` is already on disk. Resolves the binary as `"${BOOPING_TRACKER_BIN:-$(cd "$(dirname "$0")/../.." && pwd)/bin/booping-tracker}"` — the script lives two levels below the repo root at `playbooks/_scripts/`, and cwd is the plan directory, so the path must be derived from the script's own location and never from cwd. | `playbooks/_scripts/tracker-sync` | 1 | pending |
| 4.2 | Write `tracker-comment`: takes one workdir-relative file path as its argument, runs `bin/booping-tracker comment --issue {tracker_request or tracker_issue} --body-file {path}` against the ref read from the artifact's frontmatter, skips silently at exit 0 when the file is absent or the ref is null, and absorbs the tracker's exit code the same way. | `playbooks/_scripts/tracker-comment` | 1 | pending |
| 4.3 | Wire `script tracker-sync` onto every transition in groom's `run` machine — including the two `cancelled` edges on the superstates — appending it to existing hook lists rather than replacing them, and keeping it last so the vault-side hooks (`stamp-session`, `commit-plan`, `frontmatter-update`) run first. | `playbooks/groom/playbook.yaml` | 1 | pending |

Tests: the corpus covers the hook contract at the `playbook-transition` boundary — a transition whose hook runs the `cli` provider (receipt, exit 0), and a transition whose tracker stub exits non-zero (warning on stderr, transition still reported, exit 0) — using an executable fixture script per the existing hook cases.

## Definition of Done

### Task 4.1

- [ ] The script is executable (`chmod +x`) and runs with cwd set to the plan directory, as `playbook-transition` invokes it.
- [ ] A tracker exit of 1 or 2 produces `warning:` on stderr and exit 0; the transition report still prints `script tracker-sync: ok`.
- [ ] Under `core.tracker.driver: cli` the script exits 0 having performed no tracker write.
- [ ] `BOOPING_TRACKER_BIN` overrides the resolved binary path, and with it unset the script still finds the binary when cwd is the plan directory inside the vault.

### Task 4.2

- [ ] Passing a path that does not exist exits 0 and writes nothing.
- [ ] An artifact whose tracker refs are null exits 0 and writes nothing.
- [ ] The comment targets `tracker_request` when set, falling back to `tracker_issue`.

### Task 4.3

- [ ] Every transition in `playbooks/groom/playbook.yaml` — including both superstate `cancelled` edges — carries `script tracker-sync` as its last hook.
- [ ] Hooks that already existed on those transitions are unchanged and still run first.
- [ ] `bin/booping playbook-state groom --workdir {plan-dir}` still reports the same frontier as before the change.
- [ ] The rule is stated where the next milestone will read it: every transition added to groom later — M05's clarification edges included — carries `script tracker-sync` as its last hook.

## Verify

```
just e2e -k playbook-transition
bin/booping playbook-transition groom researching --workdir {a scratch plan dir seeded with core.tracker.driver=cli}
```

Expected: the corpus passes, including the two new hook cases; the manual transition prints `script tracker-sync: ok` with the `cli` no-op receipt and leaves the artifact's status advanced.
