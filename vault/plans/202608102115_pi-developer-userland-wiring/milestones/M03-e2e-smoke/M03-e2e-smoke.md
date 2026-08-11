---
id: "03"
title: "End-to-end smoke through the proxy path"
sp: 2
status: pending
plan: "vault/plans/202608102115_pi-developer-userland-wiring/index.md"
---

# M03: End-to-end smoke through the proxy path

**Goal**: one recorded end-to-end run proving the chain — composed prompt → `~/.bin/pi-developer` → Qwen3-Coder-Next → repo edit + commit → validation — works and that validation catches a shortfall.

**Scope**: a throwaway scratch git repo under the session scratchpad (or `mktemp -d`); reads `~/.claude/agents/pi-developer.md` and the plugin repo. Writes nothing outside the scratch dir; the receipt lands in this milestone's report. `Commit: none (scratch repo discarded)` — no plan-repo commit is expected beyond the scratch repo's own.

**Tests**: the smoke run itself is the test — happy path plus one seeded-shortfall path exercising the retry branch.

## Tasks

| Task | Description | Files | SP | Status |
|------|-------------|-------|----|--------|
| 3.1 | Happy path: init a scratch repo with a trivial file and a fake milestone contract in the real milestone-file shape — seed it with `cd /home/anton/Dev/@A/claude-booping && bin/booping scaffold core.groom_playbook.milestone_scaffold {scratch}/milestones --set id=01 --set slug=smoke --set title="Smoke" --set sp=1 --set plan={scratch}/index.md`, then fill Tasks/DoD/Verify by hand (small edit, a `## Verify` shell command, DoD checkboxes). Compose the prompt exactly as the rewritten agent body prescribes (rendered developer body + paths block) and run `~/.bin/pi-developer -f {prompt} -m Qwen3-Coder-Next -C {scratch}`. Assert: the contracted file changed, `## Verify` passes, a commit exists with the contract's message format, stdout report parses as the milestone block. | scratch dir only | 1 | pending |
| 3.2 | Shortfall path: repeat with a contract whose DoD names a file the prompt withholds (or a Verify that must fail), confirm validation flags the gap, then exercise one `--continue` corrective re-run and confirm the retry either closes the gap or the failure is reported honestly in the milestone format. | scratch dir only | 1 | pending |

## Definition of Done

### Task 3.1

- [ ] The pi worker edited only the contracted file, got Verify green, and committed in the scratch repo.
- [ ] The captured stdout report contains the `Files touched:` / `Verify:` / `Commit:` lines the runner parses.

### Task 3.2

- [ ] The validation step detected the seeded gap before any retry.
- [ ] Exactly one `--continue` re-run was issued; its outcome (fixed or still-failing) is stated in the report.

## Verify

- Both run receipts (commands + trimmed stdout + `git log --oneline` of the scratch repo) included in the milestone report; scratch dir removed afterwards.
